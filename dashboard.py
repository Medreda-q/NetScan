"""
dashboard.py — NetScan Streamlit Dashboard
=========================================
Author: Mohamed Reda QIYAOUI
DUT Cybersecurity — Stage d'Initiation, Septembre 2026

Interactive front-end for the dual-layer network anomaly detection pipeline.
Provides two distinct operating modes:
  1. Analyse de Capture (Fichier PCAP) : Offline forensic analysis with Level 1 & 2 graphs.
  2. Surveillance Réseau en Direct (Live) : Live packet sniffing with baseline calibration.

Run with:
    streamlit run dashboard.py
"""

import asyncio
import datetime
import json
import os
import tempfile
import time

import matplotlib
# Use the non-interactive Agg backend so matplotlib renders to PNG buffers
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Windows asyncio fix — must be set before importing pyshark
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Import our detection functions from the detection engine
from detection_engine import (
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
    load_alerts,
    save_alerts,
    add_alert,
    clear_alerts,
    create_alert_record,
    ALERTS_FILE,
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
# PAGE CONFIG & STYLING
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="NetScan — Network Anomaly Detector",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Hide sidebar entirely ── */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Mode selector styling ── */
    div[data-testid="stRadio"] > div {
        display: flex;
        justify-content: center;
        gap: 1.4rem;
        margin: 0.8rem 0 1.6rem 0;
    }
    div[data-testid="stRadio"] label {
        background: #111122;
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 0.75rem 1.6rem;
        font-weight: 600;
        font-size: 0.95rem;
        color: #cbd5e1;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    div[data-testid="stRadio"] label:hover {
        border-color: rgba(139, 92, 246, 0.7);
        background: #1a1040;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #1f144e 0%, #2b1766 100%);
        border-color: #8b5cf6;
        color: #ffffff;
        box-shadow: 0 4px 16px rgba(139, 92, 246, 0.35);
    }

    /* ── Hero header ── */
    .hero {
        background: linear-gradient(135deg, #0d0d1a 0%, #1a1040 50%, #0d1a2e 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 18px;
        padding: 2rem 2.5rem 1.8rem;
        margin-bottom: 1.4rem;
        position: relative;
        overflow: hidden;
    }
    .hero h1 {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #c084fc, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.2rem 0 0.4rem;
    }
    .hero p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
        max-width: 800px;
    }
    .hero .badge {
        display: inline-block;
        background: rgba(139, 92, 246, 0.15);
        border: 1px solid rgba(139, 92, 246, 0.4);
        color: #c084fc;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 1px;
        padding: 2px 10px;
        border-radius: 20px;
        margin-bottom: 0.4rem;
        text-transform: uppercase;
    }

    /* ── Status Banner ── */
    .banner {
        border-radius: 14px;
        padding: 1.2rem 1.8rem;
        margin-bottom: 1.4rem;
    }
    .banner-danger {
        background: linear-gradient(135deg, rgba(239,68,68,0.12) 0%, rgba(15,23,42,0.8) 100%);
        border: 1px solid rgba(239, 68, 68, 0.45);
    }
    .banner-safe {
        background: linear-gradient(135deg, rgba(34,197,94,0.1) 0%, rgba(15,23,42,0.8) 100%);
        border: 1px solid rgba(34, 197, 94, 0.4);
    }
    .banner h3 {
        margin: 0 0 0.8rem;
        font-size: 1.2rem;
        font-weight: 600;
    }
    .banner-danger h3 { color: #f87171; }
    .banner-safe   h3 { color: #4ade80; }

    /* ── Metric chips ── */
    .chips {
        display: flex;
        gap: 0.8rem;
        flex-wrap: wrap;
    }
    .chip {
        background: rgba(255,255,255,0.04);
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

    /* ── Tab tweak ── */
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        font-size: 0.9rem;
    }

    /* ── Incident Notification Card ── */
    .alert-card {
        background: #111122;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.9rem;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .alert-card:hover {
        border-color: rgba(255,255,255,0.18);
        transform: translateY(-2px);
    }
    .alert-critical { border-left: 4px solid #ef4444; }
    .alert-high     { border-left: 4px solid #f97316; }
    .alert-medium   { border-left: 4px solid #eab308; }

    .badge-critical {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .badge-high {
        background: rgba(249, 115, 22, 0.2);
        color: #fdba74;
        border: 1px solid rgba(249, 115, 22, 0.4);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .badge-medium {
        background: rgba(234, 179, 8, 0.2);
        color: #fde047;
        border: 1px solid rgba(234, 179, 8, 0.4);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .soc-mitigation-box {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        border-radius: 8px;
        padding: 0.6rem 0.9rem;
        margin-top: 0.6rem;
        font-size: 0.82rem;
        color: #6ee7b7;
        line-height: 1.45;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# CACHED PCAP PARSING
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Analyse du fichier .pcap en cours...")
def load_and_detect_packets(file_bytes: bytes, _filename: str) -> pd.DataFrame:
    """
    Parse the uploaded .pcap and run Layer 1 (per-packet) detection.
    Cached based on file_bytes so repeated views take milliseconds.
    """
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        raw_df = extract_features(tmp_path)
        analyzed_df = detect_anomalies(raw_df)
    finally:
        os.unlink(tmp_path)

    return analyzed_df


# ──────────────────────────────────────────────────────────────────────────────
# HELPER: RENDER ALERTS CENTER
# ──────────────────────────────────────────────────────────────────────────────

def render_alerts_center():
    """Renders the SOC incident notification center, filters, mitigation, and exports."""
    st.subheader("Centre de Notifications des Incidents de Sécurité")
    st.caption(
        "Registre des attaques confirmées avec niveau de gravité, statistiques et commandes de remédiation pare-feu."
    )

    alerts_list = load_alerts()

    # KPI Metrics Row
    total_alerts = len(alerts_list)
    crit_alerts = sum(1 for a in alerts_list if a.get("severity") == "CRITICAL")
    high_alerts = sum(1 for a in alerts_list if a.get("severity") == "HIGH")
    unique_attackers = len(set(a.get("src_address") for a in alerts_list if a.get("src_address")))

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Incidents", total_alerts)
    k2.metric("Scans Critiques", crit_alerts)
    k3.metric("Floods / DDoS", high_alerts)
    k4.metric("IPs Attaquantes", unique_attackers)

    st.markdown("---")

    # Action & Filter Toolbar
    col_f1, col_f2, col_act1, col_act2 = st.columns([1.5, 2, 2, 1.2])

    with col_f1:
        sev_filter = st.selectbox(
            "Gravité",
            options=["Toutes", "CRITICAL", "HIGH", "MEDIUM"],
            index=0,
            key="soc_sev_filter",
        )

    with col_f2:
        ip_query = st.text_input(
            "Rechercher une IP",
            placeholder="ex. 10.0.2.15",
            key="soc_ip_query",
        ).strip()

    with col_act1:
        st.write("")
        st.write("")
        if st.button(
            "Charger Incidents Démo (Nmap)",
            help="Préremplit des attaques réelles issues de la capture démo",
            key="soc_load_demo_btn",
        ):
            demo_events = [
                {
                    "src_address": "10.0.2.15",
                    "anomaly_type": "Port Scan",
                    "packet_count": 524,
                    "unique_dst_ports": 491,
                    "unique_dst_ips": 1,
                    "syn_count": 491,
                    "avg_packet_length": 60.0,
                    "time_window": 1629118905.0,
                    "origin": "Capture Démo",
                },
                {
                    "src_address": "10.0.2.15",
                    "anomaly_type": "Port Scan",
                    "packet_count": 587,
                    "unique_dst_ports": 526,
                    "unique_dst_ips": 1,
                    "syn_count": 533,
                    "avg_packet_length": 60.0,
                    "time_window": 1629118910.0,
                    "origin": "Capture Démo",
                },
                {
                    "src_address": "10.0.2.15",
                    "anomaly_type": "Flood / DDoS",
                    "packet_count": 1270,
                    "unique_dst_ports": 6,
                    "unique_dst_ips": 1,
                    "syn_count": 313,
                    "avg_packet_length": 54.0,
                    "time_window": 1629119125.0,
                    "origin": "Capture Démo",
                },
                {
                    "src_address": "10.0.2.15",
                    "anomaly_type": "Flood / DDoS",
                    "packet_count": 1938,
                    "unique_dst_ports": 3,
                    "unique_dst_ips": 1,
                    "syn_count": 482,
                    "avg_packet_length": 54.0,
                    "time_window": 1629119130.0,
                    "origin": "Capture Démo",
                },
                {
                    "src_address": "10.0.2.2",
                    "anomaly_type": "Port Scan",
                    "packet_count": 493,
                    "unique_dst_ports": 486,
                    "unique_dst_ips": 1,
                    "syn_count": 0,
                    "avg_packet_length": 54.0,
                    "time_window": 1629118905.0,
                    "origin": "Capture Démo",
                },
                {
                    "src_address": "10.0.2.2",
                    "anomaly_type": "Flood / DDoS",
                    "packet_count": 1934,
                    "unique_dst_ports": 486,
                    "unique_dst_ips": 1,
                    "syn_count": 0,
                    "avg_packet_length": 54.0,
                    "time_window": 1629119130.0,
                    "origin": "Capture Démo",
                },
            ]
            for ev in demo_events:
                rec = create_alert_record(**ev)
                add_alert(rec)
            st.success("Incidents de démonstration préremplis !")
            time.sleep(0.6)
            st.rerun()

    with col_act2:
        st.write("")
        st.write("")
        if st.button("Effacer tout", help="Effacer l'historique des alertes", key="soc_clear_btn"):
            clear_alerts()
            st.warning("Historique effacé.")
            time.sleep(0.5)
            st.rerun()

    # Filter Evaluation
    filtered_alerts = alerts_list
    if sev_filter != "Toutes":
        filtered_alerts = [a for a in filtered_alerts if a.get("severity") == sev_filter]
    if ip_query:
        filtered_alerts = [a for a in filtered_alerts if ip_query.lower() in str(a.get("src_address", "")).lower()]

    # Export Buttons
    if filtered_alerts:
        df_export = pd.DataFrame(filtered_alerts)
        csv_alerts = df_export.to_csv(index=False, sep=";").encode("utf-8-sig")
        json_alerts = json.dumps(filtered_alerts, indent=2).encode("utf-8")

        exp_col1, exp_col2, _ = st.columns([1.5, 1.5, 3])
        with exp_col1:
            st.download_button(
                label="Exporter en CSV",
                data=csv_alerts,
                file_name="rapport_incidents.csv",
                mime="text/csv",
                key="soc_dl_csv",
            )
        with exp_col2:
            st.download_button(
                label="Exporter en JSON",
                data=json_alerts,
                file_name="rapport_incidents.json",
                mime="application/json",
                key="soc_dl_json",
            )

    st.markdown("### Flux des Incidents de Sécurité")

    if not filtered_alerts:
        if alerts_list:
            st.info("Aucun incident ne correspond aux filtres de recherche.")
        else:
            st.info(
                "Aucun incident enregistré pour le moment. Lancez la **Surveillance Réseau en Direct** "
                "ou cliquez sur **Charger Incidents Démo (Nmap)** ci-dessus pour afficher des menaces enregistrées."
            )
    else:
        for alert in filtered_alerts:
            sev = alert.get("severity", "MEDIUM")
            card_class = (
                "alert-critical" if sev == "CRITICAL"
                else "alert-high" if sev == "HIGH"
                else "alert-medium"
            )
            badge_class = (
                "badge-critical" if sev == "CRITICAL"
                else "badge-high" if sev == "HIGH"
                else "badge-medium"
            )

            st.markdown(
                f"""
                <div class="alert-card {card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                        <div>
                            <span class="{badge_class}">{sev}</span>
                            <span style="font-weight: 700; font-size: 1.05rem; color: #ffffff; margin-left: 0.6rem;">
                                {alert.get('anomaly_type', 'Attaque Inconnue')}
                            </span>
                            <span style="font-size: 0.8rem; color: rgba(255,255,255,0.45); margin-left: 0.6rem;">
                                ID: <code>{alert.get('id', 'ALT')}</code>
                            </span>
                        </div>
                        <div style="font-size: 0.82rem; color: rgba(255,255,255,0.6);">
                            {alert.get('timestamp', 'Inconnu')} &nbsp;|&nbsp; <i>{alert.get('origin', 'Système')}</i>
                        </div>
                    </div>
                    <div style="font-size: 0.88rem; color: rgba(255,255,255,0.85); margin-bottom: 0.5rem;">
                        <b>IP Source :</b> <code class="val-orange" style="font-size: 0.95rem; font-weight: 600;">{alert.get('src_address', 'Inconnu')}</code>
                        &nbsp;&nbsp;•&nbsp;&nbsp;
                        <b>Paquets :</b> <span class="val-blue">{alert.get('packet_count', 0):,}</span>
                        &nbsp;&nbsp;•&nbsp;&nbsp;
                        <b>Ports Cibles :</b> <span class="val-danger">{alert.get('unique_dst_ports', 0):,}</span>
                        &nbsp;&nbsp;•&nbsp;&nbsp;
                        <b>Paquets SYN :</b> <span class="val-warn">{alert.get('syn_count', 0):,}</span>
                        &nbsp;&nbsp;•&nbsp;&nbsp;
                        <b>Taille Moy. :</b> <span>{alert.get('avg_packet_length', 0):.1f} B</span>
                    </div>
                    <div style="font-size: 0.85rem; color: rgba(255,255,255,0.7); line-height: 1.45;">
                        {alert.get('description', '')}
                    </div>
                    <div class="soc-mitigation-box">
                        <b>Remédiation Pare-Feu Recommandée :</b> {alert.get('recommendation', 'Inspecter le trafic de la machine.')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ──────────────────────────────────────────────────────────────────────────────
# HELPER: RENDER LIVE MONITORING
# ──────────────────────────────────────────────────────────────────────────────

def render_live_monitoring():
    """Renders real-time network capture, baseline calibration, and continuous detection."""
    st.subheader("Surveillance Réseau en Temps Réel")
    st.caption(
        "Phase 1 : Calibration du profil normal (baseline) • Phase 2 : Détection continue des attaques (Scans, Floods)."
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
        iface_options = ["Interface par défaut"] + available_ifaces + ["Interface personnalisée..."]
        selected_option = st.selectbox(
            "Interface Réseau",
            options=iface_options,
            help="Sélectionnez l'adaptateur réseau à surveiller.",
        )
        if selected_option == "Interface personnalisée...":
            live_interface = st.text_input("Nom de l'interface :", value="eth0")
        elif selected_option == "Interface par défaut":
            live_interface = None
        else:
            live_interface = selected_option

    with c_dur:
        live_calib_duration = st.slider(
            "Durée Calibration (s)",
            min_value=10,
            max_value=300,
            value=120,
            step=5,
            help="Temps alloué pour apprendre le profil normal du trafic.",
        )

    with c_win:
        live_window_size = st.slider(
            "Fenêtre d'Analyse (s)",
            min_value=1,
            max_value=30,
            value=5,
            step=1,
            help="Durée de chaque fenêtre pour évaluer le comportement en direct.",
        )

    col_btn1, col_btn2, _ = st.columns([1.2, 1.2, 3])
    with col_btn1:
        if not st.session_state.live_monitoring_active:
            if st.button("Lancer la Surveillance", type="primary", use_container_width=True):
                st.session_state.live_monitoring_active = True
                st.session_state.live_baseline_calibrated = False
                st.session_state.live_flagged_rows = []
                st.session_state.live_total_windows = 0
                st.session_state.live_total_packets = 0
                st.rerun()

    with col_btn2:
        if st.session_state.live_monitoring_active:
            if st.button("Arrêter", use_container_width=True):
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
                f"Phase 1 — Calibration en cours : Capture du trafic pendant {live_calib_duration}s..."
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
                    f"Erreur de Permission / Pilote Capture\n\n"
                    f"{str(pe)}\n\n"
                    f"Actions requises :\n"
                    f"- Windows : Installez Npcap (mode compatible WinPcap) et lancez le terminal en Administrateur.\n"
                    f"- Linux / macOS : Lancez avec sudo : `sudo streamlit run dashboard.py`"
                )
                st.stop()
            except Exception as e:
                st.session_state.live_monitoring_active = False
                live_status_container.empty()
                live_progress_container.empty()
                st.error(f"Échec de capture : {e}")
                st.stop()

            # Execute calibration loop
            calib_start = time.time()
            calib_buffer = []
            if not test_pkts.empty:
                calib_buffer.append(test_pkts)

            while (time.time() - calib_start) < live_calib_duration:
                if not st.session_state.live_monitoring_active:
                    st.rerun()
                elapsed = time.time() - calib_start
                frac = min(1.0, elapsed / live_calib_duration)
                progress_bar.progress(frac)
                rem = int(live_calib_duration - elapsed)
                live_status_container.info(
                    f"Phase 1 — Calibration en cours : Apprentissage du profil normal... ({rem}s restantes)"
                )
                chunk = capture_live_packets(interface=live_interface, timeout=2.0)
                if not chunk.empty:
                    calib_buffer.append(chunk)

            # Assemble calibration dataframe
            if calib_buffer:
                calib_raw_df = pd.concat(calib_buffer, ignore_index=True)
            else:
                calib_raw_df = pd.DataFrame(columns=PACKET_COLUMNS)

            live_status_container.info("Calcul du modèle baseline en cours...")
            try:
                scaler, model, base_win_df = calibrate_baseline(
                    calib_raw_df, window_size=live_window_size, contamination=0.10
                )
                st.session_state.live_scaler = scaler
                st.session_state.live_model = model
                st.session_state.live_baseline_calibrated = True
                live_progress_container.empty()
                live_status_container.success("Phase 1 terminée : Profil baseline calibré avec succès.")
            except Exception as e_calib:
                st.session_state.live_monitoring_active = False
                live_status_container.empty()
                live_progress_container.empty()
                st.error(f"Échec de calibration : {e_calib}")
                st.stop()

        # Phase 2: Monitoring loop (single window evaluation per rerun)
        if st.session_state.live_baseline_calibrated:
            live_status_container.success(
                f"Phase 2 — Surveillance Active : Évaluation continue par fenêtres de {live_window_size}s"
            )

            try:
                mon_chunk = capture_live_packets(interface=live_interface, timeout=float(live_window_size))
                st.session_state.live_total_windows += 1
                st.session_state.live_total_packets += len(mon_chunk)

                scored_win_df = score_monitoring_window(
                    mon_chunk,
                    st.session_state.live_scaler,
                    st.session_state.live_model,
                    window_size=live_window_size,
                )

                anomalous_in_window = scored_win_df[scored_win_df["Anomaly"] == -1]
                if not anomalous_in_window.empty:
                    now_str = datetime.datetime.now().strftime("%H:%M:%S")
                    for _, row in anomalous_in_window.iterrows():
                        rec = row.to_dict()
                        rec["timestamp_str"] = now_str
                        st.session_state.live_flagged_rows.append(rec)
                        try:
                            alt_rec = create_alert_record(
                                src_address=row["Src_Address"],
                                anomaly_type=row["Anomaly_Type"],
                                packet_count=row["packet_count"],
                                unique_dst_ports=row["unique_dst_ports"],
                                unique_dst_ips=row.get("unique_dst_ips", 1),
                                syn_count=row["syn_count"],
                                avg_packet_length=row.get("avg_packet_length", 0.0),
                                time_window=row.get("time_window"),
                                origin=f"Surveillance ({live_interface or 'défaut'})",
                            )
                            add_alert(alt_rec)
                        except Exception:
                            pass
                        st.toast(
                            f"Anomalie Détectée : {row['Anomaly_Type']} depuis {row['Src_Address']}"
                        )

            except Exception as e_mon:
                st.session_state.live_monitoring_active = False
                st.error(f"Surveillance interrompue : {e_mon}")
                st.stop()

    # Render metrics and table whenever there is monitoring activity or history
    if st.session_state.live_baseline_calibrated or st.session_state.live_flagged_rows:
        flagged_df = pd.DataFrame(st.session_state.live_flagged_rows)
        scans_count = int((flagged_df["Anomaly_Type"] == "Port Scan").sum()) if not flagged_df.empty else 0
        floods_count = int((flagged_df["Anomaly_Type"] == "Flood / DDoS").sum()) if not flagged_df.empty else 0

        with live_metrics_container.container():
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Fenêtres Surveillées", st.session_state.live_total_windows)
            m2.metric("Total Paquets Live", f"{st.session_state.live_total_packets:,}")
            m3.metric("Scans de Ports", scans_count)
            m4.metric("Floods / DDoS", floods_count)

        with live_table_container.container():
            st.markdown("### Journal des Anomalies Détectées en Direct")
            if flagged_df.empty:
                st.info("Aucune anomalie détectée — le trafic est conforme au profil baseline.")
            else:
                display_cols_live = [
                    c for c in [
                        "timestamp_str", "Src_Address", "time_window", "packet_count",
                        "unique_dst_ports", "unique_dst_ips", "syn_count", "avg_packet_length", "Anomaly_Type",
                    ] if c in flagged_df.columns
                ]
                styled_live = apply_anomaly_style(flagged_df, display_cols_live)
                st.dataframe(styled_live, use_container_width=True, height=280)

                csv_live = flagged_df.to_csv(index=False, sep=";").encode("utf-8-sig")
                st.download_button(
                    label="Exporter en CSV",
                    data=csv_live,
                    file_name="anomalies_direct.csv",
                    mime="text/csv",
                )

    if st.session_state.live_monitoring_active and st.session_state.live_baseline_calibrated:
        time.sleep(0.5)
        st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# HERO HEADER
# ──────────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="hero">
        <div class="badge">DUT — Stage d'Initiation Cybersécurité</div>
        <h1>NetScan — Network Anomaly Detector</h1>
        <p>
            Détection d'intrusions et anomalies réseau (Scans de ports, DDoS, paquets anormaux)
            sans signatures préalables via Machine Learning non supervisé (Isolation Forest).
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN NAVIGATION: TWO OPTIONS (UPLOAD / PCAP vs. LIVE MONITORING)
# ──────────────────────────────────────────────────────────────────────────────

col_nav1, col_nav2, col_nav3 = st.columns([1, 2.8, 1])
with col_nav2:
    mode = st.radio(
        "Mode de fonctionnement",
        options=["Analyse de Capture (Fichier PCAP)", "Surveillance Réseau en Direct (Live)"],
        horizontal=True,
        label_visibility="collapsed",
    )


# ══════════════════════════════════════════════════════════════════════════════
# OPTION 1 : ANALYSE DE FICHIER (CAPTURE PCAP + GRAPHIQUES NIVEAU 1 & 2)
# ══════════════════════════════════════════════════════════════════════════════

if mode == "Analyse de Capture (Fichier PCAP)":
    uploaded_file = st.file_uploader(
        "Importer une capture réseau (.pcap / .pcapng)",
        type=["pcap", "pcapng"],
        help="Glissez-déposez ou sélectionnez un fichier de capture réseau (.pcap ou .pcapng).",
    )

    window_size = 5
    active_bytes = None
    active_filename = None

    if uploaded_file is not None:
        active_bytes = uploaded_file.getvalue()
        active_filename = uploaded_file.name

    if active_bytes is not None:
        # Layer 1 — cached (runs only when file changes)
        packet_df = load_and_detect_packets(active_bytes, active_filename)

        # Layer 2 — aggregated into windows
        with st.spinner(f"Agrégation en fenêtres de {window_size}s et calcul des anomalies..."):
            window_df = aggregate_windows(packet_df, window_size=window_size)
            window_df = detect_window_anomalies(window_df)

        port_scans  = int((window_df["Anomaly_Type"] == "Port Scan").sum())
        floods      = int((window_df["Anomaly_Type"] == "Flood / DDoS").sum())
        pkt_anomaly = int((packet_df["Anomaly"] == -1).sum())
        total_pkts  = len(packet_df)
        total_wins  = len(window_df)

        is_safe = port_scans == 0 and floods == 0
        banner_cls = "banner banner-safe" if is_safe else "banner banner-danger"
        status_msg = (
            "Trafic normal — Aucune menace détectée"
            if is_safe
            else "Menaces détectées — Consulter l'onglet Comportemental (Niveau 2)"
        )

        st.markdown(
            f"""
            <div class="{banner_cls}">
                <h3>Analyse : {active_filename} — {status_msg}</h3>
                <div class="chips">
                    <div class="chip">
                        <span class="val {'val-danger' if port_scans > 0 else 'val-safe'}">{port_scans}</span>
                        <span class="lbl">Scans de Ports</span>
                    </div>
                    <div class="chip">
                        <span class="val {'val-orange' if floods > 0 else 'val-safe'}">{floods}</span>
                        <span class="lbl">Floods / DDoS</span>
                    </div>
                    <div class="chip">
                        <span class="val {'val-warn' if pkt_anomaly > 0 else 'val-safe'}">{pkt_anomaly:,}</span>
                        <span class="lbl">Paquets Anormaux</span>
                    </div>
                    <div class="chip">
                        <span class="val val-blue">{total_pkts:,}</span>
                        <span class="lbl">Total Paquets</span>
                    </div>
                    <div class="chip">
                        <span class="val val-blue">{total_wins:,}</span>
                        <span class="lbl">Fenêtres ({window_size}s)</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        initial_alerts = load_alerts()
        alert_badge = f" ({len(initial_alerts)})" if initial_alerts else ""

        # Sub-tabs exclusively containing graphs and forensic data for this upload
        tab1, tab2, tab_alerts = st.tabs(
            [
                "Analyse par Paquet (Niveau 1)",
                "Analyse Comportementale (Niveau 2)",
                f"Centre d'Alertes SOC{alert_badge}",
            ]
        )

        # ── TAB 1 : Analyse par Paquet ─────────────────────────────────────────
        with tab1:
            st.subheader("Niveau 1 — Analyse Microscopique (Par Paquet)")
            st.caption(
                "Détecte les paquets statistiquement anormaux : retransmissions excessives, paquets malformés, flags TCP suspects."
            )

            col_plot, col_stats = st.columns([3, 1])

            with col_plot:
                fig1, ax1 = plt.subplots(figsize=(11, 5))
                fig1.patch.set_facecolor("#0d1117")
                ax1.set_facecolor("#0d1117")

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
                    "Taille des Paquets vs. Index  (Niveau 1 — anomalies individuelles)",
                    color="white", pad=12, fontsize=11,
                )
                ax1.set_xlabel("Index du Paquet", color="#94a3b8")
                ax1.set_ylabel("Taille (octets)", color="#94a3b8")
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

            with col_stats:
                st.metric("Paquets Anormaux", pkt_anomaly)
                st.metric("Paquets Normaux", total_pkts - pkt_anomaly)
                st.markdown("---")

                if pkt_anomaly > 0:
                    st.markdown("**Types d'anomalies**")
                    type_counts = (
                        packet_df[packet_df["Anomaly"] == -1]["Anomaly_Type"]
                        .value_counts()
                        .rename("Total")
                    )
                    st.dataframe(type_counts, use_container_width=True)
                else:
                    st.success("Aucune anomalie par paquet détectée.")

            st.markdown("---")
            st.subheader("Liste des Paquets Anormaux")

            anomaly_pkt_df = packet_df[packet_df["Anomaly"] == -1].copy()

            if anomaly_pkt_df.empty:
                st.info("Aucun paquet anormal trouvé.")
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
                    height=300,
                )

                csv_bytes = anomaly_pkt_df.to_csv(index=False, sep=";").encode("utf-8-sig")
                st.download_button(
                    label="Exporter en CSV",
                    data=csv_bytes,
                    file_name="paquets_anormaux.csv",
                    mime="text/csv",
                )

        # ── TAB 2 : Analyse Comportementale ────────────────────────────────────
        with tab2:
            st.subheader(f"Niveau 2 — Analyse Comportementale par Fenêtre ({window_size}s)")
            st.caption(
                "Détecte les attaques multi-paquets : Scans de ports (dispersion vers de multiples ports) et Floods / DDoS (volume anormal)."
            )

            col_plot2, col_stats2 = st.columns([3, 1])

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
                    f"Profil Comportemental par Source / Fenêtre {window_size}s\n"
                    "Axe X = Volume de paquets · Axe Y = Diversité des ports cibles",
                    color="white", pad=12, fontsize=10,
                )
                ax2.set_xlabel("Volume de Paquets (par source / fenêtre)", color="#94a3b8")
                ax2.set_ylabel("Ports Cibles Uniques", color="#94a3b8")
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

            with col_stats2:
                st.metric("Total Fenêtres", total_wins)
                st.metric("Scans de Ports", port_scans)
                st.metric("Floods / DDoS", floods)
                st.markdown("---")

                if port_scans + floods > 0:
                    st.markdown("**IPs suspectes**")
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
                    st.dataframe(flagged_srcs, use_container_width=True, height=200)
                else:
                    st.success("Aucune anomalie comportementale.")

            with st.expander("Interprétation du graphique comportemental"):
                st.markdown(
                    """
                    - **Bas-gauche** : Hôtes normaux (faible volume, peu de ports contactés).
                    - **Haut-gauche (Rouge)** : **Scan de ports** (dispersion sur de multiples ports — ex. Nmap).
                    - **Bas-droite (Orange)** : **Flood / DDoS** (volume massif vers une cible concentrée).
                    - **Taille des points** : Proportionnelle à la taille moyenne des paquets.
                    """
                )

            st.markdown("---")
            st.subheader("Profils Comportementaux par Fenêtre")

            display_cols = [
                "Src_Address", "time_window", "packet_count", "unique_dst_ports",
                "unique_dst_ips", "syn_count", "avg_packet_length", "Anomaly_Type",
            ]

            styled = apply_anomaly_style(window_df, display_cols)
            st.dataframe(styled, use_container_width=True, height=300)

            anomaly_win_df = window_df[window_df["Anomaly"] == -1]
            csv_win = anomaly_win_df.to_csv(index=False, sep=";").encode("utf-8-sig")

            col_dl, col_push = st.columns([1, 1.3])
            with col_dl:
                st.download_button(
                    label="Exporter en CSV",
                    data=csv_win,
                    file_name="fenetres_comportementales.csv",
                    mime="text/csv",
                )
            with col_push:
                if not anomaly_win_df.empty:
                    if st.button("Enregistrer les alertes dans le Centre d'Alertes", key="push_to_alerts_btn"):
                        count_added = 0
                        for _, a_row in anomaly_win_df.iterrows():
                            a_rec = create_alert_record(
                                src_address=a_row["Src_Address"],
                                anomaly_type=a_row["Anomaly_Type"],
                                packet_count=a_row["packet_count"],
                                unique_dst_ports=a_row["unique_dst_ports"],
                                unique_dst_ips=a_row.get("unique_dst_ips", 1),
                                syn_count=a_row["syn_count"],
                                avg_packet_length=a_row.get("avg_packet_length", 0.0),
                                time_window=a_row.get("time_window"),
                                origin="Capture (.pcap)",
                            )
                            add_alert(a_rec)
                            count_added += 1
                        st.success(f"{count_added} alerte(s) ajoutée(s) au Centre de Notifications !")
                        time.sleep(0.8)
                        st.rerun()

        # ── TAB 3 : Centre d'Alertes ───────────────────────────────────────────
        with tab_alerts:
            render_alerts_center()

    else:
        st.info("Veuillez importer un fichier de capture .pcap ou .pcapng pour démarrer l'analyse.")


# ══════════════════════════════════════════════════════════════════════════════
# OPTION 2 : SURVEILLANCE RÉSEAU EN DIRECT (LIVE SNIFFING + ALERTS)
# ══════════════════════════════════════════════════════════════════════════════

else:
    render_live_monitoring()

    st.markdown("---")
    initial_alerts = load_alerts()
    alert_badge = f" ({len(initial_alerts)})" if initial_alerts else ""
    with st.expander(f"Historique des Alertes SOC Enregistrées{alert_badge}", expanded=False):
        render_alerts_center()
