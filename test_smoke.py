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

# 200 normal host windows (low packet count, low port diversity)
# Contamination=0.02 needs >=100 rows to guarantee even 2 flagged slots.
# Using 200 rows gives 4 anomaly slots -> both attack rows reliably flagged.
np.random.seed(0)
for i in range(200):
    rows.append({
        "Src_Address": f"10.0.{i // 256}.{i % 256 + 1}",
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

# Flood source: 500 packets, only 2 unique ports, large frames (CDN amplification)
rows.append({
    "Src_Address": "10.99.99.99",
    "time_window": 0.0,
    "packet_count": 500,
    "avg_packet_length": 1058.0,  # Near-MTU frames = volumetric amplification
    "unique_dst_ports": 1,
    "unique_dst_ips": 1,
    "syn_count": 0,
})

# Normal web download: high packet count, small frames, no SYN — should NOT be flagged
rows.append({
    "Src_Address": "192.168.1.106",
    "time_window": 0.0,
    "packet_count": 700,
    "avg_packet_length": 72.0,  # Small ACK/data frames typical of TCP streaming
    "unique_dst_ports": 2,
    "unique_dst_ips": 3,
    "syn_count": 0,
})

window_df = pd.DataFrame(rows)
result = detect_window_anomalies(window_df)

scanner_label   = result.loc[result["Src_Address"] == "192.168.1.100", "Anomaly_Type"].values[0]
flood_label     = result.loc[result["Src_Address"] == "10.99.99.99",   "Anomaly_Type"].values[0]
normal_label    = result.loc[result["Src_Address"] == "192.168.1.106", "Anomaly_Type"].values[0]

print(f"    Scanner (500 pkts, 500 ports)           -> label: '{scanner_label}'  (expected: Port Scan)")
print(f"    Flood   (500 pkts, 1 port, 1058B frames) -> label: '{flood_label}'  (expected: Flood / DDoS)")
print(f"    Normal  (700 pkts, 2 ports, 72B, syn=0)  -> label: '{normal_label}'  (expected: Normal)")

assert scanner_label == "Port Scan",    f"FAIL: scanner labeled '{scanner_label}', expected 'Port Scan'"
assert flood_label   == "Flood / DDoS", f"FAIL: flood labeled '{flood_label}', expected 'Flood / DDoS'"
assert normal_label  == "Normal",       f"FAIL: normal web traffic falsely labeled '{normal_label}', expected 'Normal'"
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

# ── 5. Audit Logging & Security Event Management test ────────────────────────
print("\n[5] Testing Security Audit Logging & Firewall Rule generation...")
from alerting import log_security_event, load_security_events, generate_firewall_rule
from detection_engine import add_alert, load_alerts
import tempfile
import os

test_evt = {
    "anomaly_type": "Port Scan",
    "src_ip": "192.168.1.45",
    "packet_count": 350,
    "unique_ports": 340,
    "severity": "CRITICAL",
}
ok, msg = log_security_event(test_evt)
assert ok, "Audit logging should succeed"

# Firewall rule IP validation checks
rule = generate_firewall_rule("192.168.1.45")
assert "192.168.1.45" in rule, "Firewall rule must contain target IP"
assert "netsh" in rule or "iptables" in rule, "Valid IPv4 must generate firewall rule command"
print(f"    Firewall rule generated: {rule[:45]}...  [OK]")

for invalid_src in ["aa:bb:cc:dd:ee:ff", "abc; rm -rf /", ""]:
    rule_invalid = generate_firewall_rule(invalid_src)
    assert rule_invalid.startswith("#"), f"Expected comment '#' for invalid input '{invalid_src}', got: {rule_invalid}"
    assert "iptables" not in rule_invalid and "netsh" not in rule_invalid, f"Invalid input '{invalid_src}' generated firewall command: {rule_invalid}"
print("    Firewall rule invalid/non-IP rejection [OK]")

# Test unified Step 2 API: round-trip write/read and deduplication using a temporary file
with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_audit:
    tmp_audit_path = tmp_audit.name

try:
    if os.path.exists(tmp_audit_path):
        os.remove(tmp_audit_path)

    evt1 = {
        "src_address": "10.10.10.50",
        "anomaly_type": "Port Scan",
        "time_window": 10.0,
        "packet_count": 100,
        "unique_dst_ports": 90,
    }
    evt2 = {
        "src_address": "10.10.10.50",
        "anomaly_type": "Port Scan",
        "time_window": 10.0,
        "packet_count": 105,
        "unique_dst_ports": 95,
    }

    ok1, _ = log_security_event(evt1, filepath=tmp_audit_path)
    assert ok1, "First event logging should succeed"
    ok2, _ = log_security_event(evt2, filepath=tmp_audit_path)
    assert ok2, "Second event logging should succeed or report dedup"

    loaded = load_security_events(tmp_audit_path)
    assert len(loaded) == 1, f"Expected 1 deduped entry, got {len(loaded)}"
    assert loaded[0]["src_address"] == "10.10.10.50"
    assert loaded[0]["time_window"] == 10.0
    assert "firewall_rule" in loaded[0]

    # Verify delegation via detection_engine functions
    add_alert(evt2, filepath=tmp_audit_path)
    alerts_delegated = load_alerts(filepath=tmp_audit_path)
    assert len(alerts_delegated) == 1, f"Expected 1 deduped entry via add_alert, got {len(alerts_delegated)}"
finally:
    if os.path.exists(tmp_audit_path):
        os.remove(tmp_audit_path)

print("    Security audit logging persistence & deduplication [OK]")

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
assert "header-logo" in report_html, "Official NetScan logo branding missing from report"
print("    Executive HTML/PDF report generated correctly with logo  [OK]")

# ── 7. Official NetScan Logo & Branding Assets test ───────────────────────────
print("\n[7] Verifying NetScan Official Brand Logo & Assets...")
import os
from PIL import Image

logo_svg = os.path.join("assets", "netscan_logo.svg")
logo_png = os.path.join("assets", "netscan_logo.png")
logo_ico = os.path.join("assets", "netscan_logo.ico")

assert os.path.exists(logo_svg), "Official SVG logo missing: assets/netscan_logo.svg"
assert os.path.getsize(logo_svg) > 500, "SVG logo file is empty or truncated"

assert os.path.exists(logo_png), "Raster PNG logo missing: assets/netscan_logo.png"
with Image.open(logo_png) as img:
    assert img.size[0] >= 128 and img.size[1] >= 128, f"PNG logo resolution too low: {img.size}"

assert os.path.exists(logo_ico), "Icon file missing: assets/netscan_logo.ico"
print("    assets/netscan_logo.svg, .png, .ico validated  [OK]")

print("\n" + "="*55)
print("ALL SMOKE TESTS PASSED [OK]")
print("="*55)

