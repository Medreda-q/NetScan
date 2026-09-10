import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_syn_flood_diagram(theme='light', filename='schema_syn_flood_fr.png'):
    # Dimensions: 16:9 widescreen format, 300 DPI
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=300)
    
    if theme == 'dark':
        bg_color = '#0b132b'
        box_bg = '#1c2541'
        box_border = '#48cae4'
        text_color = '#ffffff'
        subtext_color = '#94a3b8'
        axis_line_color = '#64dfdf'
        red_color = '#ff4d6d'
        blue_color = '#38bdf8'
        purple_color = '#c084fc'
        alert_bg = '#2a113a'
        border_color = '#334155'
        line_box_bg = '#0b132b'
    else:
        bg_color = '#ffffff'
        box_bg = '#ffffff'
        box_border = '#000000'
        text_color = '#000000'
        subtext_color = '#475569'
        axis_line_color = '#000000'
        red_color = '#c53030'
        blue_color = '#1d4ed8'
        purple_color = '#7e22ce'
        alert_bg = '#fdf2f8'
        border_color = '#000000'
        line_box_bg = '#ffffff'
        
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    
    # Outer frame
    rect_border = patches.Rectangle((0.25, 0.25), 11.5, 7.0, linewidth=1.8, edgecolor=border_color, facecolor='none')
    ax.add_patch(rect_border)

    # -------------------------------------------------------------
    # Top Header Boxes: Attaquant (Hping3) vs Serveur (Cible)
    # -------------------------------------------------------------
    x_client = 3.2
    x_server = 8.8
    box_w, box_h = 2.9, 0.95
    
    # Attacker box
    box_left = patches.Rectangle((x_client - box_w/2, 5.8), box_w, box_h, linewidth=2.0, edgecolor=box_border, facecolor=box_bg, zorder=3)
    ax.add_patch(box_left)
    ax.text(x_client, 6.4, "Attaquant (DDoS)", fontsize=13.5, weight='bold', color=text_color, ha='center', va='center')
    ax.text(x_client, 6.02, "Hping3 / Botnet (IPs spoofées)", fontsize=10.5, color=subtext_color, ha='center', va='center')

    # Server box
    box_right = patches.Rectangle((x_server - box_w/2, 5.8), box_w, box_h, linewidth=2.0, edgecolor=box_border, facecolor=box_bg, zorder=3)
    ax.add_patch(box_right)
    ax.text(x_server, 6.4, "Serveur Cible (Victime)", fontsize=13.5, weight='bold', color=text_color, ha='center', va='center')
    ax.text(x_server, 6.02, "Port Unique Cible (ex: 80 / HTTP)", fontsize=10.5, color=subtext_color, ha='center', va='center')

    # -------------------------------------------------------------
    # Vertical Timeline Bars
    # -------------------------------------------------------------
    y_top = 5.8
    y_bottom = 1.35
    ax.plot([x_client, x_client], [y_bottom, y_top], color=axis_line_color, linewidth=4.0, zorder=2)
    ax.plot([x_server, x_server], [y_bottom, y_top], color=axis_line_color, linewidth=4.0, zorder=2)

    pad = 0.35
    mid_x = (x_client + x_server) / 2

    # -------------------------------------------------------------
    # Burst 1: Inondation de paquets SYN (3 flèches inclinées)
    # -------------------------------------------------------------
    syn_offsets = [(5.3, 4.8), (4.9, 4.4), (4.5, 4.0)]
    for y_s, y_e in syn_offsets:
        ax.annotate('', xy=(x_server, y_e), xytext=(x_client, y_s),
                    arrowprops=dict(arrowstyle="-|>", color=red_color, lw=2.4, mutation_scale=16))
    
    # Text on top of burst arrows
    ax.text(mid_x, 5.2, "Rafale massive de paquets SYN", fontsize=13, weight='bold', color=red_color, ha='center', va='center', rotation=-5.5,
            bbox=dict(boxstyle="round,pad=0.2", facecolor=line_box_bg, edgecolor='none'))
    
    # Left annotation
    ax.text(x_client - pad, 5.25, "Envoie des milliers de 'SYN'", fontsize=11, weight='bold', color=red_color, ha='right', va='center')
    ax.text(x_client - pad, 4.95, "vers le même port (ex: 80)", fontsize=10, color=red_color, ha='right', va='center')
    ax.text(x_client - pad, 4.55, "Adresses IP sources usurpées", fontsize=9.5, style='italic', color=subtext_color, ha='right', va='center')

    # -------------------------------------------------------------
    # Server Action: Réserve mémoire + Réponse SYN-ACK
    # -------------------------------------------------------------
    y2_s, y2_e = 3.65, 3.15
    ax.annotate('', xy=(x_client, y2_e), xytext=(x_server, y2_s),
                arrowprops=dict(arrowstyle="-|>", color=blue_color, lw=2.4, mutation_scale=18, linestyle='--'))
    
    # Text with protective background so dashed line doesn't cross text
    ax.text(mid_x, 3.5, "SYN + ACK (En attente de réponse...)", fontsize=12, weight='bold', color=blue_color, ha='center', va='center', rotation=5.5,
            bbox=dict(boxstyle="round,pad=0.25", facecolor=line_box_bg, edgecolor=blue_color, lw=0.8))
    
    # Right annotation: Allocation mémoire & Backlog
    ax.text(x_server + pad, 4.35, "Alloue de la mémoire (TCB)", fontsize=11, weight='bold', color=red_color, ha='left', va='center')
    ax.text(x_server + pad, 4.0, "Stocke dans la « Backlog Queue »", fontsize=10, color=text_color, ha='left', va='center')
    ax.text(x_server + pad, 3.65, "Répond par 'SYN + ACK'", fontsize=9.5, color=blue_color, ha='left', va='center')

    # -------------------------------------------------------------
    # Attacker Action: SILENCE (Jamais d'ACK) + Saturation
    # -------------------------------------------------------------
    # Left annotation: Silence radio
    ax.text(x_client - pad, 2.7, "[!] Aucun ACK retourné", fontsize=11.5, weight='bold', color=purple_color, ha='right', va='center')
    ax.text(x_client - pad, 2.35, "L'attaquant ignore les SYN+ACK", fontsize=9.5, color=purple_color, ha='right', va='center')
    ax.text(x_client - pad, 2.05, "Connexions laissées ouvertes", fontsize=9.5, style='italic', color=subtext_color, ha='right', va='center')

    # Right Box: Backlog Saturée & DoS
    box_dos = patches.FancyBboxPatch((x_server + 0.35, 1.75), 2.65, 1.25, boxstyle="round,pad=0.15",
                                     linewidth=2.0, edgecolor=red_color, facecolor=alert_bg, zorder=3)
    ax.add_patch(box_dos)
    ax.text(x_server + 1.67, 2.6, "SATURATION BACKLOG", fontsize=11.5, weight='bold', color=red_color, ha='center', va='center')
    ax.text(x_server + 1.67, 2.22, "File d'attente pleine", fontsize=10, weight='bold', color=text_color, ha='center', va='center')
    ax.text(x_server + 1.67, 1.88, "Déni de Service (DoS total)", fontsize=9.5, color=red_color, ha='center', va='center')

    # -------------------------------------------------------------
    # Bottom Title (styled with underline / bold like user's image)
    # -------------------------------------------------------------
    main_title = "TCP SYN Flood (DDoS Volumétrique) — Saturation de la Backlog Queue"
    ax.text(6.0, 0.85, main_title, fontsize=15, weight='bold', color=text_color, ha='center', va='center')
    
    # Underline
    ax.plot([1.6, 10.4], [0.66, 0.66], color=text_color, linewidth=1.5)
    
    # Sub-caption
    caption = "Le serveur réserve des ressources pour chaque SYN sans jamais recevoir d'ACK → La file déborde, le service devient inaccessible"
    ax.text(6.0, 0.45, caption, fontsize=9.5, style='italic', color=subtext_color, ha='center', va='center')

    plt.tight_layout()
    plt.savefig(filename, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Generated: {filename}")

draw_syn_flood_diagram(theme='light', filename='schema_syn_flood_fr.png')
draw_syn_flood_diagram(theme='dark', filename='schema_syn_flood_fr_dark.png')
