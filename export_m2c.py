import joblib
import m2cgen as m2c

# 1. Muat model yang sudah pintar tadi
model = joblib.load('vaultsafe_model.pkl')

# 2. Terjemahkan model ke bahasa Python murni
print("Menerjemahkan model ke Python murni. Tunggu sebentar (karena ada 100 pohon)...")
kode_python_murni = m2c.export_to_python(model)

# 3. Simpan hasilnya menjadi file .py
with open('model_ai_murni.py', 'w') as f:
    f.write(kode_python_murni)

print("Berhasil! File 'model_ai_murni.py' sudah dibuat.")