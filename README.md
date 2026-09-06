# NetScan — Network Anomaly Detection and Analysis

NetScan is an unsupervised machine learning network intrusion and anomaly detection platform developed for the DUT Cybersecurity soutenance project. It combines offline `.pcap` forensic inspection with a live **Calibrate-Then-Monitor** surveillance mode to detect microscopic packet malformations and macroscopic multi-host attacks (such as stealth TCP SYN port scans and volumetric DDoS floods).

---

## Detection Architecture

NetScan operates across three complementary detection tiers:

### 1. Layer 1 — Per-Packet Anomaly Detection (Microscopic)
- **Model**: Isolation Forest (`contamination=0.05`, `random_state=42`)
- **Features**: `Length` + `Timestamp` (normalized with `StandardScaler`)
- **Detects**: Outlier frames in payload size or inter-arrival timing:
  - **Retransmission**: Detected TCP packet retransmissions
  - **Reset Flag**: TCP RST flags indicating abrupt session terminations
  - **High Packet Length**: Jumbo or fragmented frames exceeding MTU (1500 bytes)
  - **High Latency**: Abnormally delayed packets (> 95th percentile)
  - **Unexpected Protocol**: Unknown or non-standard protocol types
  - **Malformed Packet**: Frames with missing or invalid IP/MAC addresses

### 2. Layer 2 — Time-Windowed Behavioral Detection (Macroscopic)
- **Model**: Isolation Forest (`contamination=0.10`, `random_state=42`)
- **Aggregation**: Grouped by `(Src_Address, time_window)` with configurable duration (default: 5s)
- **Features**: 5 behavioral metrics:
  - `packet_count`: Volume of packets from the source host
  - `avg_packet_length`: Mean payload size across the window
  - `unique_dst_ports`: Port diversity (number of distinct target ports)
  - `unique_dst_ips`: Host diversity (number of distinct target hosts)
  - `syn_count`: Count of TCP SYN packets without ACK
- **Classification**:
  - **Port Scan**: `unique_dst_ports / packet_count > 0.5` (mathematical signature of sequential port sweeps, e.g. `nmap -sS`)
  - **Flood / DDoS**: Outlier window with low port diversity ratio (`≤ 0.5`)

### 3. Live Calibrate-Then-Monitor Mode (Real-Time Stream Surveillance)
- **Phase 1 — Calibration (default: 120s, configurable)**:
  Captures live traffic from a chosen network interface to learn the session's normal behavioral baseline. Fits and stores a session `StandardScaler` and `IsolationForest` without modifying the global model structure. Shows real-time countdown status: `"Learning normal traffic... X seconds remaining"`.
- **Phase 2 — Continuous Monitoring (every N seconds, default: 5s)**:
  Continuously aggregates live streaming windows, scores them against the Phase 1 calibrated baseline, and flags port scans and floods immediately.
- **Reporting Only**: Detected threats are logged and visualized in real time. Network traffic is **never blocked or dropped**.

---

## Prerequisites & Installation

- Python 3.8+
- Required dependencies:
  ```bash
  pip install pyshark scapy pandas matplotlib scikit-learn streamlit
  ```

### Live Capture Driver Requirements
Packet sniffing on live network interfaces requires elevated privileges:
- **Windows**: Install [Npcap](https://npcap.com) with the option **"Install Npcap in WinPcap API-compatible Mode"** enabled. Ensure the driver service is running (`net start npcap`), and run your terminal or IDE as **Administrator**.
- **Linux / macOS**: Run scripts with elevated permissions (`sudo python WiresharkAbnormality.py` or `sudo streamlit run app.py`).

---

## Usage

### 1. Interactive Streamlit Dashboard (Recommended)
Launch the web interface:
```bash
streamlit run app.py
```
The dashboard features three tabs:
- **📡 Live Monitoring**: Select a network adapter, tune calibration duration and window size, start live surveillance, and observe real-time countdowns and anomaly logs.
- **📦 Per-Packet Analysis (Layer 1)**: Upload a `.pcap` file to visualize packet-level anomalies on an interactive scatter plot.
- **🪟 Per-Window Behavioral Analysis (Layer 2)**: Dynamically adjust time window sizes with the slider to inspect behavioral clusters and port scan detections.

### 2. Command-Line Interface (CLI)
Run the core detection script:
```bash
python WiresharkAbnormality.py
```
You will be prompted to select an operational mode:
- **Option [1] — Live Capture & Monitoring**: Prompts for network interface name, calibration duration (seconds), and window size (seconds). Runs Phase 1 calibration followed by continuous Phase 2 monitoring with real-time alerts.
- **Option [2] — File Analysis Mode**: Prompts for path to an offline `.pcap` capture file (e.g. `NMAP_PROBE.pcap`) and window size, executing full Layer 1 & Layer 2 offline forensics.

---

## CSV Exports

NetScan exports structured forensic CSV files for review and reporting:

### 1. `analyzed_capture_packets.csv` (Layer 1 — Per-Packet Anomalies)
Contains 12 columns:
- `Protocol`: Transport / application layer protocol
- `Length`: Frame length in bytes
- `Src_Address`: Source IP address (or MAC address fallback)
- `Dst_Address`: Destination IP address (or MAC address fallback)
- `Src_Port`: Source port number
- `Dst_Port`: Destination port number
- `Timestamp`: Epoch arrival timestamp
- `Retransmission`: Boolean flag for TCP retransmissions
- `Reset_Flag`: Boolean flag for TCP RST
- `SYN_Flag`: Boolean flag for TCP SYN without ACK
- `Anomaly`: Model score (`-1` = anomaly, `1` = normal)
- `Anomaly_Type`: Descriptive label (`Retransmission`, `Reset Flag`, `High Packet Length`, `High Latency`, `Unexpected Protocol`, `Malformed Packet`, or `Other`)

### 2. `analyzed_capture_windows.csv` (Layer 2 — Behavioral Window Profiles)
Contains 9 columns:
- `Src_Address`: Source IP address
- `time_window`: Epoch bucket start timestamp
- `packet_count`: Number of packets transmitted by source in window
- `avg_packet_length`: Mean packet length in bytes
- `unique_dst_ports`: Count of unique destination ports targeted
- `unique_dst_ips`: Count of unique destination IP addresses targeted
- `syn_count`: Count of unmatched TCP SYN packets
- `Anomaly`: Isolation Forest anomaly label (`-1` = anomalous window, `1` = normal)
- `Anomaly_Type`: Classified behavioral category (`Port Scan`, `Flood / DDoS`, or `Normal`)

### 3. `live_detected_anomalies.csv` (Live Monitoring Alerts)
Exported from the Streamlit Live Monitoring tab, recording all real-time flagged windows with timestamps and behavioral signatures.

---

## Verification & Tests

Run the included validation suites:
```bash
# Verify imports, synthetic detection, and aggregation logic
python smoke_test.py

# Verify end-to-end detection on authentic forensic capture (NMAP_PROBE.pcap)
python test_pcap_detection.py

# Verify live calibration and monitoring logic with synthetic packet streams
python scratch/test_live_logic.py
```

---

## License & Attribution

- Base offline script: [mayanknauni](https://github.com/mayanknauni/Wireshark-Capture-Anomaly-Detection)
- Extensions & Live Monitoring Architecture: DUT Cybersecurity student (Soutenance Octobre 2026)
- Licensed under the MIT License.
