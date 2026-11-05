# VaultSafe Pro - Sistem Keamanan Anti-Tamper Berbasis Edge AI & IoT

VaultSafe Pro adalah Sistem Keamanan & Pemantau Ruang Penyimpanan Tertutup Berbasis IoT (Smart Enclosure & Anti-Tamper Security System). Proyek ini ditujukan untuk memantau laci, brankas mini, lemari berkas, atau tas dari pembongkaran secara *real-time* menggunakan sensor internal *smartphone*. 

Sistem ini kini ditenagai oleh **Edge AI (Machine Learning)** untuk mengklasifikasikan status keamanan secara cerdas tanpa membebani komputasi perangkat.

## 🌟 Fitur Utama
1. **Multi-Sensor Edge Detection:** Menggunakan sensor cahaya (Ambient Light) dan sensor gerak (Accelerometer) secara bersamaan.
2. **Advanced Data Processing:** Mengekstraksi fitur lonjakan laju cahaya (ΔLux) dan sentakan gerak (Motion Jerk).
3. **Zero-Dependency Edge AI:** Klasifikasi status (SAFE, TAMPER_WARNING, BREACH_CRITICAL) ditenagai oleh algoritma **Random Forest** yang ditranspilasi menjadi Python murni menggunakan `m2cgen`. AI berjalan dengan latensi nyaris 0 ms tanpa membutuhkan *library* berat seperti Scikit-learn di HP Laci!
4. **2-Way Cloud Communication:** Terhubung via broker MQTT `broker.emqx.io` (Uplink untuk telemetri/alert, Downlink untuk perintah balik).
5. **Interactive Smart Alarm:** Text-to-Speech (TTS) adaptif, senter LED (torch), dan getaran haptik.
6. **Local Web Dashboard:** Visualisasi grafik real-time menggunakan `Chart.js` dan kontrol remote.

## 📂 Struktur Repositori
```text
vaultsafe-pro/
├── hp_laci.py              # Node Edge 1 (Di laci) - Menjalankan AI inference
├── model_ai_murni.py       # "Otak" AI dalam pure Python (Hasil m2cgen)
├── hp_pemilik.py           # Node Edge 2 (Dipegang oleh pemilik)
├── dashboard/
│   ├── server.py           # Server lokal UI dashboard
│   └── index.html          # Web UI Dashboard (Live Chart & Controls)
├── AI_Training/            # [Folder Opsional] Skrip pelatihan model di PC
│   ├── dataset_vaultsafe.csv
│   ├── train_model.py
│   ├── export_m2c.py
│   └── vaultsafe_model.pkl
├── logger_sample.py        # Skrip pengambil data mentah untuk training
├── requirements.txt        # Dependensi Python
└── README.md               # Dokumentasi Proyek
```

## 🛠️ Cara Instalasi & Menjalankan

### Persiapan di HP Android (Edge 1 & Edge 2)
1. Unduh dan install **Termux** serta **Termux:API** (dari F-Droid).
2. Berikan izin **Notification** dan matikan *Battery Optimization* untuk Termux.
3. Buka Termux, jalankan perintah berikut:
   ```bash
   pkg update -y
   pkg install python git termux-api -y
   pip install paho-mqtt
   ```
   *(Catatan: HP Laci tidak perlu menginstal scikit-learn atau pandas berkat penggunaan pure Python AI model!)*

### 1. Menjalankan Edge 1 (HP Laci)
Buka Termux di HP 1, pastikan layar HP tidak terkunci mati, dan jalankan:
```bash
python hp_laci.py
```
*Masukkan HP ini ke dalam laci atau tutupi layarnya hingga gelap.*

### 2. Menjalankan Edge 2 (HP Pemilik)
Buka Termux di HP 2, jalankan:
```bash
python hp_pemilik.py
```
*HP ini akan otomatis bergetar dan berbicara jika HP 1 mendeteksi pola ancaman dari model AI.*

### 3. Menjalankan Dashboard (Di Laptop)
1. Pastikan laptop terhubung ke WiFi/Hotspot yang sama.
2. Buka terminal laptop, arahkan ke folder `dashboard`, lalu jalankan:
   ```bash
   python server.py
   ```
3. Buka browser dan akses alamat yang tertera (contoh: `http://localhost:8000`).

## ⚙️ Skenario Pengujian (Demo)
- **Status SAFE (0):** Laci dibiarkan tertutup rapat dan gelap.
- **Status TAMPER_WARNING (1):** Senggol meja dengan cukup keras tanpa membuka laci. AI mendeteksi lonjakan *Jerk* saat gelap dan HP 2 akan memberikan peringatan TTS volume sedang.
- **Status BREACH_CRITICAL (2):** Buka laci secara paksa dari keadaan gelap ke terang. AI mendeteksi kombinasi cahaya & getaran. HP Laci akan menyalakan alarm & senter lokal, sementara HP 2 membunyikan TTS peringatan bahaya volume maksimal.
- **Remote Alarm (Downlink):** Klik tombol "Picu Senter & Sirine Darurat" di Dashboard atau ketik "1" di HP Pemilik. HP Laci akan menyalakan flash kamera dan memberikan peringatan TTS kepada pelaku.