from pathlib import Path
import pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
BASE=Path(__file__).parent; OUT=BASE/"outputs"; OUT.mkdir(exist_ok=True)
df=pd.read_csv(BASE/"data/customer_transactions.csv").drop_duplicates(); df["Transaction_Date"]=pd.to_datetime(df["Transaction_Date"],errors="coerce")
for c in ["Quantity","Unit_Price","Amount"]: df[c]=pd.to_numeric(df[c],errors="coerce").fillna(pd.to_numeric(df[c],errors="coerce").median())
df=df.dropna(subset=["Customer_ID","Transaction_Date"]); snapshot=df["Transaction_Date"].max()+pd.Timedelta(days=1)
rfm=df.groupby("Customer_ID").agg(Last_Purchase=("Transaction_Date","max"),Frequency=("Transaction_ID","nunique"),Monetary=("Amount","sum")).reset_index(); rfm["Recency"]=(snapshot-rfm["Last_Purchase"]).dt.days; rfm=rfm[["Customer_ID","Recency","Frequency","Monetary"]]
X=StandardScaler().fit_transform(rfm[["Recency","Frequency","Monetary"]]); scores={}
for k in range(2,7): scores[k]=silhouette_score(X,KMeans(n_clusters=k,random_state=42,n_init=10).fit_predict(X))
best=max(scores,key=scores.get); rfm["Cluster"]=KMeans(n_clusters=best,random_state=42,n_init=10).fit_predict(X); print("Silhouette scores:",scores,"Chosen k:",best)
profile=rfm.groupby("Cluster").agg(Customers=("Customer_ID","count"),Avg_Recency_Days=("Recency","mean"),Avg_Frequency=("Frequency","mean"),Avg_Monetary=("Monetary","mean")).round(2); print(profile)
rfm.to_csv(OUT/"customer_segments.csv",index=False); profile.to_csv(OUT/"segment_profiles.csv")
sns.scatterplot(data=rfm,x="Frequency",y="Monetary",hue="Cluster",palette="tab10"); plt.title("Customer Segments"); plt.tight_layout(); plt.savefig(OUT/"customer_segments.png"); plt.close()
print("Recommendations: high-spend frequent customers -> loyalty rewards; high-recency customers -> win-back campaign; others -> bundles and repeat-purchase reminders.")
