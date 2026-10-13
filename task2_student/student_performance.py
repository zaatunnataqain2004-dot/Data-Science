from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  # type: ignore[import-not-found]
import seaborn as sns  # type: ignore[import-not-found]
from sklearn.model_selection import train_test_split  # type: ignore[import-not-found]
from sklearn.compose import ColumnTransformer  # type: ignore[import-not-found]
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # type: ignore[import-not-found]
from sklearn.pipeline import Pipeline  # type: ignore[import-not-found]
from sklearn.impute import SimpleImputer  # type: ignore[import-not-found]
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score  # type: ignore[import-not-found]
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor  # type: ignore[import-not-found]
BASE=Path(__file__).parent; OUT=BASE/"outputs"; OUT.mkdir(exist_ok=True)
df=pd.read_csv(BASE/"data/student_performance.csv"); print("Original shape:",df.shape); print(df.isna().sum())
df=df.drop_duplicates().dropna(subset=["Final_Score"]).copy()
for c in ["Study_Time_Hours","Attendance_Percent","Previous_Score"]: df[c]=pd.to_numeric(df[c],errors="coerce").fillna(df[c].median())
for c in ["Parental_Education","Internet_Access","Extracurricular_Activities"]: df[c]=df[c].fillna(df[c].mode()[0])
print(df.describe())
sns.histplot(df["Final_Score"],kde=True); plt.title("Final Score Distribution"); plt.tight_layout(); plt.savefig(OUT/"score_distribution.png"); plt.close()
sns.regplot(data=df,x="Study_Time_Hours",y="Final_Score"); plt.title("Study Time vs Score"); plt.tight_layout(); plt.savefig(OUT/"study_vs_score.png"); plt.close()
features=["Study_Time_Hours","Attendance_Percent","Previous_Score","Parental_Education","Internet_Access","Extracurricular_Activities"]; X=df[features]; y=df["Final_Score"]
num=features[:3]; cat=features[3:]
prep=ColumnTransformer([("num",Pipeline([("imp",SimpleImputer(strategy="median")),("scale",StandardScaler())]),num),("cat",Pipeline([("imp",SimpleImputer(strategy="most_frequent")),("ohe",OneHotEncoder(handle_unknown="ignore"))]),cat)])
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42); results=[]
for name,model in [("Random Forest",RandomForestRegressor(n_estimators=150,random_state=42)),("Gradient Boosting",HistGradientBoostingRegressor(random_state=42))]:
 pipe=Pipeline([("prep",prep),("model",model)]); pipe.fit(Xtr,ytr); pred=pipe.predict(Xte); mae=mean_absolute_error(yte,pred); rmse=np.sqrt(mean_squared_error(yte,pred)); r2=r2_score(yte,pred); results.append([name,mae,rmse,r2]); print(f"{name}: MAE={mae:.2f}, RMSE={rmse:.2f}, R2={r2:.3f}")
pd.DataFrame(results,columns=["Model","MAE","RMSE","R2"]).to_csv(OUT/"model_comparison.csv",index=False); print("Outputs saved in",OUT)
