import json
import math
import subprocess
import time
import uuid
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# ================= KONFIGURASI =================
GROUP_TAG = "kelompok_iot_vault_01"
BROKER_HOST = "broker.emqx.io"
BROKER_PORT = 1883

TOPIC_TELEMETRY = f"vaultsafe/{GROUP_TAG}/edge1/telemetry"
TOPIC_ALERTS = f"vaultsafe/{GROUP_TAG}/alerts"
TOPIC_COMMANDS = f"vaultsafe/{GROUP_TAG}/commands"

# Sensor Termux (sesuaikan jika nama sensor di HP berbeda)
ACCEL_SENSOR_NAME = "sc7a20e"
LIGHT_SENSOR_NAME = "stk33562"

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

def evaluate_threat(prev_sample, curr_sample):
    t_prev, lux_prev, accel_prev = prev_sample
    t_curr, lux_curr, accel_curr = curr_sample
    dt = max(t_curr - t_prev, 0.001)

    delta_lux_rate = max(0.0, (lux_curr - lux_prev) / dt)
    mag_prev = math.sqrt(accel_prev[0]**2 + accel_prev[1]**2 + accel_prev[2]**2)
    mag_curr = math.sqrt(accel_curr[0]**2 + accel_curr[1]**2 + accel_curr[2]**2)
    jerk = abs(mag_curr - mag_prev) / dt

    threat_score = 0
    if lux_curr > 10.0 or delta_lux_rate > 15.0:
        threat_score += 60
    elif lux_curr > 3.0:
        threat_score += 25

    if jerk > 3.0:
        threat_score += 40
    elif jerk > 1.0:
        threat_score += 20

    if threat_score >= 70:
        status = "BREACH_CRITICAL"
    elif threat_score >= 30:
        status = "TAMPER_WARNING"
    else:
        status = "SAFE"

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
            analysis = evaluate_threat(prev_sample, curr_sample)
            prev_sample = curr_sample

            telemetry = {
                "device_id": "edge1_vault",
                "timestamp": curr_sample[0],
                "metrics": analysis
            }
            client.publish(TOPIC_TELEMETRY, json.dumps(telemetry), qos=0)
            print(f"[STATUS] {analysis['status']} | Score: {analysis['score']} | Lux: {analysis['current_lux']}")

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
