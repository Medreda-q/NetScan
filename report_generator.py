"""
NetScan — Executive Incident Report Generator
Author: Mohamed Reda QIYAOUI

Generates executive-ready HTML & printable PDF incident forensic reports.
"""

import base64
from datetime import datetime
import os


def _get_report_logo_tag() -> str:
    """Returns an inline base64 image tag for the official NetScan logo."""
    svg_path = os.path.join(os.path.dirname(__file__), "assets", "netscan_logo.svg")
    png_path = os.path.join(os.path.dirname(__file__), "assets", "netscan_logo.png")
    if os.path.exists(svg_path):
        with open(svg_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            return f'<img src="data:image/svg+xml;base64,{b64}" class="header-logo" alt="NetScan Logo" />'
    elif os.path.exists(png_path):
        with open(png_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
            return f'<img src="data:image/png;base64,{b64}" class="header-logo" alt="NetScan Logo" />'
    return ""


def generate_html_incident_report(
    session_stats=None,
    anomalous_windows=None,
    packet_anomalies_sample=None,
):
    """
    Generate a standalone, styled executive cybersecurity incident report in HTML format.
    Includes print CSS rules allowing 1-click browser "Save as PDF".

    Parameters
    ----------
    session_stats : dict
        - total_packets
        - total_windows
        - port_scan_count
        - flood_count
        - packet_anomaly_count
        - source_target (e.g., 'Live Network Interface' or pcap filename)
    anomalous_windows : list of dicts or pd.DataFrame
    packet_anomalies_sample : list of dicts or pd.DataFrame

    Returns
    -------
    str : HTML document string
    """
    stats = session_stats or {}
    total_pkts = stats.get("total_packets", 0)
    total_wins = stats.get("total_windows", 0)
    port_scans = stats.get("port_scan_count", 0)
    floods = stats.get("flood_count", 0)
    pkt_anomalies = stats.get("packet_anomaly_count", 0)
    source_target = stats.get("source_target", "Session Réseau / Capture PCAP")
    now_str = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")

    # Anomalous windows table rows
    window_rows = ""
    if anomalous_windows is not None and len(anomalous_windows) > 0:
        records = anomalous_windows if isinstance(anomalous_windows, list) else anomalous_windows.to_dict("records")
        for w in records[:30]:  # limit to top 30
            src = w.get("Src_Address", w.get("src_address", "N/A"))
            atype = w.get("Anomaly_Type", w.get("anomaly_type", "Anomaly"))
            pkts = w.get("packet_count", "N/A")
            ports = w.get("unique_dst_ports", "N/A")
            time_w = w.get("time_window", "N/A")
            badge_class = "badge-danger" if "Port Scan" in str(atype) or "Flood" in str(atype) else "badge-warning"
            window_rows += f"""
            <tr>
                <td><code>{src}</code></td>
                <td><span class="badge {badge_class}">{atype}</span></td>
                <td>{pkts}</td>
                <td>{ports}</td>
                <td>{time_w}</td>
            </tr>
            """
    else:
        window_rows = """
        <tr>
            <td colspan="5" style="text-align: center; color: #888;">Aucune anomalie comportementale temporelle enregistrée.</td>
        </tr>
        """

    logo_tag = _get_report_logo_tag()

    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport d'Incident Forensic — NetScan</title>
    <style>
        :root {{
            --primary: #0066cc;
            --danger: #d93025;
            --warning: #f29900;
            --success: #188038;
            --dark: #1e293b;
            --light: #f8fafc;
            --border: #e2e8f0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #333;
            background: #f1f5f9;
            margin: 0;
            padding: 20px;
        }}
        .report-container {{
            max-width: 960px;
            margin: 0 auto;
            background: #ffffff;
            padding: 40px 50px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--primary);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header-brand {{
            display: flex;
            align-items: center;
            gap: 18px;
        }}
        .header-logo {{
            width: 58px;
            height: 58px;
            display: block;
        }}
        .header h1 {{
            margin: 0;
            font-size: 26px;
            color: var(--dark);
        }}
        .header p {{
            margin: 5px 0 0;
            color: #64748b;
            font-size: 14px;
        }}
        .meta-box {{
            text-align: right;
            font-size: 13px;
            color: #475569;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }}
        .kpi-card {{
            background: var(--light);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }}
        .kpi-num {{
            font-size: 28px;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 4px;
        }}
        .kpi-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #64748b;
        }}
        h2 {{
            font-size: 18px;
            color: var(--dark);
            border-left: 4px solid var(--primary);
            padding-left: 10px;
            margin-top: 35px;
            margin-bottom: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: #f8fafc;
            color: #475569;
            font-weight: 600;
        }}
        code {{
            background: #f1f5f9;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: Consolas, monospace;
            font-size: 12px;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-danger {{ background: #fce8e6; color: var(--danger); }}
        .badge-warning {{ background: #fef3d6; color: #b06000; }}
        .badge-success {{ background: #e6f4ea; color: var(--success); }}
        .recommendation-box {{
            background: #e0f2fe;
            border-left: 4px solid var(--primary);
            padding: 15px;
            border-radius: 4px;
            font-size: 13px;
            line-height: 1.5;
            color: #0369a1;
        }}
        .btn-print {{
            display: inline-block;
            background: var(--primary);
            color: white;
            padding: 10px 18px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            border: none;
            margin-bottom: 20px;
        }}
        .btn-print:hover {{ background: #0052a3; }}
        @media print {{
            body {{ background: #ffffff; padding: 0; }}
            .report-container {{ box-shadow: none; padding: 0; max-width: 100%; }}
            .btn-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <button class="btn-print" onclick="window.print()">🖨️ Imprimer ou Enregistrer en PDF</button>

        <div class="header">
            <div class="header-brand">
                {logo_tag}
                <div>
                    <h1>Rapport d'Incident & d'Analyse Forensic</h1>
                    <p>Système de Détection d'Intrusions Réseau (NIDS NetScan)</p>
                </div>
            </div>
            <div class="meta-box">
                <div><strong>Analyste :</strong> Mohamed Reda QIYAOUI</div>
                <div><strong>Système :</strong> NetScan NIDS/NIPS</div>
                <div><strong>Généré le :</strong> {now_str}</div>
                <div><strong>Cible :</strong> {source_target}</div>
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-num">{total_pkts:,}</div>
                <div class="kpi-label">Paquets Analysés</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-num" style="color: var(--danger);">{port_scans}</div>
                <div class="kpi-label">Scans de Ports (Nmap)</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-num" style="color: #c5221f;">{floods}</div>
                <div class="kpi-label">Attaques Flood / DDoS</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-num" style="color: var(--warning);">{pkt_anomalies:,}</div>
                <div class="kpi-label">Anomalies Microscopiques</div>
            </div>
        </div>

        <h2>1. Synthèse Exécutive</h2>
        <p style="font-size: 14px; line-height: 1.6; color: #475569;">
            Le moteur NetScan a opéré une inspection multi-niveaux basée sur l'algorithme d'apprentissage non supervisé <strong>Isolation Forest</strong>. 
            L'analyse comportementale macroscopique a permis d'isoler des signatures de reconnaissance offensive (balayage séquentiel de ports TCP SYN) ainsi que des anomalies volumétriques 
            sans recourir à des signatures statiques préalables.
        </p>

        <h2>2. Anomalies Comportementales Macroscopiques (Layer 2)</h2>
        <table>
            <thead>
                <tr>
                    <th>Adresse Source</th>
                    <th>Type d'Attaque / Comportement</th>
                    <th>Volume Paquets</th>
                    <th>Ports Cibles</th>
                    <th>Fenêtre Temporelle</th>
                </tr>
            </thead>
            <tbody>
                {window_rows}
            </tbody>
        </table>

        <h2>3. Recommandations et Plan de Remédiation (Standards NIST / CIS)</h2>
        <div class="recommendation-box">
            <strong>Directives de Sécurité Recommandées :</strong>
            <ul style="margin: 8px 0 0; padding-left: 20px;">
                <li><strong>Filtrage Pare-feu :</strong> Restreindre ou isoler les adresses IP sources ayant émis des signatures SYN scans consécutives.</li>
                <li><strong>Inspection des Services Exposés :</strong> Examiner les journaux des serveurs ciblant les ports récurrents identifiés dans ce rapport.</li>
                <li><strong>Durcissement des Politiques Réseau :</strong> Mettre en œuvre le rate-limiting sur les paquets TCP SYN pour neutraliser les dénis de service volumétriques.</li>
                <li><strong>Corrélation SIEM :</strong> Transférer les alertes vers le SOC via les webhooks automatisés pour corrélation croisée avec l'Active Directory.</li>
            </ul>
        </div>

        <div style="margin-top: 40px; border-top: 1px solid var(--border); padding-top: 15px; font-size: 12px; color: #94a3b8; text-align: center;">
            Rapport certifié généré par la plateforme NetScan — Auteur : Mohamed Reda QIYAOUI — Septembre 2026
        </div>
    </div>
</body>
</html>
"""
    return html
