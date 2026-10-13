# Retail Sales Data Analysis & Business Insights Dashboard

A beginner-friendly data analytics project built with Python, Pandas, NumPy, Plotly, and Streamlit. The dashboard provides interactive sales KPIs, product/category analysis, customer and regional performance, data-quality checks, and CSV exports.

## Features

- KPI cards: total sales, profit, quantity, orders, profit margin, average order value, and customers
- Sidebar filters for date, category, region, and customer segment
- Monthly sales trend, regional sales, sales-vs-profit scatter plot, and correlation heatmap
- Category and sub-category profitability analysis
- Top products and customers tables/charts
- Data-cleaning summary and cleaned data preview
- Download filtered clean data and KPI summary as CSV

## Project structure

```text
retail_sales_dashboard/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    └── retail_sales_demo.csv
```

## Requirements

- Python 3.10 or newer
- VS Code
- VS Code Python extension

## Run in VS Code

1. Extract the project ZIP and open the `retail_sales_dashboard` folder in VS Code.
2. Open Terminal → New Terminal.
3. Create a virtual environment:

   **Windows PowerShell**
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt:
   ```bat
   .venv\Scripts\activate.bat
   ```

4. Install dependencies:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Start the dashboard:
   ```bash
   streamlit run app.py
   ```

6. Streamlit will show a local URL, usually `http://localhost:8501`. Open it in your browser.

## Dataset

`data/retail_sales_demo.csv` is a **synthetic demo dataset** created for learning. It includes 650 generated retail records and a few intentional quality issues (missing values, inconsistent region capitalization, invalid date, and duplicate rows) so you can demonstrate cleaning. It is not real company data, and its findings must not be presented as actual market facts.

For a more realistic project, download a public **Sample Superstore** dataset from a reputable source such as Tableau's sample-data resources or a public dataset repository. Keep the CSV locally, then upload it through the dashboard sidebar. Common Superstore columns such as `Order Date`, `Sales`, `Profit`, `Quantity`, `Region`, `Category`, `Sub-Category`, `Customer Name`, `Customer ID`, `Segment`, and `Order ID` are supported. If a downloaded CSV has a different schema, adjust the column aliases in `normalize_columns()` in `app.py`.

## Data cleaning approach

- Remove exact duplicate rows
- Convert Sales, Profit, Quantity, and Discount to numeric types
- Fill missing numeric values with the column median (or zero if all values are missing)
- Parse order dates and mark invalid dates as missing
- Trim whitespace and fill missing category/region labels with `Unknown`
- Keep unknown customer identifiers missing rather than inventing identities

## Suggested analysis questions

1. Which category generates the highest revenue?
2. Which region generates the most sales and profit?
3. Which products have high sales but low or negative profit?
4. How do sales change month by month?
5. Are discounts associated with lower profit in this dataset?
6. Which customers contribute the most revenue?
7. How many rows contain negative profit?

## How to write your business insights

Use the actual filtered dashboard results. For example:

- “The highest-revenue category in the selected period was **[category]**, contributing **[amount]** in sales.”
- “The region with the highest sales was **[region]**. Its profit should also be compared before increasing investment.”
- “**[number]** records had negative profit. The business should review discounting, pricing, and costs for those products.”
- “The correlation between discount and profit was **[value]**. Correlation does not establish causation.”

Do not copy placeholder numbers from tutorials. Report only values produced by your selected dataset and filters.

## Limitations

- A missing Profit column is treated as zero for compatibility, so use a dataset with a real Profit field for meaningful profit analysis.
- Invalid order dates are excluded from date-based charts.
- The dashboard's correlation analysis shows associations, not causation.
- Synthetic demo data is for learning and software testing only.

## Future improvements

- Add a monthly sales forecast
- Add product-level profit margin analysis
- Add PDF report generation
- Deploy the Streamlit app online

## License / attribution

The demo CSV is synthetic and was generated for this educational project. Attribute any external dataset according to its original license and terms.
