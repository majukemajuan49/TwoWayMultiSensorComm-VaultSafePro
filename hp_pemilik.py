import json
import subprocess
import threading
import uuid
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

GROUP_TAG = "kelompok_iot_vault_01"
BROKER_HOST = "broker.emqx.io"
BROKER_PORT = 1883

TOPIC_ALERTS = f"vaultsafe/{GROUP_TAG}/alerts"
TOPIC_COMMANDS = f"vaultsafe/{GROUP_TAG}/commands"

def on_connect(client, userdata, flags, rc, *args):
    print(f"\n[EDGE 2] Terhubung ke broker {BROKER_HOST}! (rc={rc})")
    client.subscribe(TOPIC_ALERTS, qos=1)
    print(f"[EDGE 2] Mendengarkan alert di: {TOPIC_ALERTS}\n")

def on_message(client, userdata, msg, *args):
    raw_payload = msg.payload.decode()
    print(f"\n>>> [EDGE 2 MENERIMA ALERT!] {raw_payload}")
    try:
        data = json.loads(raw_payload)
        alert_type = data.get("alert_type")
        score = data.get("score")
        
        if alert_type == "BREACH_CRITICAL":
            # subprocess.run(["termux-volume", "music", "10"])
            subprocess.run(["termux-tts-speak", "Bahaya! Sistem mendeteksi bahwa sebuah laci telah dibuka secara paksa! Segera periksa lokasinya!"])
            subprocess.run(["termux-vibrate", "-d", "1500"])
        elif alert_type == "TAMPER_WARNING":
            # subprocess.run(["termux-volume", "music", "15"])
            subprocess.run(["termux-tts-speak", "Peringatan: terdapat getaran mencurigakan di dalam laci."])
            subprocess.run(["termux-vibrate", "-d", "500"])
        
        subprocess.run([
            "termux-notification",
            "--title", "🚨 VAULTSAFE ALERT 🚨",
            "--content", f"Status: {alert_type} (Score: {score})"
        ])
    except Exception as e:
        print(f"Error parse: {e}")

def listen_loop(client):
    client.loop_forever()

def main():
    unique_id = f"edge2_{uuid.uuid4().hex[:6]}"
    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=unique_id)
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[EDGE 2] Menghubungkan ke {BROKER_HOST}:{BROKER_PORT}...")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)

    t = threading.Thread(target=listen_loop, args=(client,), daemon=True)
    t.start()

    print("[EDGE 2 SIAP]")
    print("Ketik 1 -> Kirim TRIGGER_ALARM (Nyalakan Flash & Sirine di Laci)")
    print("Ketik 2 -> Kirim BEEP (Getaran Peringatan Ringan)\n")

    try:
        while True:
            cmd = input().strip()
            if cmd == "1":
                payload = json.dumps({"action": "TRIGGER_ALARM"})
                res = client.publish(TOPIC_COMMANDS, payload, qos=1)
                res.wait_for_publish()
                print(f"-> [PUBLISHED] TRIGGER_ALARM terkirim ke {TOPIC_COMMANDS}")
            elif cmd == "2":
                payload = json.dumps({"action": "BEEP"})
                res = client.publish(TOPIC_COMMANDS, payload, qos=1)
                res.wait_for_publish()
                print(f"-> [PUBLISHED] BEEP terkirim ke {TOPIC_COMMANDS}")
            elif cmd == "exit":
                break
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
