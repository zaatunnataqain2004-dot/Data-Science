from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
BASE=Path(__file__).parent; OUT=BASE/"outputs"; OUT.mkdir(exist_ok=True); df=pd.read_csv(BASE/"data/house_prices.csv").drop_duplicates()
num=["Area_sqft","Bedrooms","Bathrooms","Age_Years","Quality_Score","Price"]
for col in num: df[col]=pd.to_numeric(df[col],errors="coerce")
df=df.dropna(subset=["Price"]); features=num[:-1]+["Location"]
for col in num[:-1]: df[col]=df[col].fillna(df[col].median())
df["Location"]=df["Location"].fillna(df["Location"].mode()[0]).astype(str).str.strip()
q1,q3=df.Price.quantile([.25,.75]); iqr=q3-q1; print("Potential price outliers (IQR):",int(((df.Price<q1-1.5*iqr)|(df.Price>q3+1.5*iqr)).sum()))
sns.histplot(df.Price,kde=True); plt.title("Price Distribution"); plt.tight_layout(); plt.savefig(OUT/"price_distribution.png"); plt.close()
sns.scatterplot(data=df,x="Area_sqft",y="Price",hue="Location"); plt.title("Area vs Price"); plt.tight_layout(); plt.savefig(OUT/"area_vs_price.png"); plt.close()
sns.heatmap(df[num].corr(),annot=True,cmap="coolwarm",fmt=".2f"); plt.title("Feature Correlations"); plt.tight_layout(); plt.savefig(OUT/"correlation_heatmap.png"); plt.close()
X=df[features]; y=df["Price"]; numeric=features[:-1]; categorical=["Location"]
prep=ColumnTransformer([("num",Pipeline([("imp",SimpleImputer(strategy="median")),("scale",StandardScaler())]),numeric),("cat",Pipeline([("imp",SimpleImputer(strategy="most_frequent")),("ohe",OneHotEncoder(handle_unknown="ignore"))]),categorical)])
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42); results=[]; best=None; best_rmse=float("inf"); best_pred=None
for name,model in [("Linear Regression",LinearRegression()),("Ridge",Ridge()),("Random Forest",RandomForestRegressor(n_estimators=150,random_state=42))]:
 pipe=Pipeline([("prep",prep),("model",model)]); pipe.fit(Xtr,ytr); pred=pipe.predict(Xte); mae=mean_absolute_error(yte,pred); rmse=np.sqrt(mean_squared_error(yte,pred)); r2=r2_score(yte,pred); results.append([name,mae,rmse,r2]); print(f"{name}: MAE={mae:,.0f}, RMSE={rmse:,.0f}, R2={r2:.3f}")
 if rmse<best_rmse: best,best_rmse,best_pred=name,rmse,pred
pd.DataFrame(results,columns=["Model","MAE","RMSE","R2"]).to_csv(OUT/"model_comparison.csv",index=False); plt.scatter(yte,best_pred,alpha=.6); plt.xlabel("Actual price"); plt.ylabel("Predicted price"); plt.title("Actual vs Predicted: "+best); plt.tight_layout(); plt.savefig(OUT/"actual_vs_predicted.png"); plt.close(); print("Outputs saved to",OUT)
