"""
test_smoke.py — Verifies imports and detection logic without needing a .pcap file.
Author: Mohamed Reda QIYAOUI
Run with: python test_smoke.py
"""
import sys
print("Python:", sys.version)

# ── 1. Import check ───────────────────────────────────────────────────────────
print("\n[1] Checking imports...")
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import streamlit  # just import, don't run
print("    pandas, matplotlib, scikit-learn, streamlit  [OK]")

import pyshark
print("    pyshark  [OK]")

# ── 2. Import our own modules ─────────────────────────────────────────────────
print("\n[2] Importing detection_engine functions...")
from detection_engine import (
    aggregate_windows,
    detect_window_anomalies,
)
print("    aggregate_windows, detect_window_anomalies  [OK]")

# ── 3. Detection logic test on synthetic data ─────────────────────────────────
print("\n[3] Running detection logic test on synthetic data...")
import numpy as np

rows = []

# 30 normal host windows (low packet count, low port diversity)
for i in range(30):
    rows.append({
        "Src_Address": f"10.0.0.{i+1}",
        "time_window": 0.0,
        "packet_count": int(np.random.randint(5, 20)),
        "avg_packet_length": float(np.random.uniform(200, 800)),
        "unique_dst_ports": int(np.random.randint(1, 4)),
        "unique_dst_ips": int(np.random.randint(1, 3)),
        "syn_count": int(np.random.randint(0, 2)),
    })

# nmap-like port scanner: 500 packets, 500 unique ports, ratio = 1.0
rows.append({
    "Src_Address": "192.168.1.100",
    "time_window": 0.0,
    "packet_count": 500,
    "avg_packet_length": 60.0,
    "unique_dst_ports": 500,
    "unique_dst_ips": 1,
    "syn_count": 500,
})

# Flood source: 800 packets, only 2 unique ports, ratio = 0.0025
rows.append({
    "Src_Address": "10.99.99.99",
    "time_window": 0.0,
    "packet_count": 800,
    "avg_packet_length": 64.0,
    "unique_dst_ports": 2,
    "unique_dst_ips": 1,
    "syn_count": 0,
})

window_df = pd.DataFrame(rows)
result = detect_window_anomalies(window_df)

scanner_label = result.loc[result["Src_Address"] == "192.168.1.100", "Anomaly_Type"].values[0]
flood_label   = result.loc[result["Src_Address"] == "10.99.99.99",   "Anomaly_Type"].values[0]

print(f"    Scanner (500 pkts, 500 ports) -> label: '{scanner_label}'  (expected: Port Scan)")
print(f"    Flood   (800 pkts, 2 ports)   -> label: '{flood_label}'  (expected: Flood / DDoS)")

assert scanner_label == "Port Scan",    f"FAIL: scanner labeled '{scanner_label}', expected 'Port Scan'"
assert flood_label   == "Flood / DDoS", f"FAIL: flood labeled '{flood_label}', expected 'Flood / DDoS'"
print("    Detection labels  [OK]")

# ── 4. aggregate_windows logic test ───────────────────────────────────────────
print("\n[4] Testing aggregate_windows() on a synthetic per-packet DataFrame...")

# Build a mock per-packet DataFrame (same schema as extract_features output)
mock_packets = pd.DataFrame({
    "Protocol":    ["TCP"] * 10,
    "Length":      [60] * 10,
    "Src_Address": ["192.168.1.1"] * 10,
    "Dst_Address": ["10.0.0.1"] * 10,
    "Src_Port":    ["54321"] * 10,
    "Dst_Port":    [str(p) for p in range(80, 90)],  # 10 unique dst ports
    "Timestamp":   [float(i) for i in range(10)],    # 10 seconds span
    "Retransmission": [False] * 10,
    "Reset_Flag":     [False] * 10,
    "SYN_Flag":       [True]  * 10,
})

agg = aggregate_windows(mock_packets, window_size=5)
print(f"    Input: 10 packets over 10s, window_size=5 -> {len(agg)} window(s) expected: 2")
assert len(agg) == 2, f"Expected 2 windows, got {len(agg)}"

win0 = agg[agg["time_window"] == 0.0].iloc[0]
assert win0["unique_dst_ports"] == 5, f"Window 0 should have 5 unique ports, got {win0['unique_dst_ports']}"
assert win0["syn_count"]        == 5, f"Window 0 should have 5 SYN packets, got {win0['syn_count']}"
print(f"    Window 0: {win0['unique_dst_ports']} unique ports, {win0['syn_count']} SYN pkts  [OK]")
print("    aggregate_windows()  [OK]")

# ── 5. Alerting & Discord Webhook logic test ──────────────────────────────────
print("\n[5] Testing Alerting & Discord webhook payload logic...")
from alerting import send_discord_alert, load_config, save_config

# Test invalid/empty webhook safety
ok, msg = send_discord_alert("", {"anomaly_type": "Test"})
assert not ok, "Empty webhook should safely return False"
print("    Empty/invalid webhook safety handling  [OK]")

# Test config load/save
cfg = load_config()
assert isinstance(cfg, dict), "load_config should return a dict"
print("    Alerting config persistence  [OK]")

# ── 6. Executive Incident Report Generator test ───────────────────────────────
print("\n[6] Testing Executive Incident Report Generator (HTML/PDF)...")
from report_generator import generate_html_incident_report

test_stats = {
    "total_packets": 1250,
    "total_windows": 10,
    "port_scan_count": 2,
    "flood_count": 1,
    "packet_anomaly_count": 15,
    "source_target": "Unit Test Suite",
}
test_anom = [
    {"Src_Address": "192.168.1.50", "Anomaly_Type": "Port Scan", "packet_count": 500, "unique_dst_ports": 490, "time_window": 0.0}
]

report_html = generate_html_incident_report(
    session_stats=test_stats,
    anomalous_windows=test_anom,
)

assert "<!DOCTYPE html>" in report_html, "Report must be valid HTML5"
assert "Rapport d'Incident & d'Analyse Forensic" in report_html, "Report header missing"
assert "192.168.1.50" in report_html, "Attacker IP missing from report"
assert "Port Scan" in report_html, "Attack vector missing from report"
assert "@media print" in report_html, "Print CSS stylesheet missing"
print("    Executive HTML/PDF report generated correctly  [OK]")

print("\n" + "="*55)
print("ALL SMOKE TESTS PASSED [OK]")
print("="*55)

