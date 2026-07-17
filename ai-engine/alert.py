"""NMS alert engine — emails when CPU crosses a critical threshold.

Config comes from environment variables (never hardcode secrets in source):

  NMS_PROMETHEUS_URL      default http://localhost:9090
  NMS_CRITICAL_CPU        default 80
  NMS_GMAIL_ADDRESS       sender Gmail address
  NMS_GMAIL_APP_PASSWORD  Gmail app password (a secret - keep it out of git)
  NMS_ALERT_TO            recipient address
"""
import logging
import os
import smtplib
from email.mime.text import MIMEText

import requests

logging.basicConfig(level=os.environ.get("NMS_LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("nms.alert")

PROMETHEUS_URL = os.environ.get("NMS_PROMETHEUS_URL", "http://localhost:9090")
CRITICAL_CPU = float(os.environ.get("NMS_CRITICAL_CPU", "80"))
GMAIL_ADDRESS = os.environ.get("NMS_GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.environ.get("NMS_GMAIL_APP_PASSWORD")
ALERT_TO = os.environ.get("NMS_ALERT_TO", GMAIL_ADDRESS or "")
HTTP_TIMEOUT = float(os.environ.get("NMS_HTTP_TIMEOUT", "10"))


def get_cpu_usage():
    query = '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)'
    try:
        r = requests.get(f"{PROMETHEUS_URL}/api/v1/query",
                         params={"query": query}, timeout=HTTP_TIMEOUT)
        r.raise_for_status()
        result = r.json().get("data", {}).get("result", [])
    except (requests.RequestException, ValueError) as e:
        log.error("could not query Prometheus: %s", e)
        return None
    return float(result[0]["value"][1]) if result else None


def send_email(subject, body):
    if not (GMAIL_ADDRESS and GMAIL_APP_PASSWORD):
        log.error("NMS_GMAIL_ADDRESS / NMS_GMAIL_APP_PASSWORD not set - cannot send alert")
        return False
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = ALERT_TO
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=HTTP_TIMEOUT) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)
    except (smtplib.SMTPException, OSError) as e:
        log.error("failed to send alert email: %s", e)
        return False
    log.info("alert email sent to %s", ALERT_TO)
    return True


def main():
    cpu = get_cpu_usage()
    if cpu is None:
        log.warning("no CPU reading available; skipping")
        return
    log.info("CPU usage: %.2f%%", cpu)
    if cpu >= CRITICAL_CPU:
        send_email("NMS ALERT: Critical CPU Usage",
                   f"CPU usage is at {cpu:.2f}%, above the {CRITICAL_CPU}% threshold.")
    else:
        log.info("no alert needed (below %.0f%%)", CRITICAL_CPU)


if __name__ == "__main__":
    main()
