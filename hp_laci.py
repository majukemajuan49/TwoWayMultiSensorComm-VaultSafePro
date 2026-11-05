import json
import math
import subprocess
import time
import uuid
import joblib
import warnings
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# Abaikan warning scikit-learn soal feature names
warnings.filterwarnings("ignore", category=UserWarning)

# ================= KONFIGURASI =================
GROUP_TAG = "kelompok_iot_vault_01"
BROKER_HOST = "broker.emqx.io"
BROKER_PORT = 1883

TOPIC_TELEMETRY = f"vaultsafe/{GROUP_TAG}/edge1/telemetry"
TOPIC_ALERTS = f"vaultsafe/{GROUP_TAG}/alerts"
TOPIC_COMMANDS = f"vaultsafe/{GROUP_TAG}/commands"

ACCEL_SENSOR_NAME = "sc7a20e"
LIGHT_SENSOR_NAME = "stk33562"
MODEL_FILE = "vaultsafe_model.pkl"

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

def evaluate_threat_ai(prev_sample, curr_sample, model):
    t_prev, lux_prev, accel_prev = prev_sample
    t_curr, lux_curr, accel_curr = curr_sample
    dt = max(t_curr - t_prev, 0.001)

    delta_lux_rate = max(0.0, (lux_curr - lux_prev) / dt)
    mag_prev = math.sqrt(accel_prev[0]**2 + accel_prev[1]**2 + accel_prev[2]**2)
    mag_curr = math.sqrt(accel_curr[0]**2 + accel_curr[1]**2 + accel_curr[2]**2)
    jerk = abs(mag_curr - mag_prev) / dt

    # 1. AI MENGAMBIL KEPUTUSAN BERDASARKAN POLA (Bukan lagi if-else kaku)
    # Model menerima array 2D: [[Lux, Jerk]]
    prediksi_ai = model.predict([[lux_curr, jerk]])[0]

    # 2. Terjemahkan output AI (0, 1, 2) menjadi status
    if prediksi_ai == 2:
        status = "BREACH_CRITICAL"
        threat_score = 100 # Skor dummy agar grafik dashboard tetap jalan
    elif prediksi_ai == 1:
        status = "TAMPER_WARNING"
        threat_score = 50
    else:
        status = "SAFE"
        threat_score = 0

    return {
        "status": status,
        "score": threat_score,
        "lux_rate": round(delta_lux_rate, 2),
        "jerk": round(jerk, 2),
        "current_lux": round(lux_curr, 2)
    }

def on_connect(client, userdata, flags, rc, *args):
    print(f"\n[EDGE 1] Terhubung ke broker {BROKER_HOST}! (rc={rc})")
    client.subscribe(TOPIC_COMMANDS, qos=1)
    print(f"[EDGE 1] Mendengarkan perintah downlink di: {TOPIC_COMMANDS}\n")

def on_message(client, userdata, msg, *args):
    raw_payload = msg.payload.decode()
    print(f"\n>>> [EDGE 1 MENERIMA COMMAND] {raw_payload}")
    try:
        payload = json.loads(raw_payload)
        action = payload.get("action")
        
        if action == "TRIGGER_ALARM":
            print(">> AKSI: Menyalakan senter, suara, dan getaran!")
            subprocess.run(["termux-volume", "music", "15"])
            subprocess.run(["termux-torch", "on"])
            subprocess.run(["termux-tts-speak", "Security system active! Get AWAY!"])
            subprocess.run(["termux-vibrate", "-d", "1500"])
            time.sleep(4)
            subprocess.run(["termux-torch", "off"])
        elif action == "BEEP":
            print(">> AKSI: Beep getar singkat!")
            subprocess.run(["termux-volume", "music", "10"])
            subprocess.run(["termux-tts-speak", "System secure."])
            subprocess.run(["termux-vibrate", "-d", "400"])
    except Exception as e:
        print(f"Error parse: {e}")

def main():
    print(f"[INFO] Memuat model AI dari {MODEL_FILE}...")
    try:
        ai_model = joblib.load(MODEL_FILE)
        print("[INFO] Model AI berhasil dimuat!")
    except Exception as e:
        print(f"[ERROR] Gagal memuat model: {e}")
        return

    unique_id = f"edge1_{uuid.uuid4().hex[:6]}"
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=unique_id)
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[EDGE 1] Menghubungkan ke {BROKER_HOST}:{BROKER_PORT}...")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()

    prev_sample = read_sensors()

    try:
        while True:
            time.sleep(1.0)
            curr_sample = read_sensors()
            
            # Panggil fungsi evaluasi yang sudah disuntikkan AI
            analysis = evaluate_threat_ai(prev_sample, curr_sample, ai_model)
            prev_sample = curr_sample

            telemetry = {
                "device_id": "edge1_vault",
                "timestamp": curr_sample[0],
                "metrics": analysis
            }
            client.publish(TOPIC_TELEMETRY, json.dumps(telemetry), qos=0)
            print(f"[AI STATUS] {analysis['status']} | Jerk: {analysis['jerk']} | Lux: {analysis['current_lux']}")

            if analysis["status"] in ["BREACH_CRITICAL", "TAMPER_WARNING"]:
                alert_payload = {
                    "alert_type": analysis["status"],
                    "score": analysis["score"],
                    "timestamp": curr_sample[0]
                }
                client.publish(TOPIC_ALERTS, json.dumps(alert_payload), qos=1)

    except KeyboardInterrupt:
        print("\nEdge 1 Berhenti.")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()