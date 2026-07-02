"""
NMS AI Monitoring - Disk Prediction Engine (v1)
Matches PRD Section 7: AI & Predictive Analytics

What it does:
1. Asks Prometheus for disk usage history (last 6 hours)
2. Fits a simple linear trend line through the data
3. Predicts the date the disk will hit 100% full
4. Assigns a Risk Score: Low / Medium / High
"""

import requests
import numpy as np
from datetime import datetime, timedelta

PROMETHEUS_URL = "http://localhost:9090"

def get_disk_usage_history():
    """Fetch disk usage % over the last 6 hours from Prometheus."""
    query = (
        '100 - ((node_filesystem_avail_bytes{mountpoint="/"} '
        '* 100) / node_filesystem_size_bytes{mountpoint="/"})'
    )
    end = datetime.now()
    start = end - timedelta(hours=6)

    params = {
        "query": query,
        "start": start.timestamp(),
        "end": end.timestamp(),
        "step": "60s",  # one data point per minute
    }

    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query_range", params=params)
    data = response.json()

    if data["status"] != "success" or not data["data"]["result"]:
        print("⚠️  No disk data found. Is Prometheus running and scraping your agent?")
        return None

    values = data["data"]["result"][0]["values"]
    timestamps = np.array([float(v[0]) for v in values])
    usage_pct = np.array([float(v[1]) for v in values])
    return timestamps, usage_pct


def predict_disk_full(timestamps, usage_pct):
    """Fit a straight line to the data and predict when usage hits 100%."""
    # Fit: usage = slope * time + intercept
    slope, intercept = np.polyfit(timestamps, usage_pct, 1)

    current_usage = usage_pct[-1]
    print(f"\n📊 Current disk usage: {current_usage:.2f}%")

    if slope <= 0:
        print("✅ Disk usage is stable or decreasing. No risk detected.")
        return

    # Solve for time when usage = 100
    seconds_until_full = (100 - intercept) / slope
    predicted_date = datetime.fromtimestamp(seconds_until_full)
    days_remaining = (predicted_date - datetime.now()).days

    # Risk scoring (matches PRD Section 7.2)
    if days_remaining <= 7:
        risk = "🔴 HIGH"
        recommendation = "Immediate cleanup or storage upgrade required."
    elif days_remaining <= 30:
        risk = "🟠 MEDIUM"
        recommendation = "Plan a cleanup or upgrade within the next few weeks."
    else:
        risk = "🟢 LOW"
        recommendation = "No action needed right now."

    print(f"📅 Predicted disk-full date: {predicted_date.strftime('%Y-%m-%d')}")
    print(f"⏳ Days remaining: {days_remaining}")
    print(f"⚠️  Risk score: {risk}")
    print(f"💡 Recommendation: {recommendation}\n")


if __name__ == "__main__":
    print("Running NMS AI Disk Prediction Engine...\n")
    result = get_disk_usage_history()
    if result:
        timestamps, usage_pct = result
        predict_disk_full(timestamps, usage_pct)
