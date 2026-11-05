import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# 1. Muat Dataset
print("[INFO] Memuat dataset...")
df = pd.read_csv('dataset_vaultsafe.csv')

# 2. Pisahkan Fitur (X) dan Target/Label (y)
# AI hanya belajar dari angka Lux dan Jerk. Timestamp tidak dipakai.
X = df[['Lux', 'Jerk']]
y = df['Label']

# 3. Bagi Data: 80% untuk Training (Belajar), 20% untuk Ujian (Testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Inisialisasi dan Latih Model
print("[INFO] Melatih model AI (Random Forest)...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 5. Evaluasi Akurasi Ujian
print("[INFO] Mengevaluasi model dengan data testing...")
y_pred = model.predict(X_test)
akurasi = accuracy_score(y_test, y_pred)
print(f"\n=> Akurasi Model: {akurasi * 100:.2f}%\n")

# Tampilkan rapor detail
print("Detail Klasifikasi per Skenario:")
print(classification_report(y_test, y_pred, target_names=['SAFE (0)', 'TAMPER (1)', 'BREACH (2)']))

# 6. Simpan "Otak" AI (Export Model)
nama_file_model = 'vaultsafe_model.pkl'
joblib.dump(model, nama_file_model)
print(f"[INFO] Selesai! Model pintar telah disimpan sebagai '{nama_file_model}'")