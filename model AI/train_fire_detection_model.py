import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib

df = pd.read_csv('fire_detection_dataset.csv')

X = df[['T1', 'H1', 'T2', 'H2', 'CO2', 'PM2.5', 'PM10']]
y = df['Label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("=== MA TRẬN NHẦM LẪN ===")
print(confusion_matrix(y_test, y_pred))
print("\n=== BÁO CÁO CHI TIẾT ===")
print(classification_report(y_test, y_pred))

joblib.dump(model, 'fire_detection_model.pkl')
print("fire_detection_model.pkl done")
