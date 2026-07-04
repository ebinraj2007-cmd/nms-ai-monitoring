import requests
import smtplib
from email.mime.text import MIMEText

PROMETHEUS_URL = "http://localhost:9090"
CRITICAL_CPU = 80

GMAIL_ADDRESS = "ebinraj2007@gmail.com"
GMAIL_APP_PASSWORD = "ixve gjut vpuq hsdh"
ALERT_TO = "ebinraj2007@gmail.com"


def get_cpu_usage():
    query = '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)'
    r = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
    result = r.json()["data"]["result"]
    return float(result[0]["value"][1]) if result else None


def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = ALERT_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)
    print("Alert email sent.")


if __name__ == "__main__":
    cpu = get_cpu_usage()
    print(f"CPU usage: {cpu:.2f}%")
    if cpu and cpu >= CRITICAL_CPU:
        send_email(
            "NMS ALERT: Critical CPU Usage",
            f"CPU usage is at {cpu:.2f}%, above the {CRITICAL_CPU}% threshold."
        )
    else:
        print("No alert needed.")
