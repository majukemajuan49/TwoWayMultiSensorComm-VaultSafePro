# VaultSafe Pro - Sistem Keamanan Anti-Tamper Berbasis IoT

VaultSafe Pro adalah Sistem Keamanan & Pemantau Ruang Penyimpanan Tertutup Berbasis IoT (Smart Enclosure & Anti-Tamper Security System). Proyek ini ditujukan untuk memantau laci, brankas mini, lemari berkas, atau tas dari pembongkaran secara *real-time* menggunakan sensor internal *smartphone*.

## 🌟 Fitur Utama
1. **Multi-Sensor Edge Detection:** Menggunakan sensor cahaya (Ambient Light) dan sensor gerak (Accelerometer) secara bersamaan.
2. **Advanced Data Processing:** Menganalisis lonjakan laju cahaya (ΔLux) dan sentakan gerak (Motion Jerk).
3. **Smart Threat Scoring Algorithm:** Klasifikasi status cerdas (SAFE, TAMPER_WARNING, BREACH_CRITICAL).
4. **2-Way Cloud Communication:** Terhubung via broker MQTT `broker.emqx.io` (Uplink untuk telemetri/alert, Downlink untuk perintah balik).
5. **Interactive Smart Alarm:** Text-to-Speech (TTS) adaptif, senter LED (torch), dan getaran haptik.
6. **Local Web Dashboard:** Visualisasi grafik real-time menggunakan `Chart.js` dan kontrol remote.

## 📂 Struktur Repositori
```text
vaultsafe-pro/
├── hp_laci.py              # Node Edge 1 (Diletakkan di dalam brankas/laci)
├── hp_pemilik.py           # Node Edge 2 (Dipegang oleh pengguna/pemilik)
├── dashboard/
│   ├── server.py           # Server lokal untuk menyajikan UI dashboard
│   └── index.html          # Web UI Dashboard (Live Chart & Controls)
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
   pip install -r requirements.txt
   ```

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
*HP ini akan otomatis bergetar dan berbicara jika HP 1 mendeteksi guncangan atau cahaya mendadak.*

### 3. Menjalankan Dashboard (Di Laptop)
1. Pastikan laptop terhubung ke WiFi/Hotspot yang sama.
2. Buka terminal laptop, arahkan ke folder `dashboard`, lalu jalankan:
   ```bash
   python server.py
   ```
3. Buka browser dan akses alamat yang tertera (contoh: `http://localhost:8000`).

## ⚙️ Skenario Pengujian (Demo)
* **Status SAFE:** Laci dibiarkan tertutup rapat dan gelap.
* **Status TAMPER_WARNING:** Senggol meja dengan cukup keras tanpa membuka laci. HP 2 akan memberikan peringatan TTS volume sedang.
* **Status BREACH_CRITICAL:** Buka laci secara paksa dari keadaan gelap ke terang. HP 2 akan membunyikan TTS peringatan bahaya volume maksimal dan bergetar panjang.
* **Remote Alarm (Downlink):** Klik tombol "Picu Senter & Sirine Darurat" di Dashboard atau ketik "1" di HP Pemilik. HP Laci akan menyalakan flash kamera dan memberikan peringatan TTS kepada pelaku.
