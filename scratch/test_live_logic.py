"""
scratch/test_live_logic.py — Unit test for live two-phase detection logic
using mock synthetic packet streams.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
import time
import pandas as pd
import numpy as np

from WiresharkAbnormality import (
    PACKET_COLUMNS,
    WINDOW_FEATURE_COLS,
    calibrate_baseline,
    score_monitoring_window,
    run_live_detection,
    _format_permission_error,
)

print("=== [1] Testing Baseline Calibration (Phase 1) ===")
# Generate synthetic baseline traffic with natural variance (15 normal hosts, web/DNS traffic)
np.random.seed(42)
normal_packets = []
for host_id in range(1, 16):
    src = f"192.168.1.{host_id}"
    num_pkts = int(np.random.randint(10, 30))
    for _ in range(num_pkts):
        dst_p = str(np.random.choice(["80", "443", "53"]))
        normal_packets.append([
            "TCP", int(np.random.randint(100, 1400)), src, "8.8.8.8", "50000", dst_p,
            float(np.random.uniform(0, 10)), False, False, False
        ])

df_normal = pd.DataFrame(normal_packets, columns=PACKET_COLUMNS)
scaler, model, calib_windows = calibrate_baseline(df_normal, window_size=5)

assert scaler is not None, "Scaler must not be None"
assert model is not None, "Model must not be None"
assert len(calib_windows) > 0, f"Expected windows > 0, got {len(calib_windows)}"
print(f"    Calibrated on {len(df_normal)} packets across {len(calib_windows)} windows. [OK]")

print("\n=== [2] Testing Phase 2 Scoring Against Calibrated Baseline ===")
# Normal monitoring window
df_mon_normal = df_normal.iloc[:30].copy()
score_normal = score_monitoring_window(df_mon_normal, scaler, model, window_size=5)
normal_anomalies = score_normal[score_normal["Anomaly"] == -1]
print(f"    Normal window evaluated: {len(score_normal)} sources, anomalies: {len(normal_anomalies)}")

# Attack monitoring window: SYN Port Scan (300 packets, 300 distinct ports)
scan_packets = []
for p in range(1000, 1300):
    scan_packets.append([
        "TCP", 60, "10.0.0.99", "192.168.1.1", "40000", str(p),
        100.0, False, False, True
    ])
df_scan = pd.DataFrame(scan_packets, columns=PACKET_COLUMNS)
score_scan = score_monitoring_window(df_scan, scaler, model, window_size=5)
scan_flagged = score_scan[score_scan["Anomaly_Type"] == "Port Scan"]

assert len(scan_flagged) > 0, f"Port scan should be flagged as 'Port Scan', got: {score_scan.to_dict('records')}"
print(f"    Port scan flagged successfully: {scan_flagged[['Src_Address', 'Anomaly_Type', 'unique_dst_ports']].to_dict('records')} [OK]")

# Attack monitoring window: Flood / DDoS (500 packets to port 80)
flood_packets = []
for _ in range(500):
    flood_packets.append([
        "TCP", 64, "10.0.0.88", "192.168.1.1", "40000", "80",
        105.0, False, False, False
    ])
df_flood = pd.DataFrame(flood_packets, columns=PACKET_COLUMNS)
score_flood = score_monitoring_window(df_flood, scaler, model, window_size=5)
flood_flagged = score_flood[score_flood["Anomaly_Type"] == "Flood / DDoS"]
assert len(flood_flagged) > 0, "Flood should be flagged as 'Flood / DDoS'"
print(f"    Flood / DDoS flagged successfully: {flood_flagged[['Src_Address', 'Anomaly_Type', 'packet_count']].to_dict('records')} [OK]")

print("\n=== [3] Testing run_live_detection end-to-end with mock packet source ===")
# Mock packet generator function that serves normal traffic during calibration, then attack
stream_step = {"count": 0}
def mock_packet_source(interface=None, timeout=1):
    stream_step["count"] += 1
    if stream_step["count"] <= 3:
        # Phase 1 traffic: normal packets
        return df_normal.iloc[:20].copy()
    else:
        # Phase 2 traffic: port scan packets
        return df_scan.copy()

stop_evt = threading.Event()
events_received = []

def live_callback(phase, data):
    events_received.append((phase, data))
    if phase == "phase2_window":
        # Stop after receiving one monitored window
        stop_evt.set()

run_live_detection(
    interface=None,
    calibration_duration=2,  # fast 2s calibration for test
    window_size=1,
    callback=live_callback,
    stop_event=stop_evt,
    packet_source=mock_packet_source,
)

phase_names = [e[0] for e in events_received]
assert "phase1_progress" in phase_names, "Should receive phase1_progress events"
assert "phase1_complete" in phase_names, "Should receive phase1_complete event"
assert "phase2_window" in phase_names, "Should receive phase2_window event"
print("    run_live_detection executed Phase 1 -> Phase 2 smoothly. [OK]")

print("\n=== [4] Testing Permission Error Formatting ===")
err_text = _format_permission_error("eth0", "Access is denied")
assert "LIVE CAPTURE PERMISSION" in err_text
assert "Npcap" in err_text
assert "sudo" in err_text
print("    Permission error message includes Npcap and sudo instructions. [OK]")

print("\n" + "="*50)
print("ALL LIVE LOGIC UNIT TESTS PASSED [OK]")
print("="*50)
