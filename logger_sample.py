import json
import math
import subprocess
import time
import csv
from datetime import datetime

# ================= KONFIGURASI =================
# Sensor Termux (sesuaikan jika nama sensor di HP berbeda)
ACCEL_SENSOR_NAME = "sc7a20e"
LIGHT_SENSOR_NAME = "stk33562"
FILE_CSV = "dataset_vaultsafe.csv"

def read_sensors():
    try:
        cmd = ["termux-sensor", "-s", f"{ACCEL_SENSOR_NAME},{LIGHT_SENSOR_NAME}", "-n", "1"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        data = json.loads(res.stdout)
        accel = tuple(float(v) for v in data[ACCEL_SENSOR_NAME]["values"][:3])
        lux = float(data[LIGHT_SENSOR_NAME]["values"][0])
        return time.time(), lux, accel
    except Exception:
        return time.time(), 0.0, (0.0, 0.0, 9.8)

def calculate_jerk(prev_sample, curr_sample):
    t_prev, lux_prev, accel_prev = prev_sample
    t_curr, lux_curr, accel_curr = curr_sample
    dt = max(t_curr - t_prev, 0.001)

    mag_prev = math.sqrt(accel_prev[0]**2 + accel_prev[1]**2 + accel_prev[2]**2)
    mag_curr = math.sqrt(accel_curr[0]**2 + accel_curr[1]**2 + accel_curr[2]**2)
    jerk = abs(mag_curr - mag_prev) / dt
    
    return lux_curr, jerk

def main():
    with open(FILE_CSV, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Lux", "Jerk"])
        
        print(f"[INFO] Perekaman dimulai ke file: {FILE_CSV}")
        print("[INFO] Siapkan catatan waktumu. Tekan CTRL+C untuk berhenti.\n")

        prev_sample = read_sensors()

        try:
            while True:
                time.sleep(1.0)
                curr_sample = read_sensors()
                lux_curr, jerk = calculate_jerk(prev_sample, curr_sample)
                prev_sample = curr_sample
                
                waktu_sekarang = datetime.now().strftime("%H:%M:%S")
                
                writer.writerow([waktu_sekarang, round(lux_curr, 2), round(jerk, 2)])
                file.flush()
                
                print(f"[{waktu_sekarang}] Lux: {round(lux_curr, 2):<6} | Jerk: {round(jerk, 2):<6}")
                
        except KeyboardInterrupt:
            print(f"\n[INFO] Perekaman dihentikan. File {FILE_CSV} berhasil disimpan.")

if __name__ == "__main__":
    main()