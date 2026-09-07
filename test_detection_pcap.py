"""
test_detection_pcap.py — End-to-end verification on sample_nmap_attack.pcap
Author: Mohamed Reda QIYAOUI
Run with: python test_detection_pcap.py
"""
import os
import sys
import time

from detection_engine import (
    extract_features,
    detect_anomalies,
    aggregate_windows,
    detect_window_anomalies,
)

pcap_file = "sample_nmap_attack.pcap" if os.path.exists("sample_nmap_attack.pcap") else "NMAP_PROBE.pcap"
if not os.path.exists(pcap_file):
    print(f"Error: {pcap_file} not found!")
    sys.exit(1)

print(f"=== [1] Extracting features from {pcap_file} ===")
start = time.time()
df_packets = extract_features(pcap_file)
elapsed_extract = time.time() - start
print(f"Extracted {len(df_packets)} packets in {elapsed_extract:.2f}s.")

print("\n=== [2] Layer 1 Detection (Per-Packet) ===")
df_packets = detect_anomalies(df_packets)
pkt_anomalies = (df_packets["Anomaly"] == -1).sum()
print(f"Layer 1 Anomalies flagged: {pkt_anomalies} / {len(df_packets)}")
print("Layer 1 Anomaly types breakdown:")
print(df_packets[df_packets["Anomaly"] == -1]["Anomaly_Type"].value_counts().to_string())

print("\n=== [3] Layer 2 Detection (Per-Window: 5s) ===")
start = time.time()
df_windows = aggregate_windows(df_packets, window_size=5)
df_windows = detect_window_anomalies(df_windows)
elapsed_win = time.time() - start
print(f"Aggregated and detected {len(df_windows)} windows in {elapsed_win:.4f}s.")

port_scans = (df_windows["Anomaly_Type"] == "Port Scan").sum()
floods = (df_windows["Anomaly_Type"] == "Flood / DDoS").sum()
normal_wins = (df_windows["Anomaly_Type"] == "Normal").sum()

print("\nLayer 2 Anomaly types breakdown:")
print(df_windows["Anomaly_Type"].value_counts().to_string())

print("\n=== [4] Flagged Sources in Windows ===")
flagged = df_windows[df_windows["Anomaly"] == -1]
print(flagged[["Src_Address", "time_window", "packet_count", "unique_dst_ports", "syn_count", "Anomaly_Type"]].head(20).to_string(index=False))

print("\n" + "="*50)
print(f"Port Scans detected: {port_scans}")
print(f"Flood/DDoS detected: {floods}")
print("="*50)

if port_scans > 0:
    print("\n[SUCCESS] The port scan in NMAP_PROBE.pcap was successfully detected by Layer 2!")
else:
    print("\n[WARNING] No port scans detected.")
