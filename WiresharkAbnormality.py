"""
WiresharkAbnormality.py — Network Traffic Anomaly Detector
===========================================================
DUT Cybersecurity — Academic Soutenance Project

ARCHITECTURE OVERVIEW
---------------------
This script implements two complementary anomaly detection layers:

  Layer 1 — Per-Packet (original, unchanged):
      Features : packet Length + Timestamp
      Model    : Isolation Forest (contamination=0.05)
      Detects  : individual packets that are unusual in size or timing
                 (retransmissions, resets, oversized frames, etc.)
      Limitation: evaluates packets independently — cannot detect patterns
                  that only emerge across many packets from the same source.

  Layer 2 — Per-Window / Behavioral (new):
      Features : 5 aggregate statistics per (source IP, time window) group
      Model    : Isolation Forest (contamination=0.10)
      Detects  : port scans, SYN floods, host sweeps — attacks that are
                 invisible at the per-packet level but obvious in aggregate.

WHY TWO LAYERS?
---------------
A classic nmap port scan sends a small SYN packet to each target port.
Each individual packet is completely normal in length and timing — Layer 1
will never flag it. But when you zoom out and ask "how many distinct ports
did this host contact in the last 5 seconds?", the answer is 1,935. That
is the signal Layer 2 is designed to capture.

ORIGINAL AUTHORS
----------------
Base script: mayanknauni (https://github.com/mayanknauni/Wireshark-Capture-Anomaly-Detection)
Extensions:  DUT Cybersecurity student — soutenance October 2026

DEPENDENCIES
------------
  pip install pyshark pandas matplotlib scikit-learn streamlit
"""

import asyncio
import os

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


# ==============================================================================
# SECTION 1 — ORIGINAL FUNCTIONS (preserved from the base repository)
# ==============================================================================
# The four functions below are kept as close to the originals as possible.
# The only modification to extract_features() is the addition of 'SYN_Flag'
# extraction (one extra line inside the existing TCP block), which is needed
# by the windowed behavioral layer to count SYN-flood signals.
# All other logic, variable names, and column names are identical to the source.
# ==============================================================================


def extract_features(pcap_file):
    """
    [ORIGINAL — minor addition: SYN_Flag column]
    Parse a .pcap file and extract per-packet features into a DataFrame.

    Why these features?
    -------------------
    - Protocol      : lets us spot unexpected or unknown protocols
    - Length        : packet size — used by Layer 1 anomaly model
    - Src/Dst_Address: source and destination hosts (IP or MAC for L2 traffic)
    - Src/Dst_Port  : port numbers — essential for Layer 2 port-scan detection
    - Timestamp     : packet capture time — used by Layer 1 anomaly model
    - Retransmission: TCP retransmission flag (added by Wireshark dissector)
    - Reset_Flag    : TCP RST flag — abrupt connection termination
    - SYN_Flag      : [ADDED] TCP SYN without ACK = new connection request.
                      A burst of these without completing the 3-way handshake
                      is the hallmark of a SYN-flood DoS attack. We extract
                      this here so the windowed layer can count them per group.

    Parameters
    ----------
    pcap_file : str — path to a .pcap or .pcapng file

    Returns
    -------
    pd.DataFrame with columns:
        Protocol, Length, Src_Address, Dst_Address, Src_Port, Dst_Port,
        Timestamp, Retransmission, Reset_Flag, SYN_Flag
    """
    cap = pyshark.FileCapture(pcap_file)
    data = []

    for packet in cap:
        try:
            protocol = packet.highest_layer

            # Skip specific Layer 2 protocols — these carry no IP-level
            # behavioral signal useful for our detection models.
            if protocol in ["STP", "ARP", "CDP"]:
                continue

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
            syn_flag = False  # [ADDED for Layer 2]

            if hasattr(packet, "tcp"):
                retransmission = hasattr(packet.tcp, "analysis_retransmission")
                reset_flag = (
                    packet.tcp.flags_reset == "1"
                    if hasattr(packet.tcp, "flags_reset")
                    else False
                )
                # [ADDED] SYN=1, ACK=0 means the packet is initiating a new
                # connection but has NOT yet received a server response.
                # In normal traffic this is brief; in a SYN flood, thousands
                # of these arrive with no corresponding ACK from the sender.
                if hasattr(packet.tcp, "flags_syn") and hasattr(packet.tcp, "flags_ack"):
                    syn_flag = (
                        packet.tcp.flags_syn == "1" and packet.tcp.flags_ack == "0"
                    )

            # Include additional information for L2 protocols
            if src_ip == "N/A" and dst_ip == "N/A":
                src_mac = packet.eth.src if hasattr(packet, "eth") else "N/A"
                dst_mac = packet.eth.dst if hasattr(packet, "eth") else "N/A"
                data.append(
                    [protocol, length, src_mac, dst_mac, src_port, dst_port,
                     timestamp, retransmission, reset_flag, syn_flag]
                )
            else:
                data.append(
                    [protocol, length, src_ip, dst_ip, src_port, dst_port,
                     timestamp, retransmission, reset_flag, syn_flag]
                )

        except Exception as e:
            print(f"Error processing packet: {e}")
            continue

    cap.close()
    return pd.DataFrame(
        data,
        columns=[
            "Protocol", "Length", "Src_Address", "Dst_Address",
            "Src_Port", "Dst_Port", "Timestamp",
            "Retransmission", "Reset_Flag", "SYN_Flag",  # SYN_Flag added
        ],
    )


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
    [ORIGINAL — unchanged]
    Print a human-readable text report of Layer 1 (per-packet) anomalies.
    Used in command-line mode. The Streamlit dashboard renders this as a table.
    """
    anomalies = data[data["Anomaly"] == -1]
    for index, row in anomalies.iterrows():
        print(f"Abnormal Packet at Line {index + 1}:")
        print(f"  Protocol: {row['Protocol']}")
        print(f"  Length: {row['Length']} bytes")
        print(f"  Source: {row['Src_Address']}:{row['Src_Port']}")
        print(f"  Destination: {row['Dst_Address']}:{row['Dst_Port']}")
        print(f"  Anomaly Type: {row['Anomaly_Type']}")

        if row["Retransmission"]:
            print("  Issue: Retransmission detected.")
            print("  Tip: Check for network congestion or packet loss.")
        if row["Reset_Flag"]:
            print("  Issue: TCP Reset flag observed.")
            print("  Tip: Verify application behavior and potential connection issues.")
        if row["Anomaly_Type"] == "High Latency":
            print("  Reason: Packet timing suggests unusually high latency.")
            print("  Tip: Investigate potential network congestion or overloaded servers.")
        if row["Anomaly_Type"] == "Unexpected Protocol":
            print("  Reason: Detected protocol is unexpected or unknown.")
            print(
                "  Tip: Validate protocol usage and ensure no misconfigurations "
                "or unauthorized traffic."
            )
        if row["Anomaly_Type"] == "Malformed Packet":
            print("  Reason: Malformed packet with missing or invalid address information.")
            print("  Tip: Inspect capture details for errors or corrupted data.")


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
# MAIN — Command-line entry point
# ==============================================================================

if __name__ == "__main__":
    pcap_file = input("Enter the path to the Wireshark capture file (.pcap): ")

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
