"""
detection_engine.py — Network Traffic Anomaly Detector & IPS Engine
====================================================================
Author: Mohamed Reda QIYAOUI
DUT Cybersecurity — Stage d'Initiation (Septembre 2026)
École Supérieure de Technologie (EST)

ARCHITECTURE OVERVIEW
---------------------
This project implements three complementary anomaly detection components:

  Layer 1 — Per-Packet (offline & forensic):
      Features  : packet Length + Timestamp
      Model     : Isolation Forest (contamination=0.05)
      Detects   : individual packets that are unusual in size or timing
                  (retransmissions, resets, oversized frames, etc.)
      Limitation: evaluates packets independently — cannot detect patterns
                  that only emerge across many packets from the same source.

  Layer 2 — Per-Window / Behavioral (offline & forensic):
      Features  : 5 aggregate statistics per (source IP, time window) group
      Model     : Isolation Forest (contamination=0.10)
      Detects   : port scans, SYN floods, host sweeps — attacks that are
                  invisible at the per-packet level but obvious in aggregate.

  Live Calibrate-Then-Monitor (real-time stream analysis):
      Phase 1   : Live Calibration (default: 120s)
                  Captures live interface traffic to learn the normal behavioral
                  baseline for the specific network session. Fits and retains
                  StandardScaler and IsolationForest (contamination=0.10).
      Phase 2   : Continuous Monitoring (every N seconds, default: 5s)
                  Streams live windows, extracts the 5 behavioral features,
                  scores them against the Phase 1 calibrated baseline, and flags
                  port scans and floods in real-time. Report/alert only — no
                  traffic disruption or automated blocking.

WHY MULTI-TIER DETECTION?
-------------------------
A classic nmap port scan sends a small SYN packet to each target port.
Each individual packet is completely normal in length and timing — Layer 1
will never flag it. Zooming out to aggregate behavior (Layer 2) reveals
that one source contacted hundreds or thousands of distinct destination ports.
The Live mode operationalizes this capability in real time, adapting to
each environment's baseline traffic before initiating continuous surveillance.

AUTHOR & COPYRIGHT
------------------
Author: Mohamed Reda QIYAOUI
DUT Cybersecurity — Stage d'Initiation, Septembre 2026
Copyright (c) 2026 Mohamed Reda QIYAOUI. All rights reserved.

DEPENDENCIES
------------
  pip install pyshark scapy pandas matplotlib scikit-learn streamlit
"""

import asyncio
import datetime
import json
import os
import sys
import time
import uuid

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pyshark

# ──────────────────────────────────────────────────────────────────────────────
# WINDOWS ASYNCIO COMPATIBILITY FIX
# ──────────────────────────────────────────────────────────────────────────────
# pyshark uses asyncio internally to communicate with tshark (the Wireshark
# command-line backend). On Windows, Python 3.8+ defaults to ProactorEventLoop,
# which is incompatible with pyshark's subprocess management.
# Switching to SelectorEventLoop resolves "Event loop is closed" errors on
# Windows without affecting functionality on Linux/macOS.
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def _ensure_asyncio_loop():
    """Ensure an active, open asyncio event loop is registered in the current thread."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    _orig_all_tasks = getattr(asyncio, "all_tasks", None)
    if _orig_all_tasks is not None:
        def _safe_all_tasks(l=None):
            try:
                if l is None:
                    try:
                        l = asyncio.get_running_loop()
                    except RuntimeError:
                        l = asyncio.get_event_loop()
                return _orig_all_tasks(l)
            except Exception:
                return set()
        asyncio.all_tasks = _safe_all_tasks
    return loop


_ensure_asyncio_loop()

# Canonical column names for extracted packet DataFrames
PACKET_COLUMNS = [
    "Protocol", "Length", "Src_Address", "Dst_Address",
    "Src_Port", "Dst_Port", "Timestamp",
    "Retransmission", "Reset_Flag", "SYN_Flag",
]

# Canonical feature names for Layer 2 windowed behavioral analysis
WINDOW_FEATURE_COLS = [
    "packet_count",
    "avg_packet_length",
    "unique_dst_ports",
    "unique_dst_ips",
    "syn_count",
]


# ==============================================================================
# SECTION 1 — PACKET PARSING HELPERS (shared between file and live capture)
# ==============================================================================

def _parse_pyshark_packet(packet):
    """
    Extract features from a single PyShark packet object.

    Handles Layer 2 filtering (STP, ARP, CDP), field extraction, and an
    independent MAC address fallback edge-case fix.

    Returns
    -------
    list or None : 10 extracted fields matching PACKET_COLUMNS, or None if skipped.
    """
    try:
        protocol = packet.highest_layer

        # Skip specific Layer 2 protocols — these carry no IP-level
        # behavioral signal useful for our detection models.
        if protocol in ["STP", "ARP", "CDP"]:
            return None

        length = int(packet.length)
        src_ip = packet.ip.src if hasattr(packet, "ip") else "N/A"
        dst_ip = packet.ip.dst if hasattr(packet, "ip") else "N/A"
        src_port = packet.tcp.srcport if hasattr(packet, "tcp") else (
            packet.udp.srcport if hasattr(packet, "udp") else "N/A"
        )
        dst_port = packet.tcp.dstport if hasattr(packet, "tcp") else (
            packet.udp.dstport if hasattr(packet, "udp") else "N/A"
        )
        timestamp = float(packet.sniff_timestamp)

        # Check for TCP retransmissions and reset flags
        retransmission = False
        reset_flag = False
        syn_flag = False

        if hasattr(packet, "tcp"):
            retransmission = hasattr(packet.tcp, "analysis_retransmission")
            reset_flag = (
                packet.tcp.flags_reset == "1"
                if hasattr(packet.tcp, "flags_reset")
                else False
            )
            # SYN=1, ACK=0 means initiating a connection without ACK
            if hasattr(packet.tcp, "flags_syn") and hasattr(packet.tcp, "flags_ack"):
                syn_flag = (
                    packet.tcp.flags_syn == "1" and packet.tcp.flags_ack == "0"
                )

        # Bug 5 Fix: Decouple MAC address fallback logic.
        # Previously 'if src_ip == "N/A" and dst_ip == "N/A"' prevented fallback
        # if only one address was missing. Now each address independently falls back
        # to its corresponding Ethernet MAC address when the IP layer is absent.
        src_mac = packet.eth.src if hasattr(packet, "eth") else "N/A"
        dst_mac = packet.eth.dst if hasattr(packet, "eth") else "N/A"
        src_addr = src_ip if src_ip != "N/A" else src_mac
        dst_addr = dst_ip if dst_ip != "N/A" else dst_mac

        return [
            protocol, length, src_addr, dst_addr, src_port, dst_port,
            timestamp, retransmission, reset_flag, syn_flag,
        ]
    except Exception:
        return None


def _parse_scapy_packet(pkt):
    """
    Extract features from a single Scapy packet object.

    Provides pure-Python fallback dissection when tshark/pyshark is unavailable.

    Returns
    -------
    list or None : 10 extracted fields matching PACKET_COLUMNS, or None if skipped.
    """
    try:
        from scapy.all import IP, TCP, UDP, Ether
        protocol = pkt.lastlayer().name if hasattr(pkt, "lastlayer") else "N/A"
        if protocol in ["STP", "ARP", "CDP"]:
            return None

        length = len(pkt)
        src_ip = pkt[IP].src if IP in pkt else "N/A"
        dst_ip = pkt[IP].dst if IP in pkt else "N/A"

        src_port = "N/A"
        dst_port = "N/A"
        if TCP in pkt:
            src_port = str(pkt[TCP].sport)
            dst_port = str(pkt[TCP].dport)
        elif UDP in pkt:
            src_port = str(pkt[UDP].sport)
            dst_port = str(pkt[UDP].dport)

        timestamp = float(pkt.time)
        retransmission = False
        reset_flag = False
        syn_flag = False

        if TCP in pkt:
            flags = pkt[TCP].flags
            reset_flag = bool(flags & 0x04)  # RST
            syn_flag = bool(flags & 0x02) and not bool(flags & 0x10)  # SYN without ACK

        # Bug 5 Fix: Decouple MAC address fallback logic for Scapy frames
        src_mac = pkt[Ether].src if Ether in pkt else "N/A"
        dst_mac = pkt[Ether].dst if Ether in pkt else "N/A"
        src_addr = src_ip if src_ip != "N/A" else src_mac
        dst_addr = dst_ip if dst_ip != "N/A" else dst_mac

        return [
            protocol, length, src_addr, dst_addr, src_port, dst_port,
            timestamp, retransmission, reset_flag, syn_flag,
        ]
    except Exception:
        return None


def extract_features(pcap_file):
    """
    Parse a .pcap file and extract per-packet features into a DataFrame.

    Why these features?
    -------------------
    - Protocol      : lets us spot unexpected or unknown protocols
    - Length        : packet size — used by Layer 1 anomaly model
    - Src/Dst_Address: source and destination hosts (IP or MAC fallback)
    - Src/Dst_Port  : port numbers — essential for Layer 2 port-scan detection
    - Timestamp     : packet capture time — used by Layer 1 anomaly model
    - Retransmission: TCP retransmission flag (added by Wireshark dissector)
    - Reset_Flag    : TCP RST flag — abrupt connection termination
    - SYN_Flag      : TCP SYN without ACK = new connection request (SYN-flood signal)

    Parameters
    ----------
    pcap_file : str — path to a .pcap or .pcapng file

    Returns
    -------
    pd.DataFrame with columns:
        Protocol, Length, Src_Address, Dst_Address, Src_Port, Dst_Port,
        Timestamp, Retransmission, Reset_Flag, SYN_Flag
    """
    data = []
    use_pyshark = True

    # 1. Try pyshark (Wireshark dissector backend)
    try:
        _ensure_asyncio_loop()
        cap = pyshark.FileCapture(pcap_file)
        for packet in cap:
            row = _parse_pyshark_packet(packet)
            if row is not None:
                data.append(row)
        cap.close()

    except Exception as e:
        use_pyshark = False
        print(f"[Notice] pyshark unavailable ({e}). Falling back to native scapy parser...")

    # 2. Fallback: scapy native reader (pure Python, requires no external tshark binary)
    if not use_pyshark or len(data) == 0:
        data = []
        try:
            import logging
            logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
            from scapy.all import rdpcap

            packets = rdpcap(pcap_file)
            for pkt in packets:
                row = _parse_scapy_packet(pkt)
                if row is not None:
                    data.append(row)
        except Exception as e_scapy:
            print(f"Error extracting packets with scapy: {e_scapy}")

    return pd.DataFrame(data, columns=PACKET_COLUMNS)


def detect_anomalies(data):
    """
    [ORIGINAL — unchanged]
    Layer 1: per-packet anomaly detection using Isolation Forest.

    Why Isolation Forest?
    ---------------------
    Isolation Forest is an unsupervised algorithm that works by randomly
    partitioning the feature space. Points that require very few splits to
    isolate (i.e., they sit far from the bulk of the data) are scored as
    anomalies. It requires no labelled training data and runs in O(n log n),
    making it practical for large captures.

    Features used: Length + Timestamp
    ----------------------------------
    These are the two numerical features available in the original script.
    Limitation: a port-scan packet has a perfectly normal length and arrives
    at a normal time — this model will NOT flag it. That gap is addressed by
    the Layer 2 windowed model in Section 2 below.

    contamination=0.05 means: we expect roughly 5% of packets to be anomalous.
    This is tunable — lower values = fewer, higher-confidence anomalies.
    """
    # Select numeric features for analysis
    features = data[["Length", "Timestamp"]]

    # Normalize features — StandardScaler brings both to zero mean, unit variance.
    # Without scaling, Timestamp (a large epoch number) would dominate Length.
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Fit Isolation Forest model
    # random_state=42 ensures reproducible results across runs
    model = IsolationForest(contamination=0.05, random_state=42)
    data = data.copy()
    data["Anomaly"] = model.fit_predict(scaled_features)
    # fit_predict returns: -1 = anomaly, +1 = normal

    # Assign human-readable anomaly type labels using domain knowledge
    # These are rule-based labels applied ON TOP of the ML score — the ML
    # decides IF something is anomalous; the rules decide WHAT TYPE it is.
    data["Anomaly_Type"] = "Other"
    data.loc[data["Retransmission"], "Anomaly_Type"] = "Retransmission"
    data.loc[data["Reset_Flag"], "Anomaly_Type"] = "Reset Flag"
    data.loc[
        (data["Length"] > 1500) & (data["Anomaly"] == -1), "Anomaly_Type"
    ] = "High Packet Length"

    # Subdivide 'Other' anomalies into more detailed categories
    data.loc[
        (data["Anomaly_Type"] == "Other")
        & (data["Timestamp"] > data["Timestamp"].quantile(0.95)),
        "Anomaly_Type",
    ] = "High Latency"
    data.loc[
        (data["Anomaly_Type"] == "Other")
        & (data["Protocol"].str.contains("UNKNOWN", na=False)),
        "Anomaly_Type",
    ] = "Unexpected Protocol"
    data.loc[
        (data["Anomaly_Type"] == "Other")
        & ((data["Src_Address"] == "N/A") | (data["Dst_Address"] == "N/A")),
        "Anomaly_Type",
    ] = "Malformed Packet"

    return data


def analyze_anomalies(data):
    """
    Print a concise French grouped summary of Layer 1 (per-packet) anomalies.
    Shows counts by category, top source IPs, and a short preview table.
    Used in command-line mode. The Streamlit dashboard renders its own table.
    """
    anomalies = data[data["Anomaly"] == -1]
    total = len(anomalies)

    if total == 0:
        print("  Aucune anomalie de niveau paquet détectée.")
        return

    # ── Comptage par type d'anomalie ──────────────────────────────────────────
    type_counts = anomalies["Anomaly_Type"].value_counts()

    LABELS_FR = {
        "Retransmission":     "Retransmissions TCP",
        "High Latency":       "Latence élevée",
        "Reset Flag":         "Réinitialisations TCP (RST)",
        "Unexpected Protocol":"Protocoles inattendus",
        "Malformed Packet":   "Paquets malformés",
        "Other":              "Autres anomalies",
    }

    print(f"\n  {'Type d\'anomalie':<35} {'Paquets':>8}")
    print(f"  {'-'*44}")
    for atype, count in type_counts.items():
        label = LABELS_FR.get(atype, atype)
        print(f"  {label:<35} {count:>8,}")
    print(f"  {'-'*44}")
    print(f"  {'TOTAL anomalies (Couche 1)':<35} {total:>8,}")

    # ── Top 5 sources les plus actives ────────────────────────────────────────
    top_src = (
        anomalies["Src_Address"]
        .value_counts()
        .head(5)
    )
    if not top_src.empty:
        print(f"\n  Top sources suspectes :")
        for ip, cnt in top_src.items():
            bar = "█" * min(cnt // max(1, total // 20), 20)
            print(f"    {ip:<25} {cnt:>5,} paquets  {bar}")

    # ── Aperçu des 5 premiers paquets anormaux ────────────────────────────────
    print(f"\n  Aperçu (5 premiers paquets anormaux) :")
    print(f"  {'#':<6} {'Protocole':<10} {'Source':<28} {'Destination':<28} {'Type'}")
    print(f"  {'-'*90}")
    for i, (idx, row) in enumerate(anomalies.head(5).iterrows()):
        src = f"{row['Src_Address']}:{row['Src_Port']}"
        dst = f"{row['Dst_Address']}:{row['Dst_Port']}"
        label = LABELS_FR.get(row["Anomaly_Type"], row["Anomaly_Type"])
        print(f"  {idx+1:<6} {row['Protocol']:<10} {src:<28} {dst:<28} {label}")


def plot_anomalies(data):
    """
    [ORIGINAL — unchanged]
    Layer 1 visualization: scatter plot of packet Length vs. packet index,
    color-coded by anomaly type. Shows which individual packets were flagged
    and why (retransmission, reset, oversized, etc.).
    """
    plt.figure(figsize=(12, 8))

    # Separate normal and abnormal packets
    normal_packets = data[data["Anomaly"] == 1]
    abnormal_packets = data[data["Anomaly"] == -1]

    # Plot normal packets
    plt.scatter(
        normal_packets.index, normal_packets["Length"],
        color="blue", label="Normal Packets", s=5, alpha=0.5
    )

    # Highlight abnormal packets with retransmissions and reset flags
    retransmissions = abnormal_packets[abnormal_packets["Retransmission"]]
    resets = abnormal_packets[abnormal_packets["Reset_Flag"]]
    high_latency = abnormal_packets[abnormal_packets["Anomaly_Type"] == "High Latency"]
    unexpected_protocol = abnormal_packets[
        abnormal_packets["Anomaly_Type"] == "Unexpected Protocol"
    ]
    malformed_packet = abnormal_packets[
        abnormal_packets["Anomaly_Type"] == "Malformed Packet"
    ]

    plt.scatter(retransmissions.index, retransmissions["Length"], color="orange", label="Retransmissions")
    plt.scatter(resets.index, resets["Length"], color="red", label="Reset Flags")
    plt.scatter(high_latency.index, high_latency["Length"], color="green", label="High Latency")
    plt.scatter(unexpected_protocol.index, unexpected_protocol["Length"], color="purple", label="Unexpected Protocol")
    plt.scatter(malformed_packet.index, malformed_packet["Length"], color="brown", label="Malformed Packet")

    plt.title("Packet Length vs. Index with Highlighted Anomalies")
    plt.xlabel("Packet Index")
    plt.ylabel("Packet Length")
    plt.legend()
    plt.show()


# ==============================================================================
# SECTION 2 — NEW FUNCTIONS: Windowed Behavioral Analysis Layer
# ==============================================================================
# These three functions implement Layer 2. They operate on the same per-packet
# DataFrame produced by extract_features(), but instead of evaluating packets
# individually, they aggregate them into time-windowed behavioral profiles.
# ==============================================================================


def aggregate_windows(df, window_size=5):
    """
    [NEW — Layer 2 preprocessing]
    Group per-packet data into time-windowed, per-source behavioral profiles.

    WHY behavioral aggregation?
    ---------------------------
    A port scan consists of many individually "normal" packets sent to different
    ports in rapid succession. No single probe packet looks suspicious — what's
    anomalous is the PATTERN: one source hitting hundreds of unique destination
    ports within a few seconds.

    Isolation Forest on raw packets cannot see this because it evaluates packets
    in isolation. By grouping packets into (source_ip, time_window) buckets and
    computing aggregate statistics, we turn a temporal sequence of events into a
    behavioral fingerprint that the ML model can evaluate as a single observation.

    Example (from NMAP_PROBE.pcap):
        One source IP contacted 1,935 distinct destination ports.
        Per-packet Layer 1: every probe is ~60 bytes, normal timing → NOT flagged.
        Windowed Layer 2: unique_dst_ports=1935, packet_count=1935 → ratio=1.0 → FLAGGED.

    Features computed per (Src_Address, time_window) group:
    ---------------------------------------------------------
    packet_count      — Total packets from this source in this window.
                        High value = high-volume sender → flood candidate.

    unique_dst_ports  — Number of DISTINCT destination ports contacted.
                        High value relative to packet_count = port scan.
                        (An nmap default scan hits each port exactly once.)

    unique_dst_ips    — Number of DISTINCT destination IP addresses targeted.
                        High value = host sweep (scanning an entire subnet)
                        or botnet C2 beaconing to many hosts.

    syn_count         — Count of TCP SYN packets without a matching ACK.
                        In a normal 3-way handshake: SYN → SYN-ACK → ACK.
                        In a SYN flood: thousands of SYNs, no ACK ever sent.
                        A high syn_count with no matching connections = SYN flood.

    avg_packet_length — Mean payload size across all packets in the window.
                        Very high average (near MTU=1500) from a single source
                        suggests a volumetric amplification attack.

    Parameters
    ----------
    df          : pd.DataFrame — per-packet output of extract_features()
    window_size : int — bucket size in seconds (default: 5).
                  Smaller windows (1–3s) catch fast, aggressive scans.
                  Larger windows (15–30s) catch slow/stealthy scans.
                  Tradeoff: too small → legitimate traffic looks bursty;
                            too large → attack signal diluted into noise.

    Returns
    -------
    pd.DataFrame where each row = one (Src_Address, time_window) behavioral
    profile with the 5 features above.
    """
    df = df.copy()

    # Ensure Timestamp is numeric (float epoch seconds, e.g. 1685432100.123)
    df["Timestamp"] = pd.to_numeric(df["Timestamp"], errors="coerce")

    # Assign each packet to a time-window bucket.
    # floor(timestamp / window_size) * window_size = start of the window.
    # Example: timestamp=12.7s, window_size=5 → bucket_start=10.0s
    df["time_window"] = (df["Timestamp"] // window_size) * window_size

    # Only process packets with a real IP address.
    # L2-only packets (Src_Address='N/A') carry no useful behavioral signal
    # for source-level profiling — we cannot attribute them to a specific host.
    df_ip = df[df["Src_Address"] != "N/A"].copy()

    # Convert SYN_Flag boolean to int so it can be summed in the aggregation
    df_ip["SYN_Flag"] = df_ip["SYN_Flag"].astype(int)

    # Build one behavioral row per (source IP, time window) pair
    window_df = (
        df_ip.groupby(["Src_Address", "time_window"])
        .agg(
            packet_count=("Length", "count"),          # volume
            avg_packet_length=("Length", "mean"),       # payload size
            unique_dst_ports=("Dst_Port", "nunique"),  # port diversity
            unique_dst_ips=("Dst_Address", "nunique"), # target diversity
            syn_count=("SYN_Flag", "sum"),             # SYN flood indicator
        )
        .reset_index()
    )

    return window_df


def detect_window_anomalies(window_df):
    """
    [NEW — Layer 2 detection]
    Apply Isolation Forest on the windowed behavioral features, then assign
    human-readable attack-type labels based on feature ratios.

    WHY a separate model (not just extending Layer 1)?
    --------------------------------------------------
    Layer 1 and Layer 2 operate on fundamentally different observation units:
    - Layer 1 observation: one packet (features: length, timestamp)
    - Layer 2 observation: one (source, window) pair (features: 5 aggregate stats)

    Combining them into a single model would require normalizing across
    incompatible feature spaces. Keeping them separate also lets us present
    a clear "before vs. after" comparison to the jury: "here is what we saw
    before, here is what the new layer reveals".

    WHY Isolation Forest (same algorithm as Layer 1)?
    -------------------------------------------------
    Isolation Forest is ideal for this use case because:
    1. Unsupervised — no labelled attack data required.
    2. Works well on high-dimensional data (5 features here).
    3. Robust to outlier proportion — the contamination parameter controls
       how aggressively we want to flag windows.
    4. Fast — O(n log n), runs in milliseconds even on large captures.

    WHY contamination=0.10 (10%) instead of 0.05?
    ----------------------------------------------
    At the per-window level, a capture with a real attack may have a large
    fraction of anomalous windows (e.g., if the scan runs for 30 seconds and
    windows are 5s, that's 6 attack windows). Using 5% might suppress real
    events. 10% is a safer upper bound; we'd rather see a few false positives
    in the table than miss the scan entirely during a live demo.

    Anomaly label logic (domain knowledge applied after ML scoring):
    ----------------------------------------------------------------
    The Isolation Forest tells us THAT a window is anomalous.
    The rules below tell us WHAT TYPE of attack it likely is.

    Port Scan   : unique_dst_ports / packet_count > 0.5
                  Interpretation: more than half of all packets in this window
                  went to a unique destination port. This is the mathematical
                  signature of a sequential port sweep (e.g. nmap -sS).
                  Threshold 0.5 chosen because legitimate traffic rarely contacts
                  more distinct ports than half its total packet count.

    Flood/DDoS  : flagged by IF but port diversity ratio ≤ 0.5
                  Interpretation: many packets, but concentrated to a small set
                  of destinations — consistent with a volumetric flood rather
                  than a scan. Could be UDP flood, ICMP flood, HTTP flood, etc.

    Parameters
    ----------
    window_df : pd.DataFrame — output of aggregate_windows()

    Returns
    -------
    Same DataFrame with two new columns:
        Anomaly      : -1 = anomaly, +1 = normal (Isolation Forest output)
        Anomaly_Type : 'Port Scan', 'Flood / DDoS', 'Normal'
    """
    window_df = window_df.copy()

    # The 5 behavioral features to feed into the model
    feature_cols = [
        "packet_count",
        "avg_packet_length",
        "unique_dst_ports",
        "unique_dst_ips",
        "syn_count",
    ]
    features = window_df[feature_cols]

    # StandardScaler is critical here:
    # packet_count can be in the hundreds while unique_dst_ips might be 1–5.
    # Without scaling, high-magnitude features (packet_count, syn_count)
    # would dominate the Isolation Forest splits, effectively ignoring the
    # port-diversity signal that catches port scans.
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Fit and predict with Isolation Forest
    model = IsolationForest(contamination=0.10, random_state=42)
    window_df["Anomaly"] = model.fit_predict(scaled_features)

    # Initialize all windows as 'Normal'
    window_df["Anomaly_Type"] = "Normal"

    # Identify anomalous windows (Anomaly == -1)
    anomalous_mask = window_df["Anomaly"] == -1

    # Port diversity ratio: (unique dst ports) / (total packets in window)
    # A ratio near 1.0 means almost every packet went to a unique port → scan.
    # We use .replace(0, 1) to avoid division-by-zero on empty windows.
    port_diversity_ratio = (
        window_df["unique_dst_ports"] / window_df["packet_count"].replace(0, 1)
    )

    # Classify: port scan if most packets target unique ports
    port_scan_mask = anomalous_mask & (port_diversity_ratio > 0.5)
    # Classify: flood if flagged but NOT a scan
    flood_mask = anomalous_mask & ~port_scan_mask

    window_df.loc[port_scan_mask, "Anomaly_Type"] = "Port Scan"
    window_df.loc[flood_mask, "Anomaly_Type"] = "Flood / DDoS"

    return window_df


def plot_window_anomalies(window_df):
    """
    [NEW — Layer 2 visualization]
    Scatter plot of unique_dst_ports (Y) vs packet_count (X) for each
    behavioral window, color-coded by anomaly type.

    WHY these axes?
    ---------------
    These two features are the most diagnostic for distinguishing attack types:

    - X-axis (packet_count): raw volume sent by a source in one time window.
      A normal host sends a handful of packets; a flood source sends hundreds.

    - Y-axis (unique_dst_ports): port diversity. A normal host connects to
      a few well-known ports (80, 443, 22). A port scanner contacts hundreds
      of unique ports in seconds.

    Quadrant interpretation:
      Bottom-left  : few packets, few ports → NORMAL traffic
      Top-left     : many unique ports, moderate packet count → PORT SCAN
      Bottom-right : many packets, few ports → FLOOD / DDoS
      Top-right    : both high → aggressive scan + flood (rare but possible)

    Point size encodes avg_packet_length so large-payload attacks are visually
    distinguishable from small-packet floods (e.g. SYN flood vs. UDP amplification).
    """
    plt.figure(figsize=(12, 8))

    colors = {
        "Normal": "steelblue",
        "Port Scan": "red",
        "Flood / DDoS": "darkorange",
    }

    for label, group in window_df.groupby("Anomaly_Type"):
        # Scale point sizes by average packet length — larger payloads = bigger dots
        max_len = window_df["avg_packet_length"].max() or 1
        sizes = (group["avg_packet_length"] / max_len * 150 + 15).fillna(20)

        plt.scatter(
            group["packet_count"],
            group["unique_dst_ports"],
            c=colors.get(label, "gray"),
            label=label,
            alpha=0.75,
            s=sizes,
            edgecolors="white",
            linewidths=0.4,
        )

    plt.title(
        "Behavioral Window Analysis: Packet Volume vs. Port Diversity\n"
        "(point size = avg packet length; each point = one source IP per time window)"
    )
    plt.xlabel("Packet Count (per source per time window)")
    plt.ylabel("Unique Destination Ports (per source per time window)")
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.show()


# ==============================================================================
# SECTION 3 — LIVE CALIBRATE-THEN-MONITOR ANOMALY DETECTION ENGINE
# ==============================================================================
# This section implements the two-phase live detection mode:
#   Phase 1 (Calibration): capture live traffic to learn a session baseline
#                          using IsolationForest + StandardScaler (contamination=0.10).
#   Phase 2 (Monitoring) : continuously evaluate time windows against the fitted
#                          baseline and report anomalous windows in real-time.
# ==============================================================================


def _format_permission_error(interface=None, raw_error=""):
    """Format clear, OS-specific actionable guidance when live capture cannot start."""
    iface_str = f" on interface '{interface}'" if interface else ""
    return (
        f"\n{'='*75}\n"
        f"[LIVE CAPTURE PERMISSION / DRIVER ERROR]\n"
        f"Unable to capture live packets{iface_str}.\n"
        f"Detail: {raw_error}\n\n"
        f"Live packet capture requires elevated privileges and capture drivers:\n"
        f"  • Windows: Install Npcap (https://npcap.com) with 'WinPcap API-compatible Mode' enabled.\n"
        f"             Verify the Npcap service is running ('net start npcap') and run your\n"
        f"             terminal or IDE as Administrator.\n"
        f"  • Linux / macOS: Run with root / sudo permissions:\n"
        f"             sudo python detection_engine.py\n"
        f"             or sudo streamlit run dashboard.py\n"
        f"{'='*75}\n"
    )


def get_available_interfaces():
    """
    Return a list of available network interface names.
    Tries Scapy interface discovery, falling back to empty list on driver error.
    """
    ifaces = []
    try:
        import logging
        logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
        from scapy.all import conf, get_if_list
        if hasattr(conf, "ifaces") and conf.ifaces:
            for iface_key, iface_obj in conf.ifaces.items():
                desc = getattr(iface_obj, "description", None) or getattr(iface_obj, "name", str(iface_key))
                if desc and desc not in ifaces:
                    ifaces.append(desc)
        if not ifaces:
            ifaces = list(get_if_list())
    except Exception:
        pass
    return ifaces


def capture_live_packets(interface=None, timeout=5):
    """
    Capture live packets from a network interface for `timeout` seconds.

    Attempts PyShark LiveCapture first; if unavailable, falls back to native Scapy.
    Catches permission/driver failures and raises PermissionError with clear,
    actionable user guidance.

    Parameters
    ----------
    interface : str or None — network interface name/index
    timeout   : int or float — duration in seconds to capture

    Returns
    -------
    pd.DataFrame matching PACKET_COLUMNS schema.
    """
    data = []
    use_pyshark = True

    # 1. Try PyShark LiveCapture
    try:
        _ensure_asyncio_loop()
        cap_kwargs = {}
        if interface:
            cap_kwargs["interface"] = interface
        cap = pyshark.LiveCapture(**cap_kwargs)
        cap.sniff(timeout=timeout)
        for packet in cap:
            row = _parse_pyshark_packet(packet)
            if row is not None:
                data.append(row)
        cap.close()
        return pd.DataFrame(data, columns=PACKET_COLUMNS)

    except Exception as e_pyshark:
        use_pyshark = False
        last_err = str(e_pyshark)

    # 2. Fallback: Scapy sniff
    if not use_pyshark:
        try:
            import logging
            logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
            from scapy.all import sniff

            sniff_kwargs = {"timeout": timeout, "store": True}
            if interface:
                sniff_kwargs["iface"] = interface

            packets = sniff(**sniff_kwargs)
            for pkt in packets:
                row = _parse_scapy_packet(pkt)
                if row is not None:
                    data.append(row)
            return pd.DataFrame(data, columns=PACKET_COLUMNS)

        except Exception as e_scapy:
            combined_err = f"PyShark: {last_err} | Scapy: {e_scapy}"
            err_msg = _format_permission_error(interface, combined_err)
            raise PermissionError(err_msg) from e_scapy


def calibrate_baseline(df_packets, window_size=5):
    """
    Phase 1: Calibrate baseline Isolation Forest and StandardScaler from session traffic.

    Parameters
    ----------
    df_packets  : pd.DataFrame — packet data collected during Phase 1
    window_size : int — aggregation window size in seconds (default: 5)

    Returns
    -------
    (scaler, model, window_df) : fitted StandardScaler, fitted IsolationForest,
                                 and the aggregated calibration DataFrame.
    """
    if df_packets.empty:
        window_df = pd.DataFrame(columns=WINDOW_FEATURE_COLS + ["Src_Address", "time_window"])
    else:
        window_df = aggregate_windows(df_packets, window_size=window_size)

    scaler = StandardScaler()
    model = IsolationForest(contamination=0.10, random_state=42)

    if len(window_df) >= 2:
        # Check for near-zero variance across all feature columns (e.g. synthetic/constant traffic)
        feat_vals = window_df[WINDOW_FEATURE_COLS].values
        if np.all(feat_vals.std(axis=0) == 0):
            # Add micro-variation so tree splits are non-degenerate
            jitter = np.random.RandomState(42).normal(0, 1e-4, size=feat_vals.shape)
            scaled_features = scaler.fit_transform(feat_vals + jitter)
        else:
            scaled_features = scaler.fit_transform(window_df[WINDOW_FEATURE_COLS])
        model.fit(scaled_features)
    else:
        # Fallback if traffic during calibration was minimal or empty:
        # Fit on a synthetic neutral baseline to avoid fit errors on 0/1 samples
        synthetic_normal = pd.DataFrame([
            {"packet_count": 8,  "avg_packet_length": 450.0, "unique_dst_ports": 2, "unique_dst_ips": 1, "syn_count": 0},
            {"packet_count": 12, "avg_packet_length": 500.0, "unique_dst_ports": 3, "unique_dst_ips": 1, "syn_count": 1},
            {"packet_count": 15, "avg_packet_length": 520.0, "unique_dst_ports": 2, "unique_dst_ips": 2, "syn_count": 0},
            {"packet_count": 10, "avg_packet_length": 480.0, "unique_dst_ports": 1, "unique_dst_ips": 1, "syn_count": 0},
        ])
        scaled_features = scaler.fit_transform(synthetic_normal[WINDOW_FEATURE_COLS])
        model.fit(scaled_features)

    return scaler, model, window_df


def score_monitoring_window(df_packets, scaler, model, window_size=5):
    """
    Phase 2: Score a monitoring time window against the calibrated baseline.

    Uses the pre-fitted scaler and model without refitting, applying the exact
    port diversity ratio (>0.5 = Port Scan, else Flood / DDoS) domain logic.

    Parameters
    ----------
    df_packets  : pd.DataFrame — packet data from the current monitoring window
    scaler      : fitted StandardScaler from Phase 1
    model       : fitted IsolationForest from Phase 1
    window_size : int — window size in seconds (default: 5)

    Returns
    -------
    pd.DataFrame with aggregate metrics, Anomaly (-1 or 1), and Anomaly_Type.
    """
    if df_packets.empty:
        return pd.DataFrame(
            columns=WINDOW_FEATURE_COLS + ["Src_Address", "time_window", "Anomaly", "Anomaly_Type"]
        )

    window_df = aggregate_windows(df_packets, window_size=window_size)
    if window_df.empty:
        window_df["Anomaly"] = []
        window_df["Anomaly_Type"] = []
        return window_df

    features = window_df[WINDOW_FEATURE_COLS]
    scaled_features = scaler.transform(features)
    window_df["Anomaly"] = model.predict(scaled_features)
    window_df["Anomaly_Type"] = "Normal"

    anomalous_mask = window_df["Anomaly"] == -1
    port_diversity_ratio = (
        window_df["unique_dst_ports"] / window_df["packet_count"].replace(0, 1)
    )

    port_scan_mask = anomalous_mask & (port_diversity_ratio > 0.5)
    flood_mask = anomalous_mask & ~port_scan_mask

    window_df.loc[port_scan_mask, "Anomaly_Type"] = "Port Scan"
    window_df.loc[flood_mask, "Anomaly_Type"] = "Flood / DDoS"

    return window_df


def run_live_detection(
    interface=None,
    calibration_duration=120,
    window_size=5,
    callback=None,
    stop_event=None,
    packet_source=None,
):
    """
    Run live two-phase network anomaly detection.

    Phase 1 (Calibration):
        Buffers live traffic for `calibration_duration` seconds.
        Fits session baseline StandardScaler + IsolationForest.
        Prints status countdown: "Learning normal traffic... X seconds remaining".

    Phase 2 (Continuous Monitoring):
        Loops every `window_size` seconds, extracting behavioral features
        and scoring windows against the calibrated baseline.
        Reports anomalies immediately (print / log / callback).
        Never drops or blocks traffic (detection/monitoring only).

    Parameters
    ----------
    interface            : str or None — network interface name
    calibration_duration : int — calibration period in seconds (default: 120)
    window_size          : int — window interval in seconds (default: 5)
    callback             : callable or None — callback(phase, data) for UI integration
    stop_event           : threading.Event or None — external stop trigger
    packet_source        : callable or None — custom capture function(interface, timeout)
    """
    capture_fn = packet_source or capture_live_packets

    # Verify capture driver / permissions before entering loop
    try:
        test_df = capture_fn(interface=interface, timeout=0.5)
    except PermissionError as pe:
        if callback:
            callback("error", {"message": str(pe)})
        raise pe
    except Exception as e:
        err_msg = _format_permission_error(interface, str(e))
        if callback:
            callback("error", {"message": err_msg})
        raise PermissionError(err_msg) from e

    # ── Phase 1: Calibration ───────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"[PHASE 1 - CALIBRATION] Learning normal traffic baseline ({calibration_duration}s)...")
    print(f"{'='*70}")

    start_calib = time.time()
    calib_packets = []
    if not test_df.empty:
        calib_packets.append(test_df)

    step_slice = min(2, max(1, window_size))

    while True:
        if stop_event and stop_event.is_set():
            print("\nCalibration cancelled.")
            return

        elapsed = time.time() - start_calib
        remaining = max(0, int(calibration_duration - elapsed))

        status_msg = f"Learning normal traffic... {remaining}s remaining"
        print(f"\r{status_msg}  ", end="", flush=True)

        if callback:
            total_buffered = sum(len(df) for df in calib_packets)
            callback(
                "phase1_progress",
                {
                    "remaining": remaining,
                    "elapsed": elapsed,
                    "duration": calibration_duration,
                    "packets": total_buffered,
                    "status_msg": status_msg,
                },
            )

        if elapsed >= calibration_duration:
            break

        timeout = min(step_slice, remaining) if remaining > 0 else 1
        pkts = capture_fn(interface=interface, timeout=timeout)
        if not pkts.empty:
            calib_packets.append(pkts)

    print()  # newline after countdown
    all_calib_df = (
        pd.concat(calib_packets, ignore_index=True)
        if calib_packets
        else pd.DataFrame(columns=PACKET_COLUMNS)
    )

    scaler, baseline_model, calib_windows = calibrate_baseline(
        all_calib_df, window_size=window_size
    )

    print(
        f"[PHASE 1 COMPLETE] Baseline calibrated on {len(all_calib_df):,} packets "
        f"across {len(calib_windows):,} behavioral window(s).\n"
    )

    if callback:
        callback(
            "phase1_complete",
            {
                "packets": len(all_calib_df),
                "windows": len(calib_windows),
                "scaler": scaler,
                "model": baseline_model,
            },
        )

    # ── Phase 2: Continuous Monitoring ─────────────────────────────────────────
    print(f"{'='*70}")
    print(f"[PHASE 2 - CONTINUOUS MONITORING] Active (evaluating every {window_size}s).")
    print("Reporting anomalies in real time -- traffic is NOT blocked.")
    print("Press Ctrl+C to stop monitoring.")
    print(f"{'='*70}\n")

    window_idx = 0
    try:
        while True:
            if stop_event and stop_event.is_set():
                print("\nMonitoring stopped.")
                break

            window_idx += 1
            pkts = capture_fn(interface=interface, timeout=window_size)
            scored_win = score_monitoring_window(
                pkts, scaler, baseline_model, window_size=window_size
            )

            anomalies = scored_win[scored_win["Anomaly"] == -1]
            now_str = time.strftime("%H:%M:%S")

            if not anomalies.empty:
                for _, row in anomalies.iterrows():
                    print(
                        f"[!] [ALERT - {now_str}] {row['Anomaly_Type']} detected! "
                        f"Source: {row['Src_Address']} | "
                        f"Packets: {row['packet_count']} | "
                        f"Unique Ports: {row['unique_dst_ports']} | "
                        f"SYN Count: {row['syn_count']}"
                    )
                    try:
                        alert_rec = create_alert_record(
                            src_address=row['Src_Address'],
                            anomaly_type=row['Anomaly_Type'],
                            packet_count=row['packet_count'],
                            unique_dst_ports=row['unique_dst_ports'],
                            unique_dst_ips=row.get('unique_dst_ips', 1),
                            syn_count=row['syn_count'],
                            avg_packet_length=row.get('avg_packet_length', 0.0),
                            time_window=row.get('time_window'),
                            origin="Live Surveillance",
                        )
                        add_alert(alert_rec)
                    except Exception:
                        pass
            else:
                print(
                    f"[{now_str}] Window {window_idx} ({len(pkts)} packets): Normal traffic."
                )

            if callback:
                callback(
                    "phase2_window",
                    {
                        "window_idx": window_idx,
                        "packets": pkts,
                        "window_df": scored_win,
                        "anomalies": anomalies,
                        "timestamp": now_str,
                    },
                )

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")


# ──────────────────────────────────────────────────────────────────────────────
# INCIDENT NOTIFICATION & AUDIT TRAIL LOGGING
# ──────────────────────────────────────────────────────────────────────────────
ALERTS_FILE = "alerts_history.json"


def create_alert_record(
    src_address,
    anomaly_type,
    packet_count=0,
    unique_dst_ports=0,
    unique_dst_ips=0,
    syn_count=0,
    avg_packet_length=0.0,
    time_window=None,
    origin="Live Surveillance",
):
    """
    Construct a standardized security incident dictionary with severity and SOC recommendations.
    """
    now_dt = datetime.datetime.now()
    timestamp_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    alert_id = f"ALT-{now_dt.strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

    # Severity determination
    if anomaly_type == "Port Scan":
        severity = "CRITICAL"
        description = (
            f"Stealth sequential port scan detected from {src_address}. "
            f"Contacted {unique_dst_ports} unique destination ports across {packet_count} packets "
            f"(port diversity ratio: {(unique_dst_ports / max(packet_count, 1)):.1%})."
        )
        recommendation = (
            f"Immediate mitigation: Block {src_address} at perimeter gateway "
            f"(`iptables -A INPUT -s {src_address} -j DROP` or edge firewall rule). "
            f"Review audit logs on targeted hosts for service exploitation."
        )
    elif anomaly_type == "Flood / DDoS":
        severity = "HIGH"
        description = (
            f"High-volume packet flood detected from {src_address} "
            f"({packet_count} packets in window, avg length {avg_packet_length:.1f} bytes)."
        )
        recommendation = (
            f"Apply ingress rate limiting and TCP SYN-cookie enforcement for {src_address}. "
            f"Verify whether target internal service is saturated or sustaining an amplification attack."
        )
    else:
        severity = "MEDIUM"
        description = (
            f"Behavioral network anomaly ({anomaly_type}) detected from {src_address}."
        )
        recommendation = (
            f"Investigate endpoint {src_address} for protocol misconfiguration, corrupted framing, "
            f"or unauthorized tool activity."
        )

    return {
        "id": alert_id,
        "timestamp": timestamp_str,
        "severity": severity,
        "anomaly_type": str(anomaly_type),
        "src_address": str(src_address),
        "packet_count": int(packet_count),
        "unique_dst_ports": int(unique_dst_ports),
        "unique_dst_ips": int(unique_dst_ips),
        "syn_count": int(syn_count),
        "avg_packet_length": round(float(avg_packet_length), 1),
        "time_window": float(time_window) if time_window is not None else None,
        "origin": str(origin),
        "description": description,
        "recommendation": recommendation,
    }


def load_alerts(filepath=ALERTS_FILE):
    """Load persistent security alerts from JSON file."""
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


def save_alerts(alerts, filepath=ALERTS_FILE):
    """Save security alerts list to JSON file atomically."""
    try:
        tmp_file = f"{filepath}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(alerts, f, indent=2)
        if os.path.exists(filepath):
            os.replace(tmp_file, filepath)
        else:
            os.rename(tmp_file, filepath)
        return True
    except Exception:
        return False


def add_alert(alert_dict, filepath=ALERTS_FILE):
    """Add a new alert to the persistent audit trail (avoids exact duplicate entries)."""
    alerts = load_alerts(filepath)
    for a in alerts:
        if (
            a.get("src_address") == alert_dict.get("src_address")
            and a.get("anomaly_type") == alert_dict.get("anomaly_type")
            and a.get("time_window") == alert_dict.get("time_window")
            and alert_dict.get("time_window") is not None
        ):
            return alerts
    alerts.insert(0, alert_dict)
    alerts = alerts[:500]
    save_alerts(alerts, filepath)
    return alerts


def clear_alerts(filepath=ALERTS_FILE):
    """Clear all historical alerts."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass
    return []



# ==============================================================================
# MAIN — Command-line entry point
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("NetScan — Network Anomaly Detection System (NIDS / IPS)")
    print("Conçu et Développé par : Mohamed Reda QIYAOUI — DUT Cybersécurité")
    print("=" * 70)
    print("Select operational mode:")
    print("  [1] Live Capture & Monitoring (Phase 1 Calibration -> Phase 2 Detection)")
    print("  [2] File Analysis Mode (Offline .pcap processing)")
    mode = input("Enter selection [1 or 2, default: 2]: ").strip() or "2"

    if mode == "1":
        print("\n--- Live Detection Mode Configuration ---")
        available_ifaces = get_available_interfaces()
        if available_ifaces:
            print("Detected network interfaces:")
            for idx, iface_name in enumerate(available_ifaces, start=1):
                print(f"  [{idx}] {iface_name}")
            iface_sel = input("Enter interface name or number (press Enter for default): ").strip()
            if iface_sel.isdigit() and 1 <= int(iface_sel) <= len(available_ifaces):
                chosen_iface = available_ifaces[int(iface_sel) - 1]
            else:
                chosen_iface = iface_sel if iface_sel else None
        else:
            chosen_iface = (
                input("Enter network interface name (press Enter for default): ").strip() or None
            )

        try:
            calib_sec = int(
                input("Enter calibration duration in seconds [default: 120]: ").strip() or "120"
            )
        except ValueError:
            calib_sec = 120

        try:
            win_sec = int(
                input("Enter window size in seconds [default: 5]: ").strip() or "5"
            )
        except ValueError:
            win_sec = 5

        try:
            run_live_detection(
                interface=chosen_iface,
                calibration_duration=calib_sec,
                window_size=win_sec,
            )
        except (PermissionError, RuntimeError) as pe:
            print(pe)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")

    else:
        pcap_file = input("Enter the path to the Wireshark capture file (.pcap): ").strip()

        # --- Window size prompt ---
        try:
            window_size = int(
                input("Enter time window size in seconds [default: 5]: ").strip() or "5"
            )
        except ValueError:
            window_size = 5

        # ── Layer 1: Per-packet pipeline (original) ───────────────────────────────
        print("\n[1] Extracting features from the capture file...")
        data = extract_features(pcap_file)

        print("\n[2] Detecting per-packet anomalies (Layer 1 — original model)...")
        analyzed_data = detect_anomalies(data)

        print("\n[3] Analyzing per-packet anomalies...")
        analyze_anomalies(analyzed_data)

        print("\n[4] Plotting per-packet anomalies...")
        plot_anomalies(analyzed_data)

        # Save per-packet anomalies to CSV
        packets_csv = "analyzed_capture_packets.csv"
        packet_anomalies = analyzed_data[analyzed_data["Anomaly"] == -1]
        packet_anomalies.to_csv(packets_csv, index=False)
        print(f"\nPer-packet anomalies saved to: {packets_csv}")

        # ── Layer 2: Windowed behavioral pipeline (new) ───────────────────────────
        print(f"\n[5] Aggregating traffic into {window_size}s time windows...")
        window_df = aggregate_windows(analyzed_data, window_size=window_size)

        print("\n[6] Detecting windowed behavioral anomalies (Layer 2 — new model)...")
        window_results = detect_window_anomalies(window_df)

        print("\n[7] Plotting windowed behavioral anomalies...")
        plot_window_anomalies(window_results)

        # Save windowed anomalies to CSV
        windows_csv = "analyzed_capture_windows.csv"
        window_anomalies = window_results[window_results["Anomaly"] == -1]
        window_anomalies.to_csv(windows_csv, index=False)
        print(f"\nWindowed anomalies saved to: {windows_csv}")

        # ── Summary ───────────────────────────────────────────────────────────────
        port_scans = (window_results["Anomaly_Type"] == "Port Scan").sum()
        floods = (window_results["Anomaly_Type"] == "Flood / DDoS").sum()
        pkt_anomalies = (analyzed_data["Anomaly"] == -1).sum()

        print(f"\n{'='*60}")
        print(f"ANALYSIS SUMMARY")
        print(f"{'='*60}")
        print(f"  Total packets analyzed   : {len(analyzed_data):,}")
        print(f"  Per-packet anomalies     : {pkt_anomalies:,}  (Layer 1)")
        print(f"  Port scan windows        : {port_scans:,}  (Layer 2 — {window_size}s window)")
        print(f"  Flood / DDoS windows     : {floods:,}  (Layer 2 — {window_size}s window)")
        print(f"{'='*60}")
