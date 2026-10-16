"""
ui_charts.py -- NetScan SOC Plotly Chart Components
===================================================
Author: Mohamed Reda QIYAOUI
Network Intrusion Detection & Analysis System (NIDS/NIPS)

Plotly dark-themed interactive charts matching the glassmorphic SOC command center design:
  - SYN Rate Time Series (spikes highlighted with red diamond markers)
  - Attack Type Distribution Donut Chart (SYN Scan vs SYN Flood vs Normal)
  - Top 10 Source IPs Horizontal Bar Chart
  - Isolation Forest Anomaly Score Distribution Histogram
  - Layer 1 Forensic Packet Size Scatter Plot
"""

from typing import Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from i18n import t


def _get_lang(lang: Optional[str] = None) -> str:
    """Helper to retrieve current language."""
    if lang:
        return lang
    try:
        return st.session_state.get("lang", "fr")
    except Exception:
        return "fr"


# ------------------------------------------------------------------------------
# PALETTE & DESIGN CONSTANTS
# ------------------------------------------------------------------------------
C_TEAL = "#2dd4bf"
C_CYAN = "#22d3ee"
C_DANGER = "#f87171"
C_WARNING = "#fb923c"
C_SAFE = "#34d399"
C_MUTED = "#64748b"
C_DARK_BG = "rgba(11, 17, 26, 0.65)"
C_BORDER = "rgba(45, 212, 191, 0.15)"

ATTACK_COLORS = {
    "Port Scan": C_DANGER,
    "SYN Scan": C_DANGER,
    "Flood / DDoS": C_WARNING,
    "SYN Flood": C_WARNING,
    "Normal": C_TEAL,
    "Retransmission": C_WARNING,
    "Reset Flag": C_DANGER,
    "High Packet Length": "#facc15",
    "High Latency": C_SAFE,
    "Unexpected Protocol": "#38bdf8",
    "Malformed Packet": "#c084fc",
    "Other": C_MUTED,
}

BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=C_DARK_BG,
    font=dict(family="Plus Jakarta Sans, sans-serif", color="#94a3b8", size=11),
    margin=dict(l=45, r=20, t=35, b=35),
    xaxis=dict(
        gridcolor="rgba(51, 65, 85, 0.25)",
        zerolinecolor="rgba(51, 65, 85, 0.3)",
        tickfont=dict(color="#64748b", size=10),
    ),
    yaxis=dict(
        gridcolor="rgba(51, 65, 85, 0.25)",
        zerolinecolor="rgba(51, 65, 85, 0.3)",
        tickfont=dict(color="#64748b", size=10),
    ),
    legend=dict(
        bgcolor="rgba(15, 23, 42, 0.85)",
        bordercolor=C_BORDER,
        borderwidth=1,
        font=dict(color="#f1f5f9", size=10),
    ),
    hoverlabel=dict(
        bgcolor="#0f172a",
        bordercolor=C_TEAL,
        font=dict(color="#f1f5f9", size=12),
    ),
)


def create_syn_timeseries_chart(window_df: pd.DataFrame, lang: Optional[str] = None) -> go.Figure:
    """
    Time series of SYN rate. Floods/scans show as clear spikes with anomaly points in red.
    """
    l = _get_lang(lang)
    fig = go.Figure()
    if window_df.empty or "syn_count" not in window_df.columns:
        fig.update_layout(**BASE_LAYOUT, title=t("chart_syn_title", lang=l))
        return fig

    df = window_df.copy()
    if "time_window" in df.columns:
        # Use relative time in seconds from start
        min_t = df["time_window"].min()
        df["rel_time"] = df["time_window"] - min_t
        x_col = "rel_time"
        x_title = t("chart_rel_time", lang=l)
    else:
        df["window_idx"] = range(len(df))
        x_col = "window_idx"
        x_title = t("chart_window_idx", lang=l)

    # Separate normal windows from anomalous windows
    normal_mask = df.get("Anomaly", 1) == 1
    anomaly_mask = ~normal_mask

    # Continuous baseline line
    fig.add_trace(
        go.Scatter(
            x=df[x_col].tolist(),
            y=df["syn_count"].tolist(),
            mode="lines",
            line=dict(color=C_TEAL, width=2.2),
            name=t("chart_syn_nominal", lang=l),
            fill="tozeroy",
            fillcolor="rgba(45, 212, 191, 0.08)",
            hovertemplate="Time: %{x}s<br>SYN: %{y} pkts<extra>Nominal</extra>",
        )
    )

    # Highlight anomalies with glowing red diamonds
    anom_df = df[anomaly_mask]
    if not anom_df.empty:
        fig.add_trace(
            go.Scatter(
                x=anom_df[x_col].tolist(),
                y=anom_df["syn_count"].tolist(),
                mode="markers",
                marker=dict(
                    color=C_DANGER,
                    size=12,
                    symbol="diamond",
                    line=dict(width=1.5, color="#ffffff"),
                ),
                name=t("chart_syn_anomaly", lang=l),
                hovertemplate="ANOMALY<br>Time: %{x}s<br>SYN: %{y} pkts<extra>ALERT</extra>",
            )
        )

    layout = dict(BASE_LAYOUT)
    layout.update(
        title=dict(
            text=t("chart_syn_title", lang=l),
            font=dict(color="#f1f5f9", size=13),
        ),
        xaxis_title=x_title,
        yaxis_title=t("chart_syn_count", lang=l),
        height=320,
    )
    fig.update_layout(**layout)
    return fig


def create_attack_distribution_donut(window_df: pd.DataFrame, lang: Optional[str] = None) -> go.Figure:
    """
    Donut chart of attack types (SYN Scan vs SYN Flood vs Normal).
    """
    l = _get_lang(lang)
    fig = go.Figure()
    if window_df.empty or "Anomaly_Type" not in window_df.columns:
        fig.update_layout(**BASE_LAYOUT, title=t("chart_donut_title", lang=l))
        return fig

    counts = window_df["Anomaly_Type"].value_counts()
    labels = counts.index.tolist()
    values = counts.values.tolist()
    colors = [ATTACK_COLORS.get(lbl, C_MUTED) for lbl in labels]

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            marker=dict(colors=colors, line=dict(color="#07090e", width=2.5)),
            textinfo="percent+label",
            textposition="outside",
            textfont=dict(color="#f1f5f9", size=11),
            hovertemplate="<b>%{label}</b><br>Count: %{value} (%{percent})<extra></extra>",
        )
    )

    layout = dict(BASE_LAYOUT)
    layout.update(
        title=dict(
            text=t("chart_donut_title", lang=l),
            font=dict(color="#f1f5f9", size=13),
        ),
        height=320,
        showlegend=False,
    )
    fig.update_layout(**layout)
    return fig


def create_top_sources_bar(
    packet_df: pd.DataFrame, window_df: pd.DataFrame = None, top_n: int = 10, lang: Optional[str] = None
) -> go.Figure:
    """
    Horizontal bar chart of top source IP addresses by packet volume or flagged anomalies.
    """
    l = _get_lang(lang)
    fig = go.Figure()
    if packet_df.empty or "Src_Address" not in packet_df.columns:
        fig.update_layout(**BASE_LAYOUT, title=t("chart_top_ips_title", lang=l, n=top_n))
        return fig

    # Filter out N/A if present
    valid_df = packet_df[packet_df["Src_Address"] != "N/A"]
    if valid_df.empty:
        valid_df = packet_df

    ip_counts = valid_df["Src_Address"].value_counts().head(top_n)
    # Sort ascending for horizontal bar chart (highest at top)
    ip_counts = ip_counts.iloc[::-1]

    # Flag if IP is in anomalous windows
    anom_ips = set()
    if window_df is not None and not window_df.empty and "Src_Address" in window_df.columns:
        anom_subset = window_df[window_df.get("Anomaly", 1) == -1]
        anom_ips = set(anom_subset["Src_Address"].unique())

    colors = [C_DANGER if ip in anom_ips else C_CYAN for ip in ip_counts.index]

    fig.add_trace(
        go.Bar(
            x=ip_counts.values.tolist(),
            y=ip_counts.index.tolist(),
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="rgba(255,255,255,0.1)", width=0.5),
            ),
            hovertemplate="IP: %{y}<br>Packets: %{x:,}<extra></extra>",
        )
    )

    layout = dict(BASE_LAYOUT)
    layout.update(
        title=dict(
            text=t("chart_top_ips_title", lang=l, n=top_n),
            font=dict(color="#f1f5f9", size=13),
        ),
        xaxis_title=t("chart_pkt_count", lang=l),
        yaxis_title=t("col_source_ip", lang=l),
        height=320,
    )
    fig.update_layout(**layout)
    return fig


def create_anomaly_score_histogram(scores: pd.Series, contamination: float = 0.05, lang: Optional[str] = None) -> go.Figure:
    """
    Histogram of Isolation Forest anomaly scores with vertical anomaly threshold marker.
    """
    l = _get_lang(lang)
    fig = go.Figure()
    if scores is None or scores.empty:
        fig.update_layout(**BASE_LAYOUT, title=t("chart_hist_title", lang=l))
        return fig

    fig.add_trace(
        go.Histogram(
            x=scores.tolist(),
            nbinsx=35,
            marker=dict(
                color=C_TEAL,
                opacity=0.8,
                line=dict(color="#07090e", width=1),
            ),
            name="Score Distribution",
            hovertemplate="Score: %{x}<br>Count: %{y}<extra></extra>",
        )
    )

    # Calculate threshold (approximate contamination percentile)
    thresh = scores.quantile(contamination)
    fig.add_vline(
        x=thresh,
        line_width=2,
        line_dash="dash",
        line_color=C_DANGER,
        annotation_text=t("chart_hist_threshold", lang=l),
        annotation_position="top left",
        annotation_font=dict(color=C_DANGER, size=10),
    )

    layout = dict(BASE_LAYOUT)
    layout.update(
        title=dict(
            text=t("chart_hist_title", lang=l),
            font=dict(color="#f1f5f9", size=13),
        ),
        xaxis_title=t("chart_hist_score", lang=l),
        yaxis_title=t("chart_hist_samples", lang=l),
        height=320,
    )
    fig.update_layout(**layout)
    return fig


def create_layer1_scatter(packet_df: pd.DataFrame, lang: Optional[str] = None) -> go.Figure:
    """
    Layer 1 scatter plot: Packet length vs index with anomalies colored by type.
    """
    l = _get_lang(lang)
    fig = go.Figure()
    if packet_df.empty or "Length" not in packet_df.columns:
        fig.update_layout(**BASE_LAYOUT, title=t("chart_l1_title", lang=l))
        return fig

    normal = packet_df[packet_df.get("Anomaly", 1) == 1]
    abnormal = packet_df[packet_df.get("Anomaly", 1) == -1]

    # Normal packets
    fig.add_trace(
        go.Scattergl(
            x=normal.index.tolist(),
            y=normal["Length"].tolist(),
            mode="markers",
            marker=dict(color="#0d9488", size=3, opacity=0.35),
            name="Normal",
            hovertemplate="Packet #%{x}<br>Length: %{y} bytes<extra>Normal</extra>",
        )
    )

    # Anomaly points grouped by type
    if not abnormal.empty:
        for atype, grp in abnormal.groupby("Anomaly_Type"):
            col = ATTACK_COLORS.get(atype, C_DANGER)
            fig.add_trace(
                go.Scattergl(
                    x=grp.index.tolist(),
                    y=grp["Length"].tolist(),
                    mode="markers",
                    marker=dict(
                        color=col,
                        size=7,
                        opacity=0.9,
                        line=dict(width=0.5, color="#ffffff"),
                    ),
                    name=str(atype),
                    hovertemplate=f"Packet #%{{x}}<br>Length: %{{y}} bytes<extra>{atype}</extra>",
                )
            )

    layout = dict(BASE_LAYOUT)
    layout.update(
        title=dict(
            text=t("chart_l1_title", lang=l),
            font=dict(color="#f1f5f9", size=13),
        ),
        xaxis_title=t("chart_l1_pkt_num", lang=l),
        yaxis_title=t("chart_l1_pkt_len", lang=l),
        height=340,
    )
    fig.update_layout(**layout)
    return fig
