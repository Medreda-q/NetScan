import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_stage_topology_syn_flood(filename='schema_stage_commune_fr.png'):
    # Dimensions: 16:9 widescreen format, 300 DPI
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=300)
    
    bg_color = '#ffffff'
    border_color = '#000000'
    
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    
    # 1. Cadre extérieur global
    rect_border = patches.Rectangle((0.25, 0.25), 11.5, 7.0, linewidth=1.8, edgecolor=border_color, facecolor='none')
    ax.add_patch(rect_border)
    
    # 2. Grand conteneur : Environnement Réel - Commune de Tétouan
    commune_box = patches.FancyBboxPatch((0.5, 1.15), 11.0, 5.8, boxstyle="round,pad=0.15", 
                                         edgecolor='#dc2626', facecolor='#fef2f2', linewidth=2.0, linestyle='--')
    ax.add_patch(commune_box)
    
    # Titre du conteneur
    ax.text(0.8, 6.65, "SCÉNARIO 2 : SIMULATION D'INONDATION SYN FLOOD (LAN COMMUNE)", 
            fontsize=12, weight='bold', color='#991b1b', ha='left')
    ax.text(0.8, 6.35, "Réseau Local (192.168.1.0/24) — Test de saturation volumétrique de la cible via Hping3", 
            fontsize=9.2, color='#475569', ha='left')
    
    # -------------------------------------------------------------
    # POSTE 1 : Machine Émettrice / Attaquant (Hping3)
    # -------------------------------------------------------------
    pc1_box = patches.FancyBboxPatch((0.8, 1.8), 3.2, 4.2, boxstyle="round,pad=0.12",
                                     edgecolor='#dc2626', facecolor='#ffffff', linewidth=2.2)
    ax.add_patch(pc1_box)
    
    # Header PC 1
    pc1_header = patches.Rectangle((0.8, 5.4), 3.2, 0.6, edgecolor='#dc2626', facecolor='#fee2e2', linewidth=1.5)
    ax.add_patch(pc1_header)
    ax.text(2.4, 5.7, "POSTE 1 : ATTAQUANT (DDoS)", fontsize=11, weight='bold', color='#991b1b', ha='center', va='center')
    
    ax.text(2.4, 5.05, "Machine d'Émission d'Attaque", fontsize=11, weight='bold', color='#0f172a', ha='center')
    ax.text(2.4, 4.75, "Réseau Local Commune", fontsize=9.2, color='#64748b', ha='center')
    
    ip1_badge = patches.FancyBboxPatch((1.25, 4.3), 2.3, 0.35, boxstyle="round,pad=0.05",
                                       edgecolor='#dc2626', facecolor='#fff1f2', linewidth=1.2)
    ax.add_patch(ip1_badge)
    ax.text(2.4, 4.47, "IP : 192.168.1.45", fontsize=9.5, weight='bold', color='#b91c1c', ha='center', va='center')
    
    pc1_details = (
        "• Outil offensif : Hping3\n"
        "• Commande exécutée :\n"
        "   hping3 --flood -S -p 80 [Cible]\n"
        "• Type : Inondation TCP SYN massive\n"
        "• Cadence : > 800 paquets / 5 sec\n"
        "• Cible : Port unique 80 (HTTP)\n"
        "• Objectif : Saturation Backlog Queue"
    )
    ax.text(1.0, 3.05, pc1_details, fontsize=8.6, color='#1f2937', va='center', linespacing=1.35)
    
    # -------------------------------------------------------------
    # COMMUTATEUR PHYSIQUE (Switch Réseau de la Commune)
    # -------------------------------------------------------------
    switch_box = patches.FancyBboxPatch((4.4, 2.5), 3.2, 2.8, boxstyle="round,pad=0.1",
                                        edgecolor='#2563eb', facecolor='#ffffff', linewidth=2.0)
    ax.add_patch(switch_box)
    
    # Header Switch
    switch_header = patches.Rectangle((4.4, 4.7), 3.2, 0.6, edgecolor='#2563eb', facecolor='#dbeafe', linewidth=1.5)
    ax.add_patch(switch_header)
    ax.text(6.0, 5.0, "COMMUTATEUR LAN", fontsize=11, weight='bold', color='#1e40af', ha='center', va='center')
    
    ax.text(6.0, 4.35, "Switch Réseau Physique", fontsize=10.5, weight='bold', color='#0f172a', ha='center')
    ax.text(6.0, 4.05, "Câblage Ethernet Cat 6 (1 Gbps)", fontsize=9, color='#475569', ha='center')
    ax.text(6.0, 3.75, "Routage direct sans filtrage externe", fontsize=8.5, style='italic', color='#64748b', ha='center')
    
    # Note trafic switch
    switch_note = patches.FancyBboxPatch((4.6, 2.75), 2.8, 0.75, boxstyle="round,pad=0.06",
                                         edgecolor='#fca5a5', facecolor='#fef2f2', linewidth=1.0)
    ax.add_patch(switch_note)
    ax.text(6.0, 3.12, "Transit du flux d'inondation", fontsize=8.2, weight='bold', color='#b91c1c', ha='center')
    ax.text(6.0, 2.90, "Saturation volumétrique sans ACK retour", fontsize=7.8, color='#dc2626', ha='center')
    
    # -------------------------------------------------------------
    # POSTE 2 : Machine Cible & Sonde NetScan (Windows)
    # -------------------------------------------------------------
    pc2_box = patches.FancyBboxPatch((8.0, 1.8), 3.2, 4.2, boxstyle="round,pad=0.12",
                                     edgecolor='#16a34a', facecolor='#ffffff', linewidth=2.2)
    ax.add_patch(pc2_box)
    
    # Header PC 2
    pc2_header = patches.Rectangle((8.0, 5.4), 3.2, 0.6, edgecolor='#16a34a', facecolor='#dcfce7', linewidth=1.5)
    ax.add_patch(pc2_header)
    ax.text(9.6, 5.7, "POSTE 2 : CIBLE & SONDE", fontsize=11, weight='bold', color='#166534', ha='center', va='center')
    
    ax.text(9.6, 5.05, "Poste Physique Windows", fontsize=11.5, weight='bold', color='#0f172a', ha='center')
    ax.text(9.6, 4.75, "Station de supervision NetScan", fontsize=9.2, color='#64748b', ha='center')
    
    ip2_badge = patches.FancyBboxPatch((8.45, 4.3), 2.3, 0.35, boxstyle="round,pad=0.05",
                                       edgecolor='#16a34a', facecolor='#f0fdf4', linewidth=1.2)
    ax.add_patch(ip2_badge)
    ax.text(9.6, 4.47, "IP : 192.168.1.50 (Port 80)", fontsize=9.2, weight='bold', color='#15803d', ha='center', va='center')
    
    pc2_details = (
        "• Pilote : Npcap (Mode WinPcap)\n"
        "• Volumétrie observée : >800 paquets/5s\n"
        "• Ratio de diversité R < 0.01\n"
        "• Score d'anomalie IA : s = 0.92\n"
        "• Décision : Règle n°2 déclenchée\n"
        "• ALERTE CRITIQUE : Flood / DDoS\n"
        "• Notification Discord instantanée"
    )
    ax.text(8.2, 3.05, pc2_details, fontsize=8.5, color='#1f2937', va='center', linespacing=1.35)
    
    # -------------------------------------------------------------
    # LIAISONS & FLÈCHES RÉSEAU
    # -------------------------------------------------------------
    # Ligne de liaison physique PC1 <-> Switch
    ax.plot([4.0, 4.4], [3.9, 3.9], color='#2563eb', linewidth=2.5)
    
    # Ligne de liaison physique Switch <-> PC2
    ax.plot([7.6, 8.0], [3.9, 3.9], color='#2563eb', linewidth=2.5)
    
    # Flèche supérieure rouge (SYN Flood Hping3)
    ax.annotate('', xy=(4.4, 4.3), xytext=(4.0, 4.3),
                arrowprops=dict(arrowstyle="-|>", color='#dc2626', lw=2.8, mutation_scale=15))
    ax.text(4.2, 4.5, "Hping3", fontsize=8, weight='bold', color='#dc2626', ha='center')
    
    ax.annotate('', xy=(8.0, 4.3), xytext=(7.6, 4.3),
                arrowprops=dict(arrowstyle="-|>", color='#dc2626', lw=2.8, mutation_scale=15))
    ax.text(7.8, 4.5, "SYN Flood", fontsize=8, weight='bold', color='#dc2626', ha='center')
    
    # Flèche inférieure : Réponses en attente (SYN-ACK sans ACK)
    ax.annotate('', xy=(4.0, 3.5), xytext=(4.4, 3.5),
                arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=1.8, linestyle=':', mutation_scale=11))
    ax.text(4.2, 3.25, "(Pas d'ACK)", fontsize=7.5, color='#dc2626', weight='bold', ha='center')
    
    ax.annotate('', xy=(7.6, 3.5), xytext=(8.0, 3.5),
                arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=1.8, linestyle=':', mutation_scale=11))
    ax.text(7.8, 3.25, "SYN-ACK...", fontsize=7.5, color='#475569', ha='center')
    
    # -------------------------------------------------------------
    # Bas de page : Légende officielle
    # -------------------------------------------------------------
    title_line = patches.Rectangle((1.5, 0.92), 9.0, 0.03, facecolor='#0f172a', edgecolor='none')
    ax.add_patch(title_line)
    
    ax.text(6.0, 0.65, "Figure 5.2 : Détection expérimentale de l'inondation TCP SYN Flood (Hping3) par la sonde NetScan", 
            fontsize=11.5, weight='bold', color='#0f172a', ha='center')
    ax.text(6.0, 0.38, "Saturation volumétrique du port 80 générée par Hping3, capturée par Npcap et classée anomalie critique (s = 0.92)", 
            fontsize=9, style='italic', color='#475569', ha='center')
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, facecolor=bg_color, bbox_inches='tight')
    plt.close()
    print(f"[+] Schéma SYN Flood Hping3 généré avec succès : {filename}")

if __name__ == '__main__':
    draw_stage_topology_syn_flood('schema_stage_syn_flood_fr.png')
    draw_stage_topology_syn_flood('schema_stage_commune_fr.png')
