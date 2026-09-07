# NetScan — Network Anomaly Detection and Analysis

NetScan is an unsupervised machine learning network intrusion and anomaly detection platform developed by **Mohamed Reda QIYAOUI** as part of a **DUT Cybersecurity Stage d'Initiation** (Septembre 2026). It combines offline `.pcap` forensic inspection with a live **Calibrate-Then-Monitor** surveillance mode to detect microscopic packet malformations and macroscopic multi-host attacks (such as stealth TCP SYN port scans and volumetric DDoS floods).

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
### 4. Intrusion Prevention System (IPS) & Active Defense
- **Automated Host Quarantine**: When activated, hostile IP addresses flagged for port scans or DDoS floods are instantly contained at the OS firewall level (`Windows Advanced Firewall` via `netsh` or `Linux iptables`).
- **Quarantine Registry & Unblock**: Centralized registry tracking quarantined hosts, attack vectors, and timestamps, with 1-click unblock capabilities and whitelist protection (`127.0.0.1`, loopback).

### 5. SOC Alerting & SIEM Integration
- **Real-Time Discord Webhooks**: Streams rich embeds containing threat classification, source IP, targeted port diversity, packet volume, and containment status directly to Discord or SIEM endpoints.
- **Executive Forensic Report Export (PDF / HTML)**: 1-click generation of professional executive incident reports complete with KPI cards, threat actor breakdowns, firewall actions, and NIST/CIS remediation guidance, printable to PDF.

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
- **Linux / macOS**: Run scripts with elevated permissions (`sudo python detection_engine.py` or `sudo streamlit run dashboard.py`).

---

## Usage

### 1. Unified Kali-Style Terminal Launcher (Recommended)
NetScan includes a self-bootstrapping terminal launcher that automatically checks and installs missing dependencies and validates packet capture drivers (Npcap on Windows, libpcap/root on Linux):

```bash
# Windows
netscan.bat
# or
python netscan.py

# Linux / Kali
chmod +x netscan.sh
sudo ./netscan.sh
```

**Quick CLI flags:**
- `python netscan.py` — Interactive menu (Live surveillance, PCAP forensics, Dashboard, Diagnostics, IPS quarantine, Discord test, Report generator)
- `python netscan.py --live` — Directly start live network capture
- `python netscan.py --pcap sample_nmap_attack.pcap` — Directly run offline forensic inspection
- `python netscan.py --dashboard` — Directly launch the Streamlit web dashboard
- `python netscan.py --check` — Run system and driver diagnostics

### 2. Interactive Streamlit Dashboard
Launch the web interface directly:
```bash
streamlit run dashboard.py
```
The dashboard features four comprehensive modules:
- **📦 Analyse de Capture (PCAP)**: Upload `.pcap` files for deep microscopic (Layer 1) and macroscopic (Layer 2) behavioral analysis, with instant Executive HTML/PDF incident report export.
- **📡 Surveillance Réseau en Direct (Live)**: Real-time Calibrate-Then-Monitor surveillance with countdowns, live anomaly logging, automated firewall blocks, and Discord alerts.
- **🛡️ Pare-feu & Confinement (IPS)**: Active intrusion prevention mode toggle, manual quarantine, registry of blocked rules, and unblock actions.
- **🔔 Alertes & Intégrations SIEM**: Configure and test Discord webhooks with live visual embed previews.

### 3. Core Engine CLI
Run the core detection script directly:
```bash
python detection_engine.py
```


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

### 4. `incident_audit_report.csv` & `alerts_history.json` (Security Operations Center Audit Trail)
Exported from the **🔔 Incident Notification Center** tab. Provides a comprehensive persistent audit log of all historical security incidents, severity ratings (`CRITICAL`, `HIGH`, `MEDIUM`), mathematical threat signatures, and recommended firewall mitigation commands.

---

## Verification & Tests

Run the included validation suites:
```bash
# Verify imports, synthetic detection, and aggregation logic
python test_smoke.py

# Verify end-to-end detection on authentic forensic capture (sample_nmap_attack.pcap)
python test_detection_pcap.py
```

## Author & Copyright

- **Author**: Mohamed Reda QIYAOUI
- **Project**: DUT Cybersecurity — Stage d'Initiation (Septembre 2026)
- **License**: MIT License. Copyright © 2026 Mohamed Reda QIYAOUI. All rights reserved.

