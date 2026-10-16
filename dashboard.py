"""
dashboard.py -- NetScan SOC Command Center
===========================================
Author: Mohamed Reda QIYAOUI
Network Intrusion Detection & Analysis System (NIDS/NIPS)

Interactive front-end for the dual-layer network anomaly detection pipeline.
SOC-style security dashboard with:
  - Dark cyber glassmorphic design (teal/cyan accents, no emojis)
  - Modular UI components & Plotly dark charts
  - 5-metric SOC KPI Command Row
  - Time series of SYN rate (flood spikes in red)
  - Donut chart of attack types (SYN Scan vs SYN Flood vs Normal)
  - Top 10 source IPs bar chart
  - Anomaly score distribution histogram
  - Filterable & sortable alerts table with colored severity badges
  - Live auto-refreshing monitor with pulse animations
  - Kernel firewall rule generation (Windows / Linux)
  - Multilingual internationalisation (FR / EN / ES)
"""

import asyncio
import base64
import json
import logging
import os
import tempfile
import time
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Windows asyncio fix -- must be set before importing pyshark
if os.name == "nt":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

# Import core detection & alerting infrastructure
from alerting import (
    generate_firewall_rule,
    load_config as load_alert_config,
    log_security_event,
    save_config as save_alert_config,
)
from config_loader import get as cfg, load_config as load_app_config, setup_logging
from detection_engine import (
    ALERTS_FILE,
    AUDIT_LOG_FILE,
    PACKET_COLUMNS,
    WINDOW_FEATURE_COLS,
    add_alert,
    aggregate_windows,
    calibrate_baseline,
    capture_live_packets,
    clear_alerts,
    create_alert_record,
    detect_anomalies,
    detect_window_anomalies,
    extract_features,
    get_available_interfaces,
    load_alerts,
    save_alerts,
    score_monitoring_window,
)
from geoip_resolver import resolve_ip_geo
from i18n import get_supported_languages, load_locale, t
from report_generator import generate_html_incident_report
from ui_charts import (
    create_anomaly_score_histogram,
    create_attack_distribution_donut,
    create_layer1_scatter,
    create_syn_timeseries_chart,
    create_top_sources_bar,
)
from ui_components import (
    compute_threat_level,
    render_alerts_table,
    render_empty_state,
    render_header,
    render_kpi_row,
    render_section_header,
    render_skeleton_chart,
    render_skeleton_kpis,
)

# ------------------------------------------------------------------------------
# SYSTEM INITIALISATION & LOGGING
# ------------------------------------------------------------------------------
_app_cfg = load_app_config()
setup_logging()
logger = logging.getLogger(__name__)

LOGO_PNG = os.path.join(os.path.dirname(__file__), "assets", "netscan_logo.png")
LOGO_SVG = os.path.join(os.path.dirname(__file__), "assets", "netscan_logo.svg")
CSS_FILE = os.path.join(os.path.dirname(__file__), "assets", "css", "dashboard.css")

# ------------------------------------------------------------------------------
# INTERNATIONALISATION
# ------------------------------------------------------------------------------
_LANG_DICT = get_supported_languages()
_LANGS = list(_LANG_DICT.keys())
_DEFAULT_LANG = cfg("app.default_language", "fr")

if "lang" not in st.session_state:
    st.session_state["lang"] = _DEFAULT_LANG


def _t(key: str, **kwargs) -> str:
    """Helper for localized strings with fallback."""
    return t(key, lang=st.session_state.get("lang", _DEFAULT_LANG), **kwargs)


def get_logo_data_uri() -> str:
    """Return data URI of NetScan logo for inline HTML."""
    if os.path.exists(LOGO_SVG):
        with open(LOGO_SVG, "rb") as f:
            return f"data:image/svg+xml;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    elif os.path.exists(LOGO_PNG):
        with open(LOGO_PNG, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    return ""


# ------------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLES
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="NetScan -- Intelligent NIDS/IPS Platform",
    page_icon=LOGO_PNG if os.path.exists(LOGO_PNG) else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide Streamlit default chrome
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] { display: none !important; height: 0px !important; }
    .stDeployButton, [data-testid="stDeployButton"] { display: none !important; }
    #MainMenu, [data-testid="stToolbar"], [data-testid="stHeaderActionElements"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load external SOC CSS
if os.path.exists(CSS_FILE):
    with open(CSS_FILE, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# GSAP micro-animations injection
components.html(
    """
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
    <script>
      window.addEventListener("DOMContentLoaded", () => {
        try {
          const parentDoc = window.parent.document;
          const hero = parentDoc.querySelector(".netscan-hero");
          if (hero) gsap.from(hero, { y: -12, opacity: 0, duration: 0.5, ease: "power3.out" });
          const kpis = parentDoc.querySelectorAll(".kpi-card");
          if (kpis.length > 0) gsap.from(kpis, { y: 10, opacity: 0, duration: 0.4, stagger: 0.04, ease: "back.out(1.4)" });
          const panels = parentDoc.querySelectorAll(".threat-card, .glass-panel");
          if (panels.length > 0) gsap.from(panels, { y: 15, opacity: 0, duration: 0.45, stagger: 0.05, ease: "power2.out" });
        } catch (e) {}
      });
    </script>
    """,
    height=0,
)




# ------------------------------------------------------------------------------
# CACHED FORENSIC PCAP PIPELINE
# ------------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_and_detect_packets(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parse PCAP file and run Layer 1 Isolation Forest detection (cached)."""
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        raw_df = extract_features(tmp_path)
        analyzed_df = detect_anomalies(raw_df)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return analyzed_df


# ------------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ------------------------------------------------------------------------------
with st.sidebar:
    # Hero header in sidebar
    _logo_uri = get_logo_data_uri()
    _logo_html = f'<img src="{_logo_uri}" style="width:56px; margin-bottom:0.6rem;" />' if _logo_uri else ''
    st.markdown(
        f'''
        <div class="sidebar-hero">
            {_logo_html}
            <div class="sidebar-hero-title">NetScan<br/>Anomaly Shield</div>
            <div class="sidebar-hero-author">{_t("app_author", default="Mohamed Reda QIYAOUI")}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    st.markdown('<hr style="border-color:rgba(255,255,255,0.06); margin:0.6rem 0 0.8rem;"/>', unsafe_allow_html=True)

    _curr_lang = st.session_state.get('lang', _DEFAULT_LANG)

    _nav_labels = [
        _t('mode_pcap', default='Analyse Forensique PCAP'),
        _t('mode_live', default='Surveillance Live'),
        _t('mode_alerts', default='Centre SOC'),
        _t('mode_audit', default='Audit & IPS'),
        _t('mode_settings', default='Parametres & Langues'),
    ]
    _nav_keys = ['pcap', 'live', 'alerts', 'audit', 'settings']

    _nav_idx = st.radio(
        'Navigation',
        options=range(len(_nav_labels)),
        format_func=lambda i: _nav_labels[i],
        label_visibility='collapsed',
        key='sidebar_nav',
    )
    _active_page = _nav_keys[_nav_idx]


# ==============================================================================
# PAGE 1 : PCAP CAPTURE FORENSICS
# ==============================================================================
if _active_page == 'pcap':
    render_section_header(_t("sec_forensic_title", default="Analyse Forensique de Fichier de Capture (.pcap / .pcapng)"), "FORENSIC ENGINE")
    st.caption(_t("sec_forensic_caption", default="Deposez une capture reseau pour executer l'analyse microscopique par paquet et l'agregation comportementale par fenetres."))

    uploaded_file = st.file_uploader(
        _t("upload_prompt", default="Glissez-deposez ou selectionnez un fichier .pcap / .pcapng"),
        type=["pcap", "pcapng"],
        help=_t("upload_help", default="Formats supportes: .pcap, .pcapng"),
        key="pcap_file_uploader",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        filename = uploaded_file.name

        with st.spinner(f"Analyse en cours sur {filename}..."):
            packet_df = load_and_detect_packets(file_bytes, filename)

        window_size = 5
        with st.spinner(f"Agregation comportementale ({window_size}s)..."):
            window_df = aggregate_windows(packet_df, window_size=window_size)
            window_df = detect_window_anomalies(window_df)

        # ----------------------------------------------------------------------
        # KPI COMPUTATIONS (5 METRICS)
        # ----------------------------------------------------------------------
        total_packets = len(packet_df)
        
        # Calculate duration in seconds for SYN packets/sec
        if "Timestamp" in packet_df.columns and len(packet_df) > 1:
            t_min = float(packet_df["Timestamp"].min())
            t_max = float(packet_df["Timestamp"].max())
            duration_sec = max(1.0, t_max - t_min)
        else:
            duration_sec = max(1.0, len(window_df) * window_size)

        total_syn_pkts = int(packet_df.get("SYN_Flag", 0).sum()) if "SYN_Flag" in packet_df.columns else int(window_df.get("syn_count", 0).sum())
        syn_per_sec = float(total_syn_pkts) / duration_sec

        # Active anomalies/alerts in this capture
        active_anom_windows = window_df[window_df.get("Anomaly", 1) == -1]
        active_alerts_count = len(active_anom_windows)

        # Top attacker IP
        top_attacker = "None"
        if not active_anom_windows.empty and "Src_Address" in active_anom_windows.columns:
            top_attacker = active_anom_windows["Src_Address"].value_counts().index[0]
        elif not packet_df.empty and "Src_Address" in packet_df.columns:
            anom_pkts = packet_df[packet_df.get("Anomaly", 1) == -1]
            if not anom_pkts.empty and "Src_Address" in anom_pkts.columns:
                valid_src = anom_pkts[anom_pkts["Src_Address"] != "N/A"]["Src_Address"]
                if not valid_src.empty:
                    top_attacker = valid_src.value_counts().index[0]

        # Threat Level
        port_scans = int((window_df["Anomaly_Type"] == "Port Scan").sum())
        floods = int((window_df["Anomaly_Type"] == "Flood / DDoS").sum())
        capture_threat = compute_threat_level(critical=floods, high=port_scans, lang=_curr_lang)

        # 1. Render 5-card SOC KPI Row
        render_kpi_row(
            total_packets=total_packets,
            syn_per_sec=syn_per_sec,
            active_alerts=active_alerts_count,
            top_attacker=top_attacker,
            threat_tuple=capture_threat,
            lang=_curr_lang,
        )

        st.write("")

        # ----------------------------------------------------------------------
        # 2. MAIN CHARTS (2x2 GRID)
        # ----------------------------------------------------------------------
        c_row1_left, c_row1_right = st.columns([1.5, 1])
        with c_row1_left:
            fig_syn = create_syn_timeseries_chart(window_df, lang=_curr_lang)
            st.plotly_chart(fig_syn, use_container_width=True, config={"displayModeBar": False})
        with c_row1_right:
            fig_donut = create_attack_distribution_donut(window_df, lang=_curr_lang)
            st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

        c_row2_left, c_row2_right = st.columns([1, 1])
        with c_row2_left:
            fig_top_ips = create_top_sources_bar(packet_df, window_df, top_n=10, lang=_curr_lang)
            st.plotly_chart(fig_top_ips, use_container_width=True, config={"displayModeBar": False})
        with c_row2_right:
            scores_series = packet_df.get("anomaly_score", window_df.get("anomaly_score"))
            fig_hist = create_anomaly_score_histogram(scores_series, lang=_curr_lang)
            st.plotly_chart(fig_hist, use_container_width=True, config={"displayModeBar": False})

        # Microscopic Packet Scatter (Expandable)
        with st.expander(_t("chart_l1_expander", default="Inspection Microscopique par Paquet (Isolation Forest Niveau 1)"), expanded=False):
            fig_l1 = create_layer1_scatter(packet_df, lang=_curr_lang)
            st.plotly_chart(fig_l1, use_container_width=True, config={"displayModeBar": False})

        st.write("")

        # ----------------------------------------------------------------------
        # 3. ALERTS TABLE & REPORT EXPORT
        # ----------------------------------------------------------------------
        render_section_header(_t("sec_alerts_title", default="Registre des Alertes Detectees"), "ALERT DISPATCH")

        # Prepare alerts records from anomalous windows
        pcap_alerts = []
        for _, w in active_anom_windows.iterrows():
            src_addr = str(w.get("Src_Address", "-"))
            geo_info = resolve_ip_geo(src_addr)
            rec = {
                "time": str(w.get("time_window", "-")),
                "source_ip": src_addr,
                "geo_origin": geo_info["display"],
                "target_ip": f"{int(w.get('unique_dst_ips', 1))} cible(s)",
                "attack_type": str(w.get("Anomaly_Type", "Anomalie")),
                "severity": "CRITICAL" if w.get("Anomaly_Type") == "Flood / DDoS" else "HIGH",
                "anomaly_score": round(float(w.get("anomaly_score", -0.85)), 4),
            }
            pcap_alerts.append(rec)

        # Render filterable, sortable alerts table with colored badges
        render_alerts_table(pcap_alerts, key_prefix="pcap_alerts", lang=_curr_lang)

        # Action Buttons: Export Report CSV & Transmit to SOC
        col_btn1, col_btn2, _ = st.columns([1.5, 1.8, 2])
        with col_btn1:
            csv_report = active_anom_windows.to_csv(index=False, sep=";").encode("utf-8-sig")
            st.download_button(
                label=_t("btn_export_csv", default="Exporter Rapport Alertes (CSV)"),
                data=csv_report,
                file_name=f"rapport_alertes_{filename}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with col_btn2:
            if not active_anom_windows.empty:
                if st.button("Transmettre les Alertes au SOC", type="primary", use_container_width=True):
                    added_count = 0
                    for _, a_row in active_anom_windows.iterrows():
                        rec = create_alert_record(
                            src_address=a_row["Src_Address"],
                            anomaly_type=a_row["Anomaly_Type"],
                            packet_count=a_row.get("packet_count", 0),
                            unique_dst_ports=a_row.get("unique_dst_ports", 0),
                            unique_dst_ips=a_row.get("unique_dst_ips", 1),
                            syn_count=a_row.get("syn_count", 0),
                            avg_packet_length=a_row.get("avg_packet_length", 0.0),
                            time_window=a_row.get("time_window"),
                            origin=f"PCAP: {filename}",
                        )
                        add_alert(rec)
                        added_count += 1
                    st.success(f"{added_count} incident(s) transmis au registre SOC !")
                    time.sleep(0.5)
                    st.rerun()

    else:
        # Empty state — no file uploaded yet, show message only
        render_empty_state(
            _t("empty_capture_title", default="En attente d'un fichier de capture"),
            _t("empty_capture_desc", default="Selectionnez ou glissez un fichier .pcap ou .pcapng ci-dessus pour lancer la detection SOC en temps reel."),
        )


# ==============================================================================
# PAGE 2 : LIVE NETWORK SURVEILLANCE
# ==============================================================================
if _active_page == 'live':
    render_section_header(_t("sec_live_title", default="Surveillance Reseau en Temps Reel (Sniffing Continu)"), "REAL-TIME MONITOR")
    st.caption(_t("live_journal", default="Calibration automatique du profil baseline puis inference continue avec rafraichissement automatique (2-3s)."))

    # State tracking
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
        avail_ifaces = get_available_interfaces()
        iface_opts = ["Interface par defaut"] + avail_ifaces + ["Interface personnalisee..."]
        chosen_opt = st.selectbox(_t("live_interface", default="Interface Reseau"), options=iface_opts)
        if chosen_opt == "Interface personnalisee...":
            live_iface = st.text_input("Nom de l'interface :", value="eth0")
        elif chosen_opt == "Interface par defaut":
            live_iface = None
        else:
            live_iface = chosen_opt

    with c_dur:
        calib_dur = st.slider("Duree Calibration (s)", min_value=5, max_value=60, value=15, step=5)

    with c_win:
        win_sz = st.slider("Fenetre d'Analyse (s)", min_value=1, max_value=15, value=5, step=1)

    btn_col1, btn_col2, _ = st.columns([1.2, 1.2, 3])
    with btn_col1:
        if not st.session_state.live_monitoring_active:
            if st.button(_t("live_start", default="Demarrer la Surveillance"), type="primary", use_container_width=True):
                st.session_state.live_monitoring_active = True
                st.session_state.live_baseline_calibrated = False
                st.session_state.live_flagged_rows = []
                st.session_state.live_total_windows = 0
                st.session_state.live_total_packets = 0
                st.rerun()

    with btn_col2:
        if st.session_state.live_monitoring_active:
            if st.button(_t("live_stop", default="Interrompre"), use_container_width=True):
                st.session_state.live_monitoring_active = False
                st.rerun()

    status_box = st.empty()
    prog_box = st.empty()
    live_kpi_box = st.empty()
    live_feed_box = st.empty()

    if st.session_state.live_monitoring_active:
        # Phase 1: Baseline Calibration
        if not st.session_state.live_baseline_calibrated:
            status_box.info(f"Phase 1 -- Calibration en cours ({calib_dur}s). Apprentissage du profil nominal...")
            pb = prog_box.progress(0.0)

            calib_start = time.time()
            calib_chunks = []

            while (time.time() - calib_start) < calib_dur:
                if not st.session_state.live_monitoring_active:
                    st.rerun()
                elapsed = time.time() - calib_start
                pb.progress(min(1.0, elapsed / calib_dur))
                status_box.info(f"Phase 1 -- Calibration : Capture du trafic ({int(calib_dur - elapsed)}s restantes)...")
                chunk = capture_live_packets(interface=live_iface, timeout=1.5)
                if not chunk.empty:
                    calib_chunks.append(chunk)

            calib_df = pd.concat(calib_chunks, ignore_index=True) if calib_chunks else pd.DataFrame(columns=PACKET_COLUMNS)
            status_box.info("Entrainement de l'Isolation Forest de reference...")

            try:
                scaler, model, _ = calibrate_baseline(calib_df, window_size=win_sz, contamination=0.05)
                st.session_state.live_scaler = scaler
                st.session_state.live_model = model
                st.session_state.live_baseline_calibrated = True
                prog_box.empty()
                status_box.success("Baseline calibree avec succes. Passage en phase d'inference active !")
                time.sleep(0.8)
                st.rerun()
            except Exception as e_cal:
                st.session_state.live_monitoring_active = False
                status_box.error(f"Erreur de calibration : {e_cal}")

        # Phase 2: Active Monitoring Loop
        else:
            status_box.success("Surveillance Active -- Capture et evaluation en temps reel...")
            try:
                window_raw = capture_live_packets(interface=live_iface, timeout=float(win_sz))
                st.session_state.live_total_windows += 1
                st.session_state.live_total_packets += len(window_raw)

                if not window_raw.empty:
                    scored_df = score_monitoring_window(
                        window_raw,
                        st.session_state.live_scaler,
                        st.session_state.live_model,
                        window_size=win_sz,
                    )
                    anomalies = scored_df[scored_df["Anomaly"] == -1]

                    for _, row in anomalies.iterrows():
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        row_dict = row.to_dict()
                        row_dict["timestamp_str"] = now_str
                        st.session_state.live_flagged_rows.append(row_dict)

                        # Create alert record & audit log
                        alt = create_alert_record(
                            src_address=row["Src_Address"],
                            anomaly_type=row["Anomaly_Type"],
                            packet_count=row.get("packet_count", 0),
                            unique_dst_ports=row.get("unique_dst_ports", 0),
                            unique_dst_ips=row.get("unique_dst_ips", 1),
                            syn_count=row.get("syn_count", 0),
                            avg_packet_length=row.get("avg_packet_length", 0.0),
                            time_window=row.get("time_window"),
                            origin=f"Live ({live_iface or 'defaut'})",
                        )
                        add_alert(alt)
                        log_security_event({
                            "anomaly_type": row["Anomaly_Type"],
                            "src_ip": row["Src_Address"],
                            "packet_count": int(row.get("packet_count", 0)),
                            "unique_ports": int(row.get("unique_dst_ports", 0)),
                            "timestamp": now_str,
                            "severity": "CRITICAL" if row["Anomaly_Type"] in ("Port Scan", "Flood / DDoS") else "HIGH",
                        })

            except Exception as e_mon:
                st.session_state.live_monitoring_active = False
                status_box.error(f"Surveillance interrompue : {e_mon}")

    # Display Live KPIs & Incident Feed
    if st.session_state.live_baseline_calibrated or st.session_state.live_flagged_rows:
        flagged_df = pd.DataFrame(st.session_state.live_flagged_rows)
        scans_count = int((flagged_df["Anomaly_Type"] == "Port Scan").sum()) if not flagged_df.empty else 0
        floods_count = int((flagged_df["Anomaly_Type"] == "Flood / DDoS").sum()) if not flagged_df.empty else 0
        live_threat = compute_threat_level(critical=floods_count, high=scans_count, lang=_curr_lang)

        with live_kpi_box.container():
            render_kpi_row(
                total_packets=st.session_state.live_total_packets,
                syn_per_sec=float(len(st.session_state.live_flagged_rows)),
                active_alerts=len(st.session_state.live_flagged_rows),
                top_attacker=flagged_df["Src_Address"].value_counts().index[0] if not flagged_df.empty else "None",
                threat_tuple=live_threat,
                lang=_curr_lang,
            )

        with live_feed_box.container():
            render_section_header(_t("sec_live_stream_title", default="Flux des Incidents en Direct (Pulsation Active)"), "LIVE STREAM")
            if flagged_df.empty:
                st.info(_t("live_no_anomaly", default="Trafic nominal. Aucune anomalie detectee dans les fenetres d'analyse."))
            else:
                # Render the latest alerts with pulse animation
                for idx, al in enumerate(reversed(st.session_state.live_flagged_rows[-8:])):
                    is_new = (idx == 0)
                    pulse_class = "live-alert-pulse" if is_new else ""
                    src_ip = al.get('Src_Address', '-')
                    geo_info = resolve_ip_geo(src_ip)
                    st.markdown(
                        f"""
                        <div class="threat-card threat-critical {pulse_class}" style="margin-bottom:0.75rem;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div>
                                    <span class="threat-level-pill threat-level-critical">CRITICAL</span>
                                    <b style="color:#ffffff; margin-left:0.6rem; font-size:1.05rem;">{al.get('Anomaly_Type', 'Attaque')}</b>
                                    <code style="color:#38bdf8; margin-left:0.8rem; font-size:0.95rem;">{src_ip}</code>
                                    <span style="color:#2dd4bf; font-size:0.85rem; margin-left:0.8rem; font-weight:600;">{geo_info['display']}</span>
                                </div>
                                <div style="color:#94a3b8; font-size:0.85rem;">
                                    {al.get('timestamp_str', '')}
                                </div>
                            </div>
                            <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.4rem;">
                                Paquets: <span style="color:#2dd4bf;">{al.get('packet_count', 0)}</span> &nbsp;|&nbsp;
                                Ports Cibles: <span style="color:#f87171;">{al.get('unique_dst_ports', 0)}</span> &nbsp;|&nbsp;
                                Flags SYN: <span style="color:#facc15;">{al.get('syn_count', 0)}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    elif not st.session_state.live_monitoring_active:
        render_empty_state(
            _t("empty_live_title", default="Surveillance Inactive"),
            _t("empty_live_desc", default="Selectionnez une interface et cliquez sur 'Demarrer la Surveillance' pour activer le monitoring temps reel."),
        )

    # Auto-refresh cycle (every 2-3s) when monitoring is active
    if st.session_state.live_monitoring_active and st.session_state.live_baseline_calibrated:
        time.sleep(2.0)
        st.rerun()


# ==============================================================================
# PAGE 3 : SOC INCIDENT & ALERT NOTIFICATION CENTER
# ==============================================================================
if _active_page == 'alerts':
    render_section_header(_t("sec_soc_title", default="Centre de Gestion des Incidents SOC"), "INCIDENT REGISTRY")
    st.caption(_t("sec_soc_caption", default="Registre consolide des attaques analysees avec regles de mitigation pare-feu et rapports d'incident."))

    alerts_list = load_alerts()
    tot_alerts = len(alerts_list)
    crit_alerts = sum(1 for a in alerts_list if a.get("severity") == "CRITICAL")
    high_alerts = sum(1 for a in alerts_list if a.get("severity") == "HIGH")
    soc_threat = compute_threat_level(crit_alerts, high_alerts, lang=_curr_lang)

    # Render SOC KPI Command Bar
    render_kpi_row(
        total_packets=sum(a.get("packet_count", 0) for a in alerts_list),
        syn_per_sec=float(sum(a.get("syn_count", 0) for a in alerts_list) / max(1, tot_alerts)),
        active_alerts=tot_alerts,
        top_attacker=alerts_list[0].get("src_address", "None") if alerts_list else "None",
        threat_tuple=soc_threat,
        lang=_curr_lang,
    )

    st.write("")

    # Actions Toolbar
    col_s1, col_s2, col_act = st.columns([1.5, 2.5, 1.2])
    all_label_f = _t("filter_all_f", default="Toutes")
    with col_s1:
        sev_choice = st.selectbox(_t("filter_sev_label", default="Filtrer par Severite"), [all_label_f, "CRITICAL", "HIGH", "MEDIUM"], key="soc_sev_choice")
    with col_s2:
        ip_filter = st.text_input(_t("filter_ip", default="Filtrer par IP Source"), placeholder=_t("filter_ip_placeholder", default="ex. 10.0.2.15"), key="soc_ip_filter").strip()

    with col_act:
        st.write("")
        st.write("")
        if st.button(_t("btn_clear_log", default="Vider le Registre"), use_container_width=True):
            clear_alerts()
            st.warning("Registre reinitialise.")
            time.sleep(0.5)
            st.rerun()

    # Apply filters
    disp_alerts = alerts_list
    if sev_choice != all_label_f:
        disp_alerts = [a for a in disp_alerts if a.get("severity") == sev_choice]
    if ip_filter:
        disp_alerts = [a for a in disp_alerts if ip_filter.lower() in str(a.get("src_address", "")).lower()]

    # Export Buttons
    if disp_alerts:
        df_exp = pd.DataFrame(disp_alerts)
        csv_data = df_exp.to_csv(index=False, sep=";").encode("utf-8-sig")
        json_data = json.dumps(disp_alerts, indent=2).encode("utf-8")

        exp_c1, exp_c2, exp_c3 = st.columns([1, 1, 1.8])
        with exp_c1:
            st.download_button(_t("btn_export_csv", default="Exporter CSV"), csv_data, "rapport_soc.csv", "text/csv", use_container_width=True)
        with exp_c2:
            st.download_button("Exporter JSON", json_data, "rapport_soc.json", "application/json", use_container_width=True)
        with exp_c3:
            report_html = generate_html_incident_report(
                session_stats={
                    "total_packets": sum(a.get("packet_count", 0) for a in alerts_list),
                    "total_windows": len(alerts_list),
                    "port_scan_count": sum(1 for a in alerts_list if a.get("anomaly_type") == "Port Scan"),
                    "flood_count": sum(1 for a in alerts_list if a.get("anomaly_type") == "Flood / DDoS"),
                    "packet_anomaly_count": len(alerts_list),
                    "source_target": "Registre SOC NetScan",
                },
                anomalous_windows=alerts_list,
            )
            st.download_button(
                _t("btn_download_report", default="Telecharger Rapport Executif (PDF/HTML)"),
                report_html.encode("utf-8"),
                "rapport_incident_netscan.html",
                "text/html",
                use_container_width=True,
            )

    # Render Incident Cards
    st.write("")
    if not disp_alerts:
        render_empty_state(
            _t("empty_alerts_title", default="Aucun incident dans le registre"),
            _t("empty_alerts_desc", default="Importez un fichier PCAP ou lancez la surveillance pour enregistrer de nouvelles alertes."),
        )
    else:
        for al in disp_alerts:
            sev = al.get("severity", "MEDIUM")
            card_class = "threat-critical" if sev == "CRITICAL" else ("threat-high" if sev == "HIGH" else "threat-medium")
            src_ip = al.get("src_address", "-")
            geo_info = resolve_ip_geo(src_ip)
            fw_rule = generate_firewall_rule(src_ip)

            st.markdown(
                f"""
                <div class="threat-card {card_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <div>
                            <span class="threat-level-pill threat-level-{sev.lower()}">{sev}</span>
                            <span style="font-weight:700; font-size:1.05rem; margin-left:0.6rem; color:#ffffff;">
                                {al.get('anomaly_type', 'Menace Inconnue')}
                            </span>
                            <span style="color:#64748b; font-size:0.8rem; margin-left:0.6rem;">ID: {al.get('id', 'ALT')}</span>
                        </div>
                        <div style="color:#94a3b8; font-size:0.82rem;">
                            {al.get('timestamp', '')} &nbsp;|&nbsp; <i>{al.get('origin', 'Systeme')}</i>
                        </div>
                    </div>
                    <div style="font-size:0.88rem; color:#cbd5e1; margin-bottom:0.4rem;">
                        <b>IP Source :</b> <code style="color:#38bdf8; font-size:0.95rem;">{src_ip}</code>
                        &nbsp;&nbsp;--&nbsp;&nbsp;
                        <b>Origine Geo :</b> <span style="color:#2dd4bf; font-weight:600;">{geo_info['display']}</span>
                        &nbsp;&nbsp;--&nbsp;&nbsp;
                        <b>Volume Paquets :</b> <span style="color:#2dd4bf;">{al.get('packet_count', 0):,}</span>
                        &nbsp;&nbsp;--&nbsp;&nbsp;
                        <b>Ports Cibles :</b> <span style="color:#f87171;">{al.get('unique_dst_ports', 0):,}</span>
                        &nbsp;&nbsp;--&nbsp;&nbsp;
                        <b>Flags SYN :</b> <span style="color:#facc15;">{al.get('syn_count', 0):,}</span>
                    </div>
                    <div style="font-size:0.85rem; color:#94a3b8; line-height:1.4;">
                        {al.get('description', '')}
                    </div>
                    <div class="mitigation-code">
                        <span><b>IPS Mitigation :</b> <code>{fw_rule}</code></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ==============================================================================
# PAGE 4 : AUDIT LOG & IPS FIREWALL AUTOMATION
# ==============================================================================
if _active_page == 'audit':
    render_section_header(_t("sec_audit_title", default="Journal d'Audit & Blocage Pare-Feu Automatise (IPS)"), "ACTIVE DEFENSE")
    st.caption(_t("sec_audit_caption", default="Generation immediate de regles d'isolation au niveau du noyau pour Windows (netsh) et Linux (iptables)."))

    col_ips1, col_ips2 = st.columns(2)
    with col_ips1:
        st.markdown(
            """
            <div class="glass-panel-title">
                <span class="dot-indicator"></span>
                Generateur de Regle de Blocage Pare-Feu
            </div>
            """,
            unsafe_allow_html=True,
        )
        test_ip = st.text_input("Adresse IP a neutraliser :", value="10.0.2.15")
        os_target = st.selectbox("Systeme d'exploitation cible", ["windows", "linux"])

        if test_ip:
            fw_cmd = generate_firewall_rule(test_ip, os_type=os_target)
            st.code(fw_cmd, language="bash" if os_target == "linux" else "powershell")
            st.caption("Copiez cette commande dans un terminal administrateur/root pour neutraliser l'attaquant.")

    with col_ips2:
        st.markdown(
            """
            <div class="glass-panel-title">
                <span class="dot-indicator"></span>
                Configuration du Module Alerting
            </div>
            """,
            unsafe_allow_html=True,
        )
        cur_cfg = load_alert_config()
        auto_block = st.checkbox("Generation automatique de regle pare-feu", value=cur_cfg.get("auto_firewall_rule", True))
        if st.button("Enregistrer les Preferences", use_container_width=True):
            cur_cfg["auto_firewall_rule"] = auto_block
            save_alert_config(cur_cfg)
            st.success("Parametres d'alerting sauvegardes !")

    st.write("")
    render_section_header("Audit Trail Persistant", "ALERTS_HISTORY.JSON")
    audit_records = load_security_events()
    if audit_records:
        st.dataframe(pd.DataFrame(audit_records), use_container_width=True, height=260)
    else:
        render_empty_state(
            _t("audit_no_events", default="Aucun incident enregistre dans l'audit trail"),
            "Le journal d'audit est actuellement vide. Les attaques et detections futures seront automatiquement archivees ici.",
        )


# ==============================================================================
# PAGE 5 : SETTINGS & LANGUAGES
# ==============================================================================
if _active_page == 'settings':
    render_section_header(_t("sec_settings_title", default="Parametres & Langues"), "CONFIG")

    c_cfg1, c_cfg2 = st.columns([1.2, 1.8])
    with c_cfg1:
        st.markdown(
            """
            <div class="glass-panel-title">
                <span class="dot-indicator"></span>
                Choix de la Langue
            </div>
            """,
            unsafe_allow_html=True,
        )
        _lang_names = {'fr': 'Français (FR)', 'en': 'English (EN)', 'es': 'Español (ES)'}
        _curr_lang = st.session_state.get('lang', _DEFAULT_LANG)
        _sel_lang = st.selectbox(
            "Langue de l'interface",
            _LANGS,
            format_func=lambda x: _lang_names.get(x, x.upper()),
            index=_LANGS.index(_curr_lang) if _curr_lang in _LANGS else 0,
            key='settings_lang_selector',
        )
        if _sel_lang != _curr_lang:
            st.session_state['lang'] = _sel_lang
            st.rerun()

    with c_cfg2:
        st.markdown(
            """
            <div class="glass-panel-title">
                <span class="dot-indicator"></span>
                Etat des Moteurs de Detection
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style="font-size:0.9rem; color:#cbd5e1; line-height:1.7;">
                Moteur Niveau 1 (Paquets) : <span style="color:#34d399; font-weight:700;">ACTIF (Isolation Forest)</span><br>
                Moteur Niveau 2 (Comportement) : <span style="color:#34d399; font-weight:700;">ACTIF (5s Windows)</span><br>
                Interface Sniffer : <span style="color:#2dd4bf; font-weight:600;">PyShark / Scapy Hybride</span><br>
                IPS Kernel Firewall : <span style="color:#22d3ee; font-weight:600;">Windows Netsh / Linux Iptables</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

