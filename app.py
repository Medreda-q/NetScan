"""
app.py — NetScan Streamlit Dashboard
=====================================
Interactive front-end for the dual-layer network anomaly detection pipeline.

PERFORMANCE NOTE (important for the live demo):
-----------------------------------------------
Parsing a .pcap file with pyshark can take 10–30 seconds depending on size.
We use @st.cache_data on the pcap-parsing step so that:
  - The first run parses the file and caches the result in memory.
  - Moving the window-size slider ONLY re-runs aggregate_windows() +
    detect_window_anomalies(), which takes milliseconds.
  - Re-parsing is only triggered when a NEW file is uploaded.

This means the demo slider is fast and responsive even on large captures.

Run with:
    streamlit run app.py
"""

import asyncio
import os
import tempfile

import matplotlib
# Use the non-interactive Agg backend so matplotlib renders to PNG buffers
# instead of trying to open a GUI window. Required for Streamlit compatibility.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Windows asyncio fix — must be set before importing pyshark
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Import our detection functions from the main script
from WiresharkAbnormality import (
    extract_features,
    detect_anomalies,
    aggregate_windows,
    detect_window_anomalies,
    get_available_interfaces,
    capture_live_packets,
    calibrate_baseline,
    score_monitoring_window,
    PACKET_COLUMNS,
    WINDOW_FEATURE_COLS,
)


def highlight_type(val):
    """Color-code anomaly types for Streamlit table display."""
    color_map = {
        "Port Scan": "background-color: rgba(248,113,113,0.25); color: #fca5a5; font-weight: 600;",
        "Flood / DDoS": "background-color: rgba(251,146,60,0.25); color: #fdba74; font-weight: 600;",
        "Normal": "",
    }
    return color_map.get(val, "")


def apply_anomaly_style(df, display_cols):
    """
    Safely apply highlight_type styling using .map() (pandas >= 2.1)
    with backward-compatible fallback to .applymap().
    """
    styler = df[display_cols].style
    if hasattr(styler, "map"):
        return styler.map(highlight_type, subset=["Anomaly_Type"])
    return styler.applymap(highlight_type, subset=["Anomaly_Type"])

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="NetScan — Network Anomaly Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# STYLING
# ──────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Hero header ── */
    .hero {
        background: linear-gradient(135deg, #0d0d1a 0%, #1a1040 50%, #0d1a2e 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 18px;
        padding: 2.5rem 2.5rem 2rem;
        margin-bottom: 1.8rem;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.5px;
    }
    .hero p {
        color: rgba(255,255,255,0.55);
        font-size: 0.9rem;
        margin: 0;
        line-height: 1.6;
    }
    .hero .badge {
        display: inline-block;
        background: rgba(139,92,246,0.2);
        border: 1px solid rgba(139,92,246,0.4);
        color: #c4b5fd;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        margin-bottom: 0.8rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* ── Summary banner ── */
    .banner {
        border-radius: 14px;
        padding: 1.4rem 1.8rem;
        margin-bottom: 1.6rem;
        border: 1px solid transparent;
    }
    .banner-danger {
        background: linear-gradient(135deg, rgba(239,68,68,0.12) 0%, rgba(239,68,68,0.04) 100%);
        border-color: rgba(239,68,68,0.3);
    }
    .banner-safe {
        background: linear-gradient(135deg, rgba(34,197,94,0.12) 0%, rgba(34,197,94,0.04) 100%);
        border-color: rgba(34,197,94,0.3);
    }
    .banner h3 {
        margin: 0 0 1rem 0;
        color: #fff;
        font-size: 1.05rem;
        font-weight: 600;
    }
    .chips {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
    }
    .chip {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 0.6rem 1rem;
        min-width: 120px;
        text-align: center;
    }
    .chip .val {
        font-size: 1.6rem;
        font-weight: 700;
        display: block;
        line-height: 1.1;
    }
    .chip .lbl {
        font-size: 0.72rem;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.15rem;
        display: block;
    }
    .val-danger { color: #f87171; }
    .val-orange { color: #fb923c; }
    .val-warn   { color: #fbbf24; }
    .val-safe   { color: #4ade80; }
    .val-blue   { color: #60a5fa; }

    /* ── Info callout ── */
    .info-box {
        background: rgba(99,102,241,0.09);
        border-left: 3px solid #6366f1;
        border-radius: 0 8px 8px 0;
        padding: 0.75rem 1rem;
        margin: 0.8rem 0;
        font-size: 0.82rem;
        color: rgba(255,255,255,0.7);
        line-height: 1.5;
    }
    .info-box b { color: #a5b4fc; }

    /* ── Tab tweak ── */
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        font-size: 0.9rem;
    }

    /* ── Sidebar tweaks ── */
    section[data-testid="stSidebar"] {
        background: #0d0d1a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ──────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="hero">
        <div class="badge">🛡️ DUT Cybersecurity — Soutenance Project</div>
        <h1>NetScan — Network Anomaly Detector</h1>
        <p>
            Dual-layer unsupervised ML pipeline: per-packet Isolation Forest (Length + Timestamp)
            and time-windowed behavioral analysis (port diversity, packet volume, SYN flood signals).
            Detects port scans, DDoS / flood attempts, and packet-level anomalies without predefined signatures.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR — upload + controls
# ──────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Controls")

    uploaded_file = st.file_uploader(
        "Upload a .pcap / .pcapng file",
        type=["pcap", "pcapng"],
        help="Wireshark capture file to analyze",
    )

    st.markdown("---")
    st.markdown("### 🪟 Window Settings")

    window_size = st.slider(
        "Time window size (seconds)",
        min_value=1,
        max_value=30,
        value=5,
        step=1,
        help=(
            "Packets from the same source are grouped into buckets of this duration. "
            "Small windows (1–3 s) catch fast, aggressive scans. "
            "Large windows (15–30 s) catch slow, stealthy scans."
        ),
    )

    st.markdown(
        """
        <div class="info-box">
            <b>Demo tip:</b> drag the slider and watch the window scatter plot update
            instantly — the pcap is parsed only <b>once</b> (cached), so changing the
            window size re-runs only the fast aggregation step.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 📐 Model Parameters")
    st.caption("Layer 1 (per-packet): contamination = 0.05")
    st.caption("Layer 2 (per-window): contamination = 0.10")
    st.markdown(
        """
        <div class="info-box">
            <b>Why different contamination?</b><br>
            At packet level, ~5 % noise is a safe estimate for typical traffic.
            At window level, a capture with an active scan might have 10–20 %
            of windows that are malicious — so we use 10 % to avoid missing them.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("NetScan v2.0 — Soutenance Oct 2026")

# ──────────────────────────────────────────────────────────────────────────────
# CACHED PCAP PARSING
# ──────────────────────────────────────────────────────────────────────────────


@st.cache_data(show_spinner="📦 Parsing .pcap file with pyshark — please wait...")
def load_and_detect_packets(file_bytes: bytes, _filename: str) -> pd.DataFrame:
    """
    Parse the uploaded .pcap and run Layer 1 (per-packet) detection.

    @st.cache_data caches the return value based on the function arguments.
    Since file_bytes changes only when a new file is uploaded, this expensive
    operation (pyshark subprocess + packet loop) runs at most ONCE per file.
    Moving the window slider does NOT trigger a re-parse.

    The _filename argument is prefixed with _ to tell Streamlit not to hash it
    (it's for display purposes only; file_bytes already uniquely identifies the file).

    Parameters
    ----------
    file_bytes : raw bytes of the uploaded file
    _filename  : original filename (for display only, not used for caching key)

    Returns
    -------
    Fully annotated per-packet DataFrame (with Anomaly and Anomaly_Type columns).
    """
    # pyshark requires a file path — write bytes to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        raw_df = extract_features(tmp_path)
        analyzed_df = detect_anomalies(raw_df)
    finally:
        # Always clean up the temp file, even if an exception occurs
        os.unlink(tmp_path)

    return analyzed_df


# ──────────────────────────────────────────────────────────────────────────────
# OFFLINE PCAP PROCESSING (if file uploaded)
# ──────────────────────────────────────────────────────────────────────────────

packet_df = None
window_df = None

if uploaded_file is not None:
    # Layer 1 — cached (runs only when a new file is uploaded)
    packet_df = load_and_detect_packets(uploaded_file.getvalue(), uploaded_file.name)

    # Layer 2 — fast (runs every time window_size slider changes)
    with st.spinner(
        f"🔎 Aggregating into {window_size}s windows and scoring behavioral anomalies..."
    ):
        window_df = aggregate_windows(packet_df, window_size=window_size)
        window_df = detect_window_anomalies(window_df)

    # ── Offline Summary Banner ──
    port_scans  = int((window_df["Anomaly_Type"] == "Port Scan").sum())
    floods      = int((window_df["Anomaly_Type"] == "Flood / DDoS").sum())
    pkt_anomaly = int((packet_df["Anomaly"] == -1).sum())
    total_pkts  = len(packet_df)
    total_wins  = len(window_df)

    is_safe = port_scans == 0 and floods == 0
    banner_cls = "banner banner-safe" if is_safe else "banner banner-danger"
    status_icon = "✅" if is_safe else "🚨"
    status_msg = (
        "No behavioral anomalies detected — capture appears clean"
        if is_safe
        else "Threats detected — review the Per-Window tab for details"
    )

    st.markdown(
        f"""
        <div class="{banner_cls}">
            <h3>{status_icon} Offline Capture Analysis: {uploaded_file.name} — {status_msg}</h3>
            <div class="chips">
                <div class="chip">
                    <span class="val {'val-danger' if port_scans > 0 else 'val-safe'}">{port_scans}</span>
                    <span class="lbl">Port Scan Windows</span>
                </div>
                <div class="chip">
                    <span class="val {'val-orange' if floods > 0 else 'val-safe'}">{floods}</span>
                    <span class="lbl">Flood / DDoS Windows</span>
                </div>
                <div class="chip">
                    <span class="val {'val-warn' if pkt_anomaly > 0 else 'val-safe'}">{pkt_anomaly:,}</span>
                    <span class="lbl">Anomalous Packets</span>
                </div>
                <div class="chip">
                    <span class="val val-blue">{total_pkts:,}</span>
                    <span class="lbl">Total Packets</span>
                </div>
                <div class="chip">
                    <span class="val val-blue">{total_wins:,}</span>
                    <span class="lbl">Time Windows ({window_size}s)</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────────────────────────────────────
# TABS: Live Monitoring + Offline Forensic Layers
# ──────────────────────────────────────────────────────────────────────────────

tab_live, tab1, tab2 = st.tabs(
    [
        "📡  Live Monitoring (Calibrate & Detect)",
        "📦  Per-Packet Analysis  (Layer 1 — offline)",
        "🪟  Per-Window Behavioral Analysis  (Layer 2 — offline)",
    ]
)

# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ TAB 0 — Live Calibrate-Then-Monitor Surveillance                           │
# └─────────────────────────────────────────────────────────────────────────────┘

with tab_live:
    st.subheader("Live Calibrate-Then-Monitor Network Surveillance")
    st.markdown(
        """
        **Phase 1 — Calibration**: Sniffs live network traffic to establish this session's normal behavioral baseline
        using an unsupervised Isolation Forest model (`contamination=0.10`).  
        **Phase 2 — Continuous Monitoring**: Evaluates live traffic in sliding time windows against the
        calibrated baseline and flags suspected Port Scans or Floods in real-time.  
        *Note: Detection and reporting only — network traffic is NOT blocked or dropped.*
        """
    )

    # Initialize session state tracking
    if "live_monitoring_active" not in st.session_state:
        st.session_state.live_monitoring_active = False
    if "live_baseline_calibrated" not in st.session_state:
        st.session_state.live_baseline_calibrated = False
    if "live_scaler" not in st.session_state:
        st.session_state.live_scaler = None
    if "live_model" not in st.session_state:
        st.session_state.live_model = None
    if "live_flagged_rows" not in st.session_state:
        st.session_state.live_flagged_rows = []
    if "live_total_windows" not in st.session_state:
        st.session_state.live_total_windows = 0
    if "live_total_packets" not in st.session_state:
        st.session_state.live_total_packets = 0

    c_iface, c_dur, c_win = st.columns([2, 1, 1])
    with c_iface:
        available_ifaces = get_available_interfaces()
        iface_options = ["Default Interface"] + available_ifaces + ["Custom Interface..."]
        selected_option = st.selectbox(
            "Network Interface",
            options=iface_options,
            help="Select the network adapter to monitor.",
        )
        if selected_option == "Custom Interface...":
            live_interface = st.text_input("Interface Name / Index:", value="eth0")
        elif selected_option == "Default Interface":
            live_interface = None
        else:
            live_interface = selected_option

    with c_dur:
        live_calib_duration = st.slider(
            "Calibration Duration (s)",
            min_value=10,
            max_value=300,
            value=120,
            step=5,
            help="Time allocated for Phase 1 to learn normal traffic patterns.",
        )

    with c_win:
        live_window_size = st.slider(
            "Monitoring Window (s)",
            min_value=1,
            max_value=30,
            value=5,
            step=1,
            help="Evaluation window size for Phase 2 continuous scoring.",
        )

    col_btn1, col_btn2, _ = st.columns([1.2, 1.2, 3])
    with col_btn1:
        if not st.session_state.live_monitoring_active:
            if st.button("🚀 Start Live Monitoring", type="primary", use_container_width=True):
                st.session_state.live_monitoring_active = True
                st.session_state.live_baseline_calibrated = False
                st.session_state.live_flagged_rows = []
                st.session_state.live_total_windows = 0
                st.session_state.live_total_packets = 0
                st.rerun()

    with col_btn2:
        if st.session_state.live_monitoring_active:
            if st.button("⏹️ Stop Monitoring", use_container_width=True):
                st.session_state.live_monitoring_active = False
                st.rerun()

    live_status_container = st.empty()
    live_progress_container = st.empty()
    live_metrics_container = st.empty()
    live_table_container = st.empty()

    if st.session_state.live_monitoring_active:
        # Phase 1: If baseline not yet calibrated, run calibration
        if not st.session_state.live_baseline_calibrated:
            live_status_container.info(
                f"⏳ **Phase 1 — Calibration in progress:** Capturing live traffic for {live_calib_duration}s..."
            )
            progress_bar = live_progress_container.progress(0.0)

            # Test interface before entering loop
            try:
                test_pkts = capture_live_packets(interface=live_interface, timeout=0.5)
            except (PermissionError, RuntimeError) as pe:
                st.session_state.live_monitoring_active = False
                live_status_container.empty()
                live_progress_container.empty()
                st.error(
                    f"⚠️ **Live Packet Capture Permission / Driver Error**\n\n"
                    f"{str(pe)}\n\n"
                    f"**Required Actions:**\n"
                    f"- **Windows**: Install [Npcap](https://npcap.com) with *'WinPcap API-compatible Mode'* enabled, "
                    f"ensure the driver service is running (`net start npcap`), and run your IDE/terminal as Administrator.\n"
                    f"- **Linux / macOS**: Run with elevated permissions: `sudo streamlit run app.py`"
                )
                st.stop()
            except Exception as e:
                st.session_state.live_monitoring_active = False
                live_status_container.empty()
                live_progress_container.empty()
                st.error(f"Failed to start capture: {e}")
                st.stop()

            # Execute calibration loop
            calib_start = time.time()
            calib_buffer = []
            if not test_pkts.empty:
                calib_buffer.append(test_pkts)

            slice_sec = min(2, max(1, live_window_size))
            while True:
                elapsed = time.time() - calib_start
                remaining = max(0, int(live_calib_duration - elapsed))
                frac = min(1.0, elapsed / live_calib_duration)
                progress_bar.progress(frac)
                total_pkts_buffered = sum(len(df) for df in calib_buffer)
                live_status_container.info(
                    f"⏳ **Phase 1 — Learning normal traffic...** `{remaining}s remaining` "
                    f"({total_pkts_buffered:,} packets buffered)"
                )

                if elapsed >= live_calib_duration:
                    break

                step_timeout = min(slice_sec, remaining) if remaining > 0 else 1
                try:
                    pkts = capture_live_packets(interface=live_interface, timeout=step_timeout)
                    if not pkts.empty:
                        calib_buffer.append(pkts)
                except Exception as cap_err:
                    st.session_state.live_monitoring_active = False
                    st.error(f"Error during packet capture: {cap_err}")
                    st.stop()

            all_calib_df = (
                pd.concat(calib_buffer, ignore_index=True)
                if calib_buffer
                else pd.DataFrame(columns=PACKET_COLUMNS)
            )
            scaler, baseline_model, calib_wins = calibrate_baseline(
                all_calib_df, window_size=live_window_size
            )
            st.session_state.live_scaler = scaler
            st.session_state.live_model = baseline_model
            st.session_state.live_baseline_calibrated = True
            live_progress_container.empty()
            live_status_container.success(
                f"✅ **Phase 1 Complete:** Baseline calibrated on {len(all_calib_df):,} packets "
                f"across {len(calib_wins):,} behavioral window(s). Entering Phase 2..."
            )
            time.sleep(1.0)
            st.rerun()

        # Phase 2: Continuous monitoring
        else:
            live_status_container.success(
                f"🟢 **Phase 2 — Continuous Monitoring Active** (evaluating every {live_window_size}s on "
                f"`{live_interface or 'default'}`). Reporting anomalies in real-time."
            )

            # Capture one monitoring window
            try:
                window_pkts = capture_live_packets(interface=live_interface, timeout=live_window_size)
                scored_win = score_monitoring_window(
                    window_pkts,
                    st.session_state.live_scaler,
                    st.session_state.live_model,
                    window_size=live_window_size,
                )
                st.session_state.live_total_windows += 1
                st.session_state.live_total_packets += len(window_pkts)

                anomalies = scored_win[scored_win["Anomaly"] == -1]
                now_str = time.strftime("%H:%M:%S")
                if not anomalies.empty:
                    for _, row in anomalies.iterrows():
                        rec = row.to_dict()
                        rec["timestamp_str"] = now_str
                        st.session_state.live_flagged_rows.append(rec)
                        st.toast(
                            f"🚨 Anomaly Flagged: {row['Anomaly_Type']} from {row['Src_Address']}!",
                            icon="🚨",
                        )

            except Exception as e_mon:
                st.session_state.live_monitoring_active = False
                st.error(f"Monitoring stopped due to error: {e_mon}")
                st.stop()

    # Render metrics and table whenever there is monitoring activity or history
    if st.session_state.live_baseline_calibrated or st.session_state.live_flagged_rows:
        flagged_df = pd.DataFrame(st.session_state.live_flagged_rows)
        scans_count = int((flagged_df["Anomaly_Type"] == "Port Scan").sum()) if not flagged_df.empty else 0
        floods_count = int((flagged_df["Anomaly_Type"] == "Flood / DDoS").sum()) if not flagged_df.empty else 0

        with live_metrics_container.container():
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Windows Monitored", st.session_state.live_total_windows)
            m2.metric("Total Live Packets", f"{st.session_state.live_total_packets:,}")
            m3.metric("Port Scans Flagged", scans_count)
            m4.metric("Floods / DDoS Flagged", floods_count)

        with live_table_container.container():
            st.markdown("### 📋 Live Detected Anomalies Log")
            if flagged_df.empty:
                st.info("No anomalies detected yet — evaluated traffic conforms to the calibrated baseline.")
            else:
                display_cols_live = [
                    c for c in [
                        "timestamp_str", "Src_Address", "time_window", "packet_count",
                        "unique_dst_ports", "unique_dst_ips", "syn_count", "avg_packet_length", "Anomaly_Type",
                    ] if c in flagged_df.columns
                ]
                styled_live = apply_anomaly_style(flagged_df, display_cols_live)
                st.dataframe(styled_live, use_container_width=True, height=280)

                csv_live = flagged_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download live_detected_anomalies.csv",
                    data=csv_live,
                    file_name="live_detected_anomalies.csv",
                    mime="text/csv",
                )

    if st.session_state.live_monitoring_active and st.session_state.live_baseline_calibrated:
        # Loop for continuous real-time streaming
        time.sleep(0.5)
        st.rerun()


# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ TAB 1 — Per-Packet (Offline)                                               │
# └─────────────────────────────────────────────────────────────────────────────┘

with tab1:
    st.subheader("Layer 1 — Per-Packet Anomaly Detection")

    st.markdown(
        """
        **Model**: Isolation Forest on `Length` + `Timestamp` (contamination = 0.05)  
        **What it finds**: individual packets that are statistically unusual in
        size or timing — retransmissions, TCP resets, oversized frames, high-latency bursts.  
        **What it misses**: port scans — every individual probe packet is normal-sized
        and arrives at a plausible time. This gap is addressed in Layer 2 (next tab).
        """
    )

    if uploaded_file is None:
        st.info("👆 Upload a **.pcap** file in the sidebar to run offline Layer 1 analysis.")
    else:
        col_plot, col_stats = st.columns([3, 1])

        # ── Scatter plot ──────────────────────────────────────────────────────────
        with col_plot:
            fig1, ax1 = plt.subplots(figsize=(11, 5))
            fig1.patch.set_facecolor("#0d1117")
            ax1.set_facecolor("#0d1117")

            # Palette matching original script colors
            anomaly_colors = {
                "Retransmission":     "#fb923c",
                "Reset Flag":         "#f87171",
                "High Packet Length": "#fbbf24",
                "High Latency":       "#4ade80",
                "Unexpected Protocol":"#c084fc",
                "Malformed Packet":   "#92400e",
                "Other":              "#e879f9",
            }

            normal = packet_df[packet_df["Anomaly"] == 1]
            abnormal = packet_df[packet_df["Anomaly"] == -1]

            ax1.scatter(
                normal.index, normal["Length"],
                color="#3b82f6", s=3, alpha=0.35, label="Normal", zorder=1,
            )

            for atype, grp in abnormal.groupby("Anomaly_Type"):
                ax1.scatter(
                    grp.index, grp["Length"],
                    color=anomaly_colors.get(atype, "#94a3b8"),
                    s=18, alpha=0.95, label=atype, zorder=3, edgecolors="white", linewidths=0.3,
                )

            ax1.set_title(
                "Packet Length vs. Index  (Layer 1 — per-packet anomalies)",
                color="white", pad=12, fontsize=11,
            )
            ax1.set_xlabel("Packet Index", color="#94a3b8")
            ax1.set_ylabel("Packet Length (bytes)", color="#94a3b8")
            ax1.tick_params(colors="#94a3b8")
            for spine in ax1.spines.values():
                spine.set_edgecolor("#1e293b")
            ax1.grid(True, alpha=0.12, color="#334155")
            ax1.legend(
                loc="upper right", fontsize=8,
                facecolor="#0f172a", edgecolor="#334155", labelcolor="white",
            )
            fig1.tight_layout(pad=1.5)
            st.pyplot(fig1)
            plt.close(fig1)

        # ── Stats column ──────────────────────────────────────────────────────────
        with col_stats:
            st.metric("Anomalous Packets", pkt_anomaly)
            st.metric("Normal Packets", total_pkts - pkt_anomaly)
            st.markdown("---")

            if pkt_anomaly > 0:
                st.markdown("**Breakdown by type**")
                type_counts = (
                    packet_df[packet_df["Anomaly"] == -1]["Anomaly_Type"]
                    .value_counts()
                    .rename("Count")
                )
                st.dataframe(type_counts, use_container_width=True)
            else:
                st.success("No per-packet anomalies detected.")

        # ── Table ─────────────────────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("Flagged Packets")

        anomaly_pkt_df = packet_df[packet_df["Anomaly"] == -1].copy()

        if anomaly_pkt_df.empty:
            st.info("No anomalous packets found.")
        else:
            st.dataframe(
                anomaly_pkt_df[
                    [
                        "Protocol", "Length", "Src_Address", "Dst_Address",
                        "Src_Port", "Dst_Port", "Timestamp",
                        "Retransmission", "Reset_Flag", "SYN_Flag", "Anomaly_Type",
                    ]
                ],
                use_container_width=True,
                height=320,
            )

            csv_bytes = anomaly_pkt_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️  Download analyzed_capture_packets.csv",
                data=csv_bytes,
                file_name="analyzed_capture_packets.csv",
                mime="text/csv",
            )


# ┌─────────────────────────────────────────────────────────────────────────────┐
# │ TAB 2 — Per-Window Behavioral (Offline)                                     │
# └─────────────────────────────────────────────────────────────────────────────┘

with tab2:
    st.subheader(f"Layer 2 — Windowed Behavioral Detection  (window = {window_size} s)")

    st.markdown(
        f"""
        **Model**: Isolation Forest on 5 behavioral features aggregated per
        *(source IP, {window_size}s window)* group (contamination = 0.10).  
        **Features**: `packet_count`, `unique_dst_ports`, `unique_dst_ips`,
        `syn_count`, `avg_packet_length`  
        **Labels**: *Port Scan* (port diversity ratio > 0.5) · *Flood/DDoS* (high volume, concentrated target)  
        **Key insight**: a port scanner contacts hundreds of unique ports in seconds —
        invisible per-packet, obvious in aggregate.
        """
    )

    if uploaded_file is None:
        st.info("👆 Upload a **.pcap** file in the sidebar to run offline Layer 2 behavioral analysis.")
    else:
        col_plot2, col_stats2 = st.columns([3, 1])

        # ── Behavioral scatter ────────────────────────────────────────────────────
        with col_plot2:
            fig2, ax2 = plt.subplots(figsize=(11, 5))
            fig2.patch.set_facecolor("#0d1117")
            ax2.set_facecolor("#0d1117")

            win_colors = {
                "Normal":       ("#3b82f6", 0.3,  8),
                "Port Scan":    ("#f87171", 0.92, 80),
                "Flood / DDoS": ("#fb923c", 0.92, 80),
            }

            max_len = window_df["avg_packet_length"].max() or 1

            for label, grp in window_df.groupby("Anomaly_Type"):
                c, alpha, base_s = win_colors.get(label, ("#94a3b8", 0.6, 30))
                sizes = (grp["avg_packet_length"] / max_len * base_s + 8).fillna(10)
                ax2.scatter(
                    grp["packet_count"],
                    grp["unique_dst_ports"],
                    c=c, alpha=alpha, s=sizes, label=label,
                    edgecolors="white" if label != "Normal" else "none",
                    linewidths=0.4,
                    zorder=3 if label != "Normal" else 1,
                )

            ax2.set_title(
                f"Behavioral Profile per Source / {window_size}s Window  (Layer 2)\n"
                "X = packet volume · Y = port diversity · size ∝ avg packet length",
                color="white", pad=12, fontsize=10,
            )
            ax2.set_xlabel("Packet Count (per source per window)", color="#94a3b8")
            ax2.set_ylabel("Unique Destination Ports", color="#94a3b8")
            ax2.tick_params(colors="#94a3b8")
            for spine in ax2.spines.values():
                spine.set_edgecolor("#1e293b")
            ax2.grid(True, alpha=0.12, color="#334155")
            ax2.legend(
                loc="upper right", fontsize=9,
                facecolor="#0f172a", edgecolor="#334155", labelcolor="white",
            )
            fig2.tight_layout(pad=1.5)
            st.pyplot(fig2)
            plt.close(fig2)

        # ── Stats column ──────────────────────────────────────────────────────────
        with col_stats2:
            st.metric("Total Windows", total_wins)
            st.metric("Port Scan Windows", port_scans)
            st.metric("Flood / DDoS Windows", floods)
            st.markdown("---")

            if port_scans + floods > 0:
                st.markdown("**Flagged source IPs**")
                flagged_srcs = (
                    window_df[window_df["Anomaly"] == -1]
                    .groupby(["Src_Address", "Anomaly_Type"])
                    .agg(
                        windows=("packet_count", "count"),
                        max_ports=("unique_dst_ports", "max"),
                        max_pkts=("packet_count", "max"),
                    )
                    .reset_index()
                )
                st.dataframe(flagged_srcs, use_container_width=True, height=220)
            else:
                st.success("No behavioral anomalies detected.")

        # ── Explanation of axes ───────────────────────────────────────────────────
        with st.expander("📖 How to read this plot (for the jury)"):
            st.markdown(
                """
                Each point on the scatter represents **one source IP in one time window**
                (e.g., IP `192.168.1.5` from second 10 to second 15).

                | Quadrant | Interpretation |
                |---|---|
                | **Bottom-left** (low X, low Y) | Normal host — few packets, few ports |
                | **Top-left** (low X, high Y) | **Port scan** — many unique ports, moderate volume (e.g. slow nmap) |
                | **Bottom-right** (high X, low Y) | **Flood / DDoS** — high volume, concentrated target |
                | **Top-right** (high X, high Y) | Aggressive scan + flood combined |

                **Point size** is proportional to the average packet length in that window.
                A large point in the flood quadrant suggests an **amplification attack**
                (few targets, very large packets — e.g. DNS or NTP amplification).

                **Why Isolation Forest?**
                Isolation Forest randomly partitions the feature space. A port-scanning
                source with 1,935 unique destination ports is trivially isolated from the
                bulk of normal sources (which have 1–5 ports). The model assigns it an
                anomaly score without needing any labelled attack data.
                """
            )

        # ── Table ─────────────────────────────────────────────────────────────────
        st.markdown("---")
        st.subheader("All Behavioral Window Profiles")

        display_cols = [
            "Src_Address", "time_window", "packet_count", "unique_dst_ports",
            "unique_dst_ips", "syn_count", "avg_packet_length", "Anomaly_Type",
        ]

        # Use safe apply_anomaly_style helper (Bug 4 fix: returns css and uses .map with fallback)
        styled = apply_anomaly_style(window_df, display_cols)
        st.dataframe(styled, use_container_width=True, height=340)

        # Download
        anomaly_win_df = window_df[window_df["Anomaly"] == -1]
        csv_win = anomaly_win_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️  Download analyzed_capture_windows.csv",
            data=csv_win,
            file_name="analyzed_capture_windows.csv",
            mime="text/csv",
        )

