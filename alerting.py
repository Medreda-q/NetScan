"""
NetScan — Alerting & SIEM Integration Module
DUT Cybersecurity Stage d'Initiation (Septembre 2026)
Author: Mohamed Reda QIYAOUI

Provides real-time webhook notifications (Discord / Slack) with rich embeds.
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    """Load persistent configuration (webhook URLs)."""
    default_config = {
        "discord_webhook_url": "",
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_config.update(data)
        except Exception:
            pass
    return default_config


def save_config(config_dict):
    """Save persistent configuration to JSON file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2)
        return True
    except Exception:
        return False


def send_discord_alert(webhook_url, alert_data):
    """
    Send a rich Discord embed alert for detected network threats.

    Parameters
    ----------
    webhook_url : str — Discord Webhook URL
    alert_data  : dict — Dictionary containing:
        - anomaly_type : str ('Port Scan', 'Flood / DDoS', 'Packet Anomaly')
        - src_ip       : str (Attacker IP)
        - packet_count : int
        - unique_ports : int
        - window_time  : str / float

    Returns
    -------
    tuple (success: bool, message: str)
    """
    if not webhook_url or not webhook_url.strip().startswith("http"):
        return False, "Invalid or missing webhook URL."

    anomaly_type = alert_data.get("anomaly_type", "Network Anomaly")
    src_ip = alert_data.get("src_ip", "Unknown")
    packet_count = alert_data.get("packet_count", 0)
    unique_ports = alert_data.get("unique_ports", 0)
    window_time = alert_data.get("window_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Color coding for Discord embeds: Red = Port Scan / Flood, Amber = Anomaly
    if "Port Scan" in anomaly_type:
        color = 15158332  # Red
        title_emoji = "🚨"
        severity = "HIGH (Reconnaissance Attack)"
    elif "Flood" in anomaly_type or "DDoS" in anomaly_type:
        color = 16711680  # Bright Red
        title_emoji = "💥"
        severity = "CRITICAL (Volumetric Denial of Service)"
    else:
        color = 16753920  # Orange / Amber
        title_emoji = "⚠️"
        severity = "MEDIUM (Statistical Outlier)"

    embed = {
        "title": f"{title_emoji} NetScan NIDS Alert — {anomaly_type}",
        "description": "Une activité réseau anormale a été interceptée par le moteur d'apprentissage non supervisé Isolation Forest.",
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": "NetScan NIDS Platform | Mohamed Reda QIYAOUI",
        },

        "fields": [
            {
                "name": "🌐 Adresse Source (Attaquant)",
                "value": f"`{src_ip}`",
                "inline": True,
            },
            {
                "name": "🎯 Ports Uniques Ciblés",
                "value": f"`{unique_ports}` port(s)",
                "inline": True,
            },
            {
                "name": "📦 Volume de Paquets",
                "value": f"`{packet_count}` paquets",
                "inline": True,
            },
            {
                "name": "⚡ Sévérité",
                "value": severity,
                "inline": True,
            },
            {
                "name": "🕒 Horodatage",
                "value": str(window_time),
                "inline": True,
            },
            {
                "name": "📊 Modèle IA",
                "value": "Isolation Forest (Layer 2 Macroscopic)",
                "inline": True,
            },
        ],
    }

    payload = {
        "username": "NetScan Security Bot",
        "avatar_url": "https://raw.githubusercontent.com/feathericons/feather/master/icons/shield.png",
        "embeds": [embed],
    }

    try:
        req = urllib.request.Request(
            webhook_url.strip(),
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "NetScan-Alerting/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status in (200, 204):
                return True, "Alert sent successfully to Discord."
            return False, f"Discord returned HTTP status {response.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP Error {e.code}: {e.reason}"
    except Exception as e:
        return False, f"Connection error: {e}"


def test_discord_webhook(webhook_url):
    """Send a test embed to confirm the Discord webhook URL is working."""
    test_data = {
        "anomaly_type": "Test Connectivity / Diagnostic Alert",
        "src_ip": "192.168.1.100 (Test Host)",
        "packet_count": 42,
        "unique_ports": 15,
        "window_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "blocked": False,
    }
    return send_discord_alert(webhook_url, test_data)
