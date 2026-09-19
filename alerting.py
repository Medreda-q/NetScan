"""
NetScan — Security Audit Logging & Incident Management Module
Author: Mohamed Reda QIYAOUI

Provides persistent local audit logging for all detected intrusion attempts
(Port Scans, SYN Floods, Anomalies) and generates defensive firewall rules.
"""

import json
import os
import sys
from datetime import datetime

AUDIT_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alerts_history.json")
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    """Load persistent configuration."""
    default_config = {
        "log_file": "alerts_history.json",
        "auto_firewall_rule": True,
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


def generate_firewall_rule(src_ip, os_type="windows"):
    """
    Generate an immediate kernel firewall blocking command for an offending IP.
    """
    if not src_ip or src_ip in ("Unknown", "127.0.0.1", "localhost"):
        return "# IP non spécifiée"
    
    clean_ip = src_ip.split()[0].strip()
    if os_type == "windows" or os.name == "nt":
        return f'netsh advfirewall firewall add rule name="NetScan-Block-{clean_ip}" dir=in action=block remoteip={clean_ip}'
    else:
        return f'iptables -A INPUT -s {clean_ip} -j DROP'


def log_security_event(alert_data, filepath=AUDIT_LOG_FILE):
    """
    Persistently logs a security incident into the local audit trail.
    """
    events = load_security_events(filepath)
    
    timestamp = alert_data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {
        "timestamp": timestamp,
        "anomaly_type": alert_data.get("anomaly_type", "Anomalie Réseau"),
        "src_address": alert_data.get("src_ip") or alert_data.get("src_address", "Inconnue"),
        "packet_count": int(alert_data.get("packet_count", 0)),
        "unique_dst_ports": int(alert_data.get("unique_ports") or alert_data.get("unique_dst_ports", 0)),
        "severity": alert_data.get("severity", "HIGH"),
        "firewall_rule": generate_firewall_rule(alert_data.get("src_ip") or alert_data.get("src_address", "")),
    }

    # Avoid immediate exact duplicates within the same second
    for ev in events[:10]:
        if (ev.get("src_address") == record["src_address"] and
            ev.get("anomaly_type") == record["anomaly_type"] and
            ev.get("timestamp") == record["timestamp"]):
            return True, "Événement déjà consigné dans le journal."

    events.insert(0, record)
    events = events[:1000]  # Cap at 1000 entries
    
    try:
        tmp_file = f"{filepath}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        if os.path.exists(filepath):
            os.replace(tmp_file, filepath)
        else:
            os.rename(tmp_file, filepath)
        return True, "Événement consigné dans le journal d'audit local."
    except Exception as e:
        return False, f"Erreur d'écriture du journal d'audit: {e}"


def load_security_events(filepath=AUDIT_LOG_FILE):
    """
    Loads all recorded security incidents from the local audit log.
    """
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []


def clear_security_events(filepath=AUDIT_LOG_FILE):
    """
    Clears historical audit trail.
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        return True
    except Exception:
        return False


# ── Backward-compatible stubs ────────────────────────────────────────────────
def send_discord_alert(webhook_url, alert_data):
    """
    Maintained for backwards-compatibility: logs the incident locally into the audit log.
    """
    if not webhook_url:
        return False, "Discord désactivé: les alertes sont consignées dans le journal d'audit local."
    ok, msg = log_security_event(alert_data)
    return ok, "Alerte consignée dans le journal d'audit local (mode local)."


def test_discord_webhook(webhook_url):
    """Stub testing audit logging."""
    test_data = {
        "anomaly_type": "Test Incident / Diagnostic",
        "src_ip": "192.168.1.100",
        "packet_count": 42,
        "unique_ports": 15,
        "severity": "MEDIUM",
    }
    return log_security_event(test_data)
