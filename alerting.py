"""
NetScan — Security Audit Logging & Incident Management Module
Author: Mohamed Reda QIYAOUI

Provides persistent local audit logging for all detected intrusion attempts
(Port Scans, SYN Floods, Anomalies) and generates defensive firewall rules.
"""

import ipaddress
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


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
    Validates that src_ip is a legitimate IPv4/IPv6 address before creating commands.
    """
    if not src_ip or src_ip in ("Unknown", "127.0.0.1", "localhost"):
        return "# IP non spécifiée"

    clean_ip = str(src_ip).split()[0].strip()
    if clean_ip in ("", "Unknown", "127.0.0.1", "localhost"):
        return "# IP non spécifiée"

    try:
        ip_obj = ipaddress.ip_address(clean_ip)
    except ValueError:
        return "# Adresse non valide ou non-IP: aucune règle générée"

    if ip_obj.is_loopback:
        return "# IP non spécifiée"

    valid_ip_str = str(ip_obj)
    if os_type == "windows" or os.name == "nt":
        return f'netsh advfirewall firewall add rule name="NetScan-Block-{valid_ip_str}" dir=in action=block remoteip={valid_ip_str}'
    else:
        return f'iptables -A INPUT -s {valid_ip_str} -j DROP'


def log_security_event(alert_data, filepath=None):
    """
    Persistently logs a security incident into the unified audit trail.
    Enforces unified superset schema and deduplication.
    """
    target_path = filepath or AUDIT_LOG_FILE
    events = load_security_events(target_path)

    timestamp = alert_data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    src_address = alert_data.get("src_address") or alert_data.get("src_ip", "Inconnue")
    anomaly_type = alert_data.get("anomaly_type", "Anomalie Réseau")
    packet_count = int(alert_data.get("packet_count", 0))
    unique_dst_ports = int(alert_data.get("unique_dst_ports") or alert_data.get("unique_ports", 0))
    unique_dst_ips = int(alert_data.get("unique_dst_ips", 0))
    syn_count = int(alert_data.get("syn_count", 0))
    avg_packet_length = float(alert_data.get("avg_packet_length", 0.0))
    time_window = alert_data.get("time_window")
    if time_window is not None:
        try:
            time_window = float(time_window)
        except (ValueError, TypeError):
            time_window = None

    severity = alert_data.get("severity", "HIGH")
    origin = alert_data.get("origin", "Live Surveillance")
    description = alert_data.get("description", "")
    recommendation = alert_data.get("recommendation", "")
    firewall_rule = alert_data.get("firewall_rule") or generate_firewall_rule(src_address)
    alert_id = alert_data.get("id") or f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

    record = {
        "id": alert_id,
        "timestamp": timestamp,
        "anomaly_type": anomaly_type,
        "src_address": src_address,
        "packet_count": packet_count,
        "unique_dst_ports": unique_dst_ports,
        "unique_dst_ips": unique_dst_ips,
        "syn_count": syn_count,
        "avg_packet_length": round(avg_packet_length, 1),
        "time_window": time_window,
        "severity": severity,
        "origin": origin,
        "description": description,
        "recommendation": recommendation,
        "firewall_rule": firewall_rule,
    }

    # Deduplication rule
    for ev in events:
        if ev.get("src_address") == record["src_address"] and ev.get("anomaly_type") == record["anomaly_type"]:
            if record["time_window"] is not None and ev.get("time_window") == record["time_window"]:
                return True, "Événement déjà consigné dans le journal."
            if record["timestamp"] is not None and ev.get("timestamp") == record["timestamp"]:
                return True, "Événement déjà consigné dans le journal."

    events.insert(0, record)
    events = events[:1000]  # Cap at 1000 entries

    ok = save_security_events(events, target_path)
    if ok:
        logger.info("Alert logged: type=%s src=%s id=%s", anomaly_type, src_address, alert_id)
        return True, "Événement consigné dans le journal d'audit local."
    else:
        logger.error("Failed to write alert to %s", target_path)
        return False, "Erreur d'écriture du journal d'audit."


def save_security_events(events, filepath=None):
    """Save security events list to JSON file atomically."""
    target_path = filepath or AUDIT_LOG_FILE
    try:
        tmp_file = f"{target_path}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(events[:1000], f, indent=2, ensure_ascii=False)
        if os.path.exists(target_path):
            os.replace(tmp_file, target_path)
        else:
            os.rename(tmp_file, target_path)
        logger.debug("Audit log saved: %d events → %s", len(events), target_path)
        return True
    except Exception:
        return False


def load_security_events(filepath=None):
    """
    Loads all recorded security incidents from the local audit log.
    Tolerant of older schemas by defaulting missing fields.
    """
    target_path = filepath or AUDIT_LOG_FILE
    if not os.path.exists(target_path):
        return []
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                normalized = []
                for entry in data:
                    if isinstance(entry, dict):
                        item = {
                            "id": entry.get("id", ""),
                            "timestamp": entry.get("timestamp", ""),
                            "anomaly_type": entry.get("anomaly_type", "Anomalie Réseau"),
                            "src_address": entry.get("src_address") or entry.get("src_ip", "Inconnue"),
                            "packet_count": int(entry.get("packet_count", 0)),
                            "unique_dst_ports": int(entry.get("unique_dst_ports") or entry.get("unique_ports", 0)),
                            "unique_dst_ips": int(entry.get("unique_dst_ips", 0)),
                            "syn_count": int(entry.get("syn_count", 0)),
                            "avg_packet_length": float(entry.get("avg_packet_length", 0.0)),
                            "time_window": entry.get("time_window"),
                            "severity": entry.get("severity", "HIGH"),
                            "origin": entry.get("origin", "Live Surveillance"),
                            "description": entry.get("description", ""),
                            "recommendation": entry.get("recommendation", ""),
                            "firewall_rule": entry.get("firewall_rule") or generate_firewall_rule(entry.get("src_address") or entry.get("src_ip", "")),
                        }
                        normalized.append(item)
                return normalized
            return []
    except Exception:
        return []


def clear_security_events(filepath=None):
    """
    Clears historical audit trail.
    """
    target_path = filepath or AUDIT_LOG_FILE
    try:
        if os.path.exists(target_path):
            os.remove(target_path)
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
