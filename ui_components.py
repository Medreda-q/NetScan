"""
ui_components.py -- Reusable SOC UI Components for NetScan
==========================================================
Author: Mohamed Reda QIYAOUI
Network Intrusion Detection & Analysis System (NIDS/NIPS)

Modular UI presentation elements:
  - SOC Glassmorphic Hero Header (Logo, ENGINE ACTIVE badge, Real-time Clock)
  - 5-Card SOC KPI Command Row (Packets, SYN/s, Active Alerts, Top Attacker, Threat Level)
  - Skeleton loading states and shimmer cards
  - Severity Badges (CRITICAL, HIGH, MEDIUM, LOW)
  - Filterable Alerts Data Table
"""

import base64
import os
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from i18n import t


def _get_lang(lang: Optional[str] = None) -> str:
    """Helper to resolve active language."""
    if lang:
        return lang
    return st.session_state.get("lang", "fr")


def compute_threat_level(critical: int, high: int, lang: Optional[str] = None) -> Tuple[str, str]:
    """
    Return (label, css_class) for the threat level assessment.
    Levels: Critical (red), High (orange), Medium (amber), Low (green/teal).
    """
    l = _get_lang(lang)
    if critical > 3:
        return (t("severity_critical", lang=l), "threat-level-critical")
    if critical > 0:
        return (t("severity_high", lang=l), "threat-level-high")
    if high > 0:
        return (t("severity_medium", lang=l), "threat-level-medium")
    return (t("severity_low", lang=l), "threat-level-low")


def render_header(
    logo_uri: str,
    threat_tuple: Tuple[str, str],
    clock_str: str,
    title: str = "NetScan Anomaly Shield",
    subtitle: str = "Autonomous Network Intrusion Detection & Behavioral Anomaly Analytics",
    author: str = "Mohamed Reda QIYAOUI",
) -> None:
    """Render the SOC top command bar."""
    lbl, cls_name = threat_tuple
    logo_html = f'<img src="{logo_uri}" alt="NetScan Logo" />' if logo_uri else ""

    st.markdown(
        f"""
        <div class="netscan-hero">
            <div class="hero-content">
                <div class="hero-logo-box">
                    {logo_html}
                </div>
                <div class="hero-title-group">
                    <div class="hero-badge">DUAL-LAYER NIDS / IPS  --  ISOLATION FOREST ENGINE</div>
                    <h1>{title}</h1>
                    <p>
                        {subtitle}
                        &nbsp;--&nbsp; <i>{author}</i>
                    </p>
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(
    total_packets: int,
    syn_per_sec: float,
    active_alerts: int,
    top_attacker: str,
    threat_tuple: Tuple[str, str],
    lang: Optional[str] = None,
) -> None:
    """
    Render the 5-card SOC KPI metrics row:
      1. Total packets analyzed
      2. SYN packets/sec
      3. Active alerts
      4. Top attacker IP
      5. Threat level (Low / Medium / High / Critical with color)
    """
    l = _get_lang(lang)
    lbl, cls_name = threat_tuple
    top_ip_display = top_attacker if top_attacker and top_attacker != "N/A" else "None"

    syn_cls = "kpi-danger" if syn_per_sec > 100 else ("kpi-warning" if syn_per_sec > 20 else "kpi-teal")
    alerts_cls = "kpi-danger" if active_alerts > 0 else "kpi-safe"
    attacker_cls = "kpi-danger" if top_ip_display != "None" else "kpi-muted"

    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <span class="kpi-val kpi-cyan">{total_packets:,}</span>
                <span class="kpi-lbl">{t("kpi_total", lang=l)}</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-val {syn_cls}">{syn_per_sec:.1f} <small style="font-size:0.55em; font-weight:500;">/s</small></span>
                <span class="kpi-lbl">{t("kpi_syn_rate", lang=l)}</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-val {alerts_cls}">{active_alerts:,}</span>
                <span class="kpi-lbl">{t("kpi_active_alerts", lang=l)}</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-val {attacker_cls}" style="font-size:1.15rem; font-family:'JetBrains Mono',monospace;">{top_ip_display}</span>
                <span class="kpi-lbl">{t("kpi_top_attacker", lang=l)}</span>
            </div>
            <div class="kpi-card" style="display:flex; flex-direction:column; justify-content:center; align-items:flex-start;">
                <span class="threat-level-pill {cls_name}">{lbl}</span>
                <span class="kpi-lbl" style="margin-top:0.4rem;">{t("kpi_global_threat", lang=l)}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_skeleton_kpis(count: int = 5) -> None:
    """Render animated shimmer skeleton cards for empty states."""
    cards = ""
    for _ in range(count):
        cards += """
        <div class="skeleton-card">
            <div class="skeleton-bar skeleton-bar-lg"></div>
            <div class="skeleton-bar skeleton-bar-sm"></div>
        </div>"""
    st.markdown(f'<div class="skeleton-grid">{cards}</div>', unsafe_allow_html=True)


def render_skeleton_chart(label: str = "AWAITING DATA FEED") -> None:
    """Render a shimmer placeholder for pending charts."""
    st.markdown(
        f"""
        <div class="skeleton-chart">
            <span class="skeleton-chart-label">{label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, description: str) -> None:
    """Render an aesthetic empty state message."""
    st.markdown(
        f"""
        <div class="empty-state">
            <span class="empty-state-icon"></span>
            <h4>{title}</h4>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, tag: Optional[str] = None) -> None:
    """Render a styled section header with glowing rule and optional tag."""
    tag_html = f'<span class="section-tag">{tag}</span>' if tag else ""
    st.markdown(
        f"""
        <div class="section-header">
            <h3>{title}</h3>
            <div class="section-line"></div>
            {tag_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


from geoip_resolver import resolve_ip_geo


def render_alerts_table(
    alerts: List[Dict[str, Any]],
    key_prefix: str = "soc_table",
    lang: Optional[str] = None,
) -> None:
    """
    Render interactive, filterable, and sortable alerts table with colored badges and GeoIP.
    Columns: time, source IP, Geo Origin, target IP, attack type, severity, anomaly score.
    """
    l = _get_lang(lang)
    if not alerts:
        render_empty_state(
            t("empty_alerts_title", lang=l),
            t("empty_alerts_desc", lang=l),
        )
        return

    df = pd.DataFrame(alerts)

    # Normalize columns
    if "time" not in df.columns:
        if "timestamp" in df.columns:
            df["time"] = df["timestamp"]
        elif "time_window" in df.columns:
            df["time"] = df["time_window"].astype(str)
        else:
            df["time"] = "-"

    if "source_ip" not in df.columns:
        df["source_ip"] = df.get("src_address", df.get("Src_Address", "-"))

    # Resolve GeoIP origin
    if "geo_origin" not in df.columns:
        df["geo_origin"] = df["source_ip"].apply(lambda ip: resolve_ip_geo(str(ip))["display"])

    if "target_ip" not in df.columns:
        df["target_ip"] = df.get("dst_address", df.get("Dst_Address", "Reseau Interne"))

    if "attack_type" not in df.columns:
        df["attack_type"] = df.get("anomaly_type", df.get("Anomaly_Type", "Inconnu"))

    if "severity" not in df.columns:
        # Default severity mapping
        def _get_sev(t_val):
            t_str = str(t_val).lower()
            if "flood" in t_str or "ddos" in t_str:
                return "CRITICAL"
            elif "scan" in t_str:
                return "HIGH"
            elif "reset" in t_str or "protocol" in t_str:
                return "MEDIUM"
            return "LOW"
        df["severity"] = df["attack_type"].apply(_get_sev)

    if "anomaly_score" not in df.columns:
        df["anomaly_score"] = df.get("score", df.get("Score", -0.75))

    # Filters row
    all_label_m = t("filter_all_m", lang=l)
    all_label_f = t("filter_all_f", lang=l)
    f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 2])
    with f_col1:
        types_avail = [all_label_m] + sorted(list(df["attack_type"].dropna().unique()))
        sel_type = st.selectbox(t("filter_type_label", lang=l), types_avail, key=f"{key_prefix}_type")
    with f_col2:
        sevs_avail = [all_label_f, "CRITICAL", "HIGH", "MEDIUM", "LOW"]
        sel_sev = st.selectbox(t("filter_sev_label", lang=l), sevs_avail, key=f"{key_prefix}_sev")
    with f_col3:
        search_ip = st.text_input(t("filter_search_label", lang=l), "", key=f"{key_prefix}_search").strip().lower()

    filtered = df.copy()
    if sel_type != all_label_m:
        filtered = filtered[filtered["attack_type"] == sel_type]
    if sel_sev != all_label_f:
        filtered = filtered[filtered["severity"] == sel_sev]
    if search_ip:
        filtered = filtered[
            filtered["source_ip"].astype(str).str.lower().str.contains(search_ip)
            | filtered["geo_origin"].astype(str).str.lower().str.contains(search_ip)
            | filtered["target_ip"].astype(str).str.lower().str.contains(search_ip)
        ]

    # Display columns: time, source IP, Geo Origin, target IP, attack type, severity, anomaly score
    display_df = filtered[["time", "source_ip", "geo_origin", "target_ip", "attack_type", "severity", "anomaly_score"]].copy()
    sev_col_name = t("col_severity", lang=l)
    display_df.rename(
        columns={
            "time": t("col_time", lang=l),
            "source_ip": t("col_source_ip", lang=l),
            "geo_origin": t("col_geo_origin", lang=l),
            "target_ip": t("col_target_ip", lang=l),
            "attack_type": t("col_attack_type", lang=l),
            "severity": sev_col_name,
            "anomaly_score": t("col_score", lang=l),
        },
        inplace=True,
    )

    # Style function for severity badges and attack types
    def _style_severity(val):
        v = str(val).upper()
        if "CRIT" in v:
            return "background-color: rgba(248,113,113,0.22); color: #fca5a5; font-weight: 700; border-left: 3px solid #f87171;"
        elif "HIGH" in v or "ELEV" in v or "ALTO" in v:
            return "background-color: rgba(251,146,60,0.22); color: #fdba74; font-weight: 700; border-left: 3px solid #fb923c;"
        elif "MED" in v or "MOY" in v:
            return "background-color: rgba(250,204,21,0.18); color: #fde047; font-weight: 600; border-left: 3px solid #facc15;"
        return "background-color: rgba(52,211,153,0.15); color: #6ee7b7; font-weight: 600; border-left: 3px solid #34d399;"

    styled = display_df.style.map(_style_severity, subset=[sev_col_name])
    st.dataframe(styled, use_container_width=True, height=280)
