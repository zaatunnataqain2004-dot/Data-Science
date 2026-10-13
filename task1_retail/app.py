from pathlib import Path
import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Retail Sales Insights", page_icon="🛍️", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA = BASE_DIR / "data" / "retail_sales_demo.csv"

st.title("🛍️ Retail Sales Data Analysis & Business Insights")
st.caption("Explore sales, profit, product performance, customer behavior, and regional trends.")

with st.sidebar:
    st.header("Data source")
    uploaded_file = st.file_uploader("Upload a retail CSV file", type=["csv"])
    st.caption("No file uploaded? The included demo dataset loads automatically.")
    st.divider()
    st.header("Dashboard filters")

@st.cache_data
def read_csv(file_bytes=None, local_path=None):
    if file_bytes is not None:
        return pd.read_csv(io.BytesIO(file_bytes))
    return pd.read_csv(local_path)

try:
    raw_df = read_csv(uploaded_file.getvalue() if uploaded_file else None,
                      None if uploaded_file else str(DEFAULT_DATA))
except Exception as exc:
    st.error(f"Could not read the CSV file: {exc}")
    st.stop()

# Normalize column names for common Superstore-style datasets.
def normalize_columns(frame):
    frame = frame.copy()
    frame.columns = [str(c).strip() for c in frame.columns]
    aliases = {
        "order date": "Order Date", "date": "Order Date",
        "sales": "Sales", "revenue": "Sales",
        "profit": "Profit", "quantity": "Quantity",
        "region": "Region", "category": "Category",
        "sub-category": "Sub-Category", "subcategory": "Sub-Category",
        "product name": "Product Name", "product": "Product Name",
        "customer id": "Customer ID", "customer name": "Customer Name",
        "segment": "Segment", "discount": "Discount",
        "order id": "Order ID"
    }
    mapping = {}
    for col in frame.columns:
        key = col.lower().strip()
        if key in aliases:
            mapping[col] = aliases[key]
    return frame.rename(columns=mapping)

df = normalize_columns(raw_df)
required = ["Sales"]
missing_required = [c for c in required if c not in df.columns]
if missing_required:
    st.error("Your CSV must contain a Sales or Revenue column. Please use a retail sales dataset.")
    st.write("Columns found:", list(df.columns))
    st.stop()

# Add optional columns so dashboard works with smaller datasets too.
defaults = {
    "Profit": 0, "Quantity": 1, "Order Date": pd.NaT,
    "Region": "Unknown", "Category": "Uncategorized",
    "Sub-Category": "Unknown", "Product Name": "Unknown Product",
    "Customer ID": None, "Customer Name": None, "Segment": "Unknown",
    "Discount": 0, "Order ID": None
}
for col, value in defaults.items():
    if col not in df.columns:
        df[col] = value

rows_before = len(df)
duplicates_removed = int(df.duplicated().sum())
df = df.drop_duplicates().copy()

for col in ["Sales", "Profit", "Quantity", "Discount"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")
for col in ["Sales", "Profit", "Quantity", "Discount"]:
    df[col] = df[col].fillna(df[col].median() if df[col].notna().any() else 0)

df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
for col in ["Region", "Category", "Sub-Category", "Product Name", "Segment"]:
    df[col] = df[col].astype("string").str.strip().replace("", pd.NA).fillna("Unknown")
for col in ["Customer ID", "Customer Name", "Order ID"]:
    df[col] = df[col].astype("string").str.strip().replace("", pd.NA)

if df.empty:
    st.warning("The dataset has no rows after cleaning.")
    st.stop()

# Sidebar filters.
with st.sidebar:
    categories = sorted(df["Category"].dropna().unique().tolist())
    selected_categories = st.multiselect("Category", categories, default=categories)
    regions = sorted(df["Region"].dropna().unique().tolist())
    selected_regions = st.multiselect("Region", regions, default=regions)
    segments = sorted(df["Segment"].dropna().unique().tolist())
    selected_segments = st.multiselect("Customer segment", segments, default=segments)

    valid_dates = df["Order Date"].dropna()
    if not valid_dates.empty:
        min_date = valid_dates.min().date()
        max_date = valid_dates.max().date()
        date_range = st.date_input("Order date range", value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)
    else:
        date_range = None

filtered = df[
    df["Category"].isin(selected_categories)
    & df["Region"].isin(selected_regions)
    & df["Segment"].isin(selected_segments)
].copy()

if date_range and isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["Order Date"].isna()
        | ((filtered["Order Date"].dt.date >= start_date) &
           (filtered["Order Date"].dt.date <= end_date))
    ]

if filtered.empty:
    st.warning("No rows match the selected filters. Change your filters in the sidebar.")
    st.stop()

total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
total_quantity = filtered["Quantity"].sum()
orders = filtered["Order ID"].nunique() if filtered["Order ID"].notna().any() else len(filtered)
customers = filtered["Customer ID"].nunique() if filtered["Customer ID"].notna().any() else filtered["Customer Name"].nunique()
profit_margin = (total_profit / total_sales * 100) if total_sales else 0
avg_order_value = total_sales / orders if orders else 0

st.subheader("Business performance overview")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total sales", f"${total_sales:,.2f}")
k2.metric("Total profit", f"${total_profit:,.2f}")
k3.metric("Units sold", f"{total_quantity:,.0f}")
k4.metric("Orders", f"{orders:,.0f}")
k5.metric("Profit margin", f"{profit_margin:.1f}%")
st.caption(f"Average order value: ${avg_order_value:,.2f}  ·  Customers: {customers:,}  ·  "
           f"Removed exact duplicate rows: {duplicates_removed:,}  ·  Rows loaded: {rows_before:,}")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales overview", "📦 Products & categories", "🌎 Regions & customers", "🧹 Data quality"])

with tab1:
    left, right = st.columns(2)
    with left:
        dated = filtered.dropna(subset=["Order Date"]).copy()
        if not dated.empty:
            dated["Month"] = dated["Order Date"].dt.to_period("M").dt.to_timestamp()
            monthly = dated.groupby("Month", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
            fig = px.line(monthly, x="Month", y="Sales", markers=True, title="Monthly sales trend")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No valid order dates are available for a sales trend.")
    with right:
        region_sales = filtered.groupby("Region", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
        fig = px.bar(region_sales, x="Region", y="Sales", color="Region", title="Sales by region")
        st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)
    with left:
        fig = px.scatter(filtered, x="Sales", y="Profit", color="Category",
                         size="Quantity", hover_data=["Product Name", "Region"],
                         title="Sales vs. profit")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        corr = filtered[["Sales", "Profit", "Quantity", "Discount"]].corr(numeric_only=True)
        fig = px.imshow(corr, text_auto=".2f", aspect="auto", title="Numeric correlation heatmap",
                        color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    left, right = st.columns(2)
    with left:
        cat = filtered.groupby("Category", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        fig = px.bar(cat.sort_values("Sales", ascending=False), x="Category", y="Sales",
                     color="Category", title="Sales by category")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        sub = filtered.groupby("Sub-Category", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        fig = px.bar(sub.sort_values("Profit"), x="Profit", y="Sub-Category", orientation="h",
                     color="Profit", title="Profit by sub-category")
        st.plotly_chart(fig, use_container_width=True)

    product_table = filtered.groupby("Product Name", as_index=False).agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"))
    st.markdown("#### Top products by sales")
    st.dataframe(product_table.sort_values("Sales", ascending=False).head(10),
                 use_container_width=True, hide_index=True)

with tab3:
    left, right = st.columns(2)
    with left:
        segment = filtered.groupby("Segment", as_index=False).agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        fig = px.bar(segment, x="Segment", y="Sales", color="Segment", title="Sales by customer segment")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        if filtered["Customer Name"].notna().any():
            customer_col = "Customer Name"
        elif filtered["Customer ID"].notna().any():
            customer_col = "Customer ID"
        else:
            customer_col = None
        if customer_col:
            top_customers = filtered.groupby(customer_col, as_index=False).agg(
                Sales=("Sales", "sum"), Profit=("Profit", "sum"))
            top_customers = top_customers.sort_values("Sales", ascending=False).head(10)
            fig = px.bar(top_customers.sort_values("Sales"), x="Sales", y=customer_col,
                         orientation="h", title="Top 10 customers by sales")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Customer identifiers are not present in this dataset.")
    st.markdown("#### Regional performance table")
    st.dataframe(filtered.groupby("Region", as_index=False).agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum")
    ).sort_values("Sales", ascending=False), use_container_width=True, hide_index=True)

with tab4:
    st.markdown("#### Cleaning summary")
    quality = pd.DataFrame({
        "Check": ["Rows loaded", "Exact duplicate rows removed", "Rows after duplicate removal",
                  "Missing values remaining (all columns)", "Invalid order dates"],
        "Result": [rows_before, duplicates_removed, len(df), int(df.isna().sum().sum()),
                   int(df["Order Date"].isna().sum())]
    })
    st.dataframe(quality, use_container_width=True, hide_index=True)
    st.markdown("#### Missing values by column (after cleaning)")
    missing = df.isna().sum().rename_axis("Column").reset_index(name="Missing values")
    st.dataframe(missing[missing["Missing values"] > 0], use_container_width=True, hide_index=True)
    st.markdown("#### Preview cleaned data")
    st.dataframe(filtered.head(100), use_container_width=True, hide_index=True)

st.divider()
st.subheader("💡 Automatic business observations")
best_category = filtered.groupby("Category")["Sales"].sum().idxmax()
best_region = filtered.groupby("Region")["Sales"].sum().idxmax()
best_profit_category = filtered.groupby("Category")["Profit"].sum().idxmax()
loss_rows = int((filtered["Profit"] < 0).sum())
discount_corr = filtered[["Discount", "Profit"]].corr(numeric_only=True).iloc[0, 1]
observations = [
    f"**Highest-revenue category:** {best_category}. Review its best-selling products and stock availability.",
    f"**Highest-revenue region:** {best_region}. Compare its profit as well as sales before allocating more budget.",
    f"**Highest total-profit category:** {best_profit_category}. Consider protecting margins in this category.",
    f"**Loss-making rows:** {loss_rows:,} of {len(filtered):,} filtered records show negative profit. Review pricing, costs, and discounts."
]
if pd.notna(discount_corr):
    observations.append(f"**Discount-profit correlation:** {discount_corr:.2f}. This is an association, not proof that discounts cause profit changes.")
for item in observations:
    st.markdown(f"- {item}")

st.download_button(
    "⬇️ Download filtered, cleaned data (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="retail_sales_cleaned.csv",
    mime="text/csv"
)
summary = pd.DataFrame({
    "Metric": ["Total Sales", "Total Profit", "Quantity Sold", "Orders", "Customers",
               "Average Order Value", "Profit Margin (%)"],
    "Value": [total_sales, total_profit, total_quantity, orders, customers, avg_order_value, profit_margin]
})
st.download_button(
    "⬇️ Download KPI summary (CSV)",
    data=summary.to_csv(index=False).encode("utf-8"),
    file_name="retail_sales_kpi_summary.csv",
    mime="text/csv"
)
st.caption("Academic project note: the included dataset is synthetic demo data. Replace it with a documented real dataset before presenting findings as real-world business results.")
