import requests
import os
import glob
from datetime import datetime

PROMETHEUS_URL = "http://localhost:9090"
CRITICAL_CPU_THRESHOLD = 80
LOG_FILE = "self_heal_log.txt"
DEMO_TEMP_FOLDER = "demo_temp_files"


def get_current_cpu_usage():
    query = '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)'
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
    data = response.json()

    if data["status"] != "success" or not data["data"]["result"]:
        print("Could not get CPU data. Is Prometheus running?")
        return None

    value = float(data["data"]["result"][0]["value"][1])
    return value


def log_action(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")


def clear_temp_files():
    os.makedirs(DEMO_TEMP_FOLDER, exist_ok=True)
    files = glob.glob(os.path.join(DEMO_TEMP_FOLDER, "*"))

    if not files:
        log_action("Self-healing triggered: no temp files to clear (demo folder empty).")
        return

    for f in files:
        os.remove(f)
    log_action(f"Self-healing triggered: cleared {len(files)} temp file(s).")


def run_check():
    print("Running NMS Self-Healing Check...\n")
    cpu_usage = get_current_cpu_usage()

    if cpu_usage is None:
        return

    print(f"Current CPU usage: {cpu_usage:.2f}%")
    print(f"Critical threshold: {CRITICAL_CPU_THRESHOLD}%\n")

    if cpu_usage >= CRITICAL_CPU_THRESHOLD:
        print("CRITICAL state detected. Triggering self-healing action...")
        clear_temp_files()
    else:
        print("System healthy. No action needed.")


if __name__ == "__main__":
    run_check()
