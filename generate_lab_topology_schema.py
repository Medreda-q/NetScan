import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_lab_topology(theme='light', filename='schema_lab_topology_fr.png'):
    # Dimensions: 16:9 widescreen format, 300 DPI
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=300)
    
    bg_color = '#ffffff'
    border_color = '#000000'
    text_color = '#000000'
    subtext_color = '#334155'
    net_border = '#0284c7'
    net_bg = '#f0f9ff'
    
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    
    # Cadre extérieur global
    rect_border = patches.Rectangle((0.25, 0.25), 11.5, 7.0, linewidth=1.8, edgecolor=border_color, facecolor='none')
    ax.add_patch(rect_border)
    
    # Grand conteneur : Hyperviseur / Laboratoire Isolé
    lab_box = patches.FancyBboxPatch((0.6, 1.2), 10.8, 5.7, boxstyle="round,pad=0.15", 
                                     edgecolor='#2563eb', facecolor='#f8fafc', linewidth=2.0, linestyle='--')
    ax.add_patch(lab_box)
    
    # Titre du conteneur Lab
    ax.text(0.85, 6.65, "ENVIRONNEMENT DE TEST VIRTUEL ISOLÉ (Hyperviseur / Réseau Host-Only)", 
            fontsize=11.5, weight='bold', color='#1e3a8a', ha='left')
    ax.text(0.85, 6.35, "Sous-réseau sécurisé : 192.168.56.0/24 — Confinement total des flux d'attaque", 
            fontsize=9.5, color='#475569', ha='left')
    
    # -------------------------------------------------------------
    # 1. VM 1 : Machine Attaquante (Kali Linux)
    # -------------------------------------------------------------
    kali_box = patches.FancyBboxPatch((0.9, 3.2), 3.0, 2.7, boxstyle="round,pad=0.1",
                                      edgecolor='#dc2626', facecolor='#ffffff', linewidth=2.2)
    ax.add_patch(kali_box)
    
    # Header Kali
    kali_header = patches.Rectangle((0.9, 5.3), 3.0, 0.6, edgecolor='#dc2626', facecolor='#fee2e2', linewidth=1.5)
    ax.add_patch(kali_header)
    ax.text(2.4, 5.6, "MACHINE ATTAQUANTE", fontsize=11, weight='bold', color='#991b1b', ha='center', va='center')
    
    ax.text(2.4, 4.95, "Kali Linux 2024.x", fontsize=12, weight='bold', color='#111827', ha='center')
    ax.text(2.4, 4.60, "IP : 192.168.56.101", fontsize=10, weight='bold', color='#dc2626', ha='center')
    
    tools_kali = "• Nmap (-sS Stealth Scan)\n• Hping3 (SYN Flood DDoS)\n• Scapy (Trames anormales)"
    ax.text(1.15, 3.85, tools_kali, fontsize=9, color='#374151', va='center', linespacing=1.4)
    
    # -------------------------------------------------------------
    # 2. COMMUTATEUR VIRTUEL (Virtual Switch / Vmnet)
    # -------------------------------------------------------------
    switch_box = patches.FancyBboxPatch((4.5, 4.2), 3.0, 1.4, boxstyle="round,pad=0.1",
                                        edgecolor='#2563eb', facecolor='#eff6ff', linewidth=2.0)
    ax.add_patch(switch_box)
    ax.text(6.0, 5.15, "COMMUTATEUR VIRTUEL", fontsize=11, weight='bold', color='#1e40af', ha='center')
    ax.text(6.0, 4.80, "Mode Promiscuous / Port Mirroring", fontsize=9.2, weight='bold', color='#2563eb', ha='center')
    ax.text(6.0, 4.48, "Duplication passive des trames", fontsize=8.5, color='#475569', ha='center')
    
    # -------------------------------------------------------------
    # 3. VM 2 : Machine Cible (Metasploitable 2)
    # -------------------------------------------------------------
    target_box = patches.FancyBboxPatch((8.1, 3.2), 3.0, 2.7, boxstyle="round,pad=0.1",
                                        edgecolor='#16a34a', facecolor='#ffffff', linewidth=2.2)
    ax.add_patch(target_box)
    
    # Header Target
    target_header = patches.Rectangle((8.1, 5.3), 3.0, 0.6, edgecolor='#16a34a', facecolor='#dcfce7', linewidth=1.5)
    ax.add_patch(target_header)
    ax.text(9.6, 5.6, "SERVEUR CIBLE (VICTIME)", fontsize=10.5, weight='bold', color='#166534', ha='center', va='center')
    
    ax.text(9.6, 4.95, "Metasploitable 2", fontsize=12, weight='bold', color='#111827', ha='center')
    ax.text(9.6, 4.60, "IP : 192.168.56.102", fontsize=10, weight='bold', color='#16a34a', ha='center')
    
    services = "• Ports ouverts : 21, 22, 80, 445\n• Services : Apache, SSH, VSFTPD\n• Backlog TCP queue vulnérable"
    ax.text(8.35, 3.85, services, fontsize=8.8, color='#374151', va='center', linespacing=1.4)
    
    # -------------------------------------------------------------
    # 4. SONDE D'ANALYSE & DÉTECTION (NetScan NIDS)
    # -------------------------------------------------------------
    probe_box = patches.FancyBboxPatch((4.0, 1.35), 4.0, 2.0, boxstyle="round,pad=0.1",
                                       edgecolor='#7c3aed', facecolor='#faf5ff', linewidth=2.4)
    ax.add_patch(probe_box)
    
    # Header Probe
    probe_header = patches.Rectangle((4.0, 2.85), 4.0, 0.5, edgecolor='#7c3aed', facecolor='#f3e8ff', linewidth=1.5)
    ax.add_patch(probe_header)
    ax.text(6.0, 3.10, "SONDE NETSCAN (NIDS HYBRIDE)", fontsize=11, weight='bold', color='#6b21a8', ha='center', va='center')
    
    ax.text(6.0, 2.62, "Station de Supervision & Analyse SOC", fontsize=10.2, weight='bold', color='#1e1b4b', ha='center')
    ax.text(6.0, 2.36, "Capture passive (Npcap / Libpcap) — IP : 192.168.56.1", fontsize=8.5, weight='bold', color='#6b21a8', ha='center')
    
    probe_desc = "• Modèle ML : Isolation Forest (contamination=0.03)\n• Moteur de Règles Heuristiques (Scan & Flood)\n• Dashboard Streamlit & Alerting Discord instantané"
    ax.text(4.25, 1.82, probe_desc, fontsize=8.5, color='#374151', va='center', linespacing=1.35)
    
    # -------------------------------------------------------------
    # LIAISONS & FLUX DE PAQUETS (Flèches)
    # -------------------------------------------------------------
    # Flux d'attaque Kali -> Switch -> Target
    ax.annotate('', xy=(4.5, 4.9), xytext=(3.9, 4.9),
                arrowprops=dict(arrowstyle="-|>", color='#dc2626', lw=2.8, mutation_scale=16))
    ax.text(4.2, 5.2, "Attaque", fontsize=8.5, weight='bold', color='#dc2626', ha='center')
    
    ax.annotate('', xy=(8.1, 4.9), xytext=(7.5, 4.9),
                arrowprops=dict(arrowstyle="-|>", color='#dc2626', lw=2.8, mutation_scale=16))
    ax.text(7.8, 5.2, "Scans / SYN", fontsize=8.5, weight='bold', color='#dc2626', ha='center')
    
    # Flux miroir Switch -> Sonde NetScan
    ax.annotate('', xy=(6.0, 3.4), xytext=(6.0, 4.2),
                arrowprops=dict(arrowstyle="-|>", color='#7c3aed', lw=2.6, linestyle='--', mutation_scale=16))
    
    # Badge Miroir SPAN
    span_badge = patches.FancyBboxPatch((6.25, 3.65), 1.9, 0.45, boxstyle="round,pad=0.06",
                                        facecolor='#ede9fe', edgecolor='#7c3aed', linewidth=1.2)
    ax.add_patch(span_badge)
    ax.text(7.2, 3.87, "Miroir SPAN (Passif)", fontsize=8, weight='bold', color='#6b21a8', ha='center', va='center')
    
    # -------------------------------------------------------------
    # Bas de page : Titre officiel de la figure
    # -------------------------------------------------------------
    title_line = patches.Rectangle((1.5, 0.92), 9.0, 0.03, facecolor='#0f172a', edgecolor='none')
    ax.add_patch(title_line)
    
    ax.text(6.0, 0.65, "Figure 1.1 : Topologie du laboratoire d'expérimentation virtualisé", 
            fontsize=12, weight='bold', color='#0f172a', ha='center')
    ax.text(6.0, 0.38, "Environnement sécurisé reproduisant l'infrastructure de test (Attaquant Kali, Cible Metasploitable 2 et Sonde NetScan)", 
            fontsize=9.5, style='italic', color='#475569', ha='center')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, facecolor=bg_color, bbox_inches='tight')
    plt.close()
    print(f"[+] Figure 1.1 générée avec succès : {filename}")

if __name__ == '__main__':
    draw_lab_topology('light', 'schema_lab_topology_fr.png')
