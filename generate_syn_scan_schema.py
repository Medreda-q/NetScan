import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_syn_scan_diagram(theme='light', filename='schema_nmap_syn_scan_fr.png'):
    # Dimensions: 16:9 widescreen format, high DPI
    fig, ax = plt.subplots(figsize=(12, 6.75), dpi=300)
    
    if theme == 'dark':
        bg_color = '#0b132b'
        box_bg = '#1c2541'
        box_border = '#48cae4'
        text_color = '#ffffff'
        subtext_color = '#94a3b8'
        axis_line_color = '#64dfdf'
        red_color = '#ff5964'
        blue_color = '#38bdf8'
        yellow_color = '#facc15'
        border_color = '#334155'
    else:
        bg_color = '#ffffff'
        box_bg = '#ffffff'
        box_border = '#000000'
        text_color = '#000000'
        subtext_color = '#475569'
        axis_line_color = '#000000'
        red_color = '#c53030'
        blue_color = '#1d4ed8'
        yellow_color = '#b45309'
        border_color = '#000000'
        
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    
    # Outer frame like reference image
    rect_border = patches.Rectangle((0.25, 0.25), 11.5, 7.0, linewidth=1.8, edgecolor=border_color, facecolor='none')
    ax.add_patch(rect_border)

    # -------------------------------------------------------------
    # Top Header Boxes: Client (Attaquant) vs Serveur (Cible)
    # -------------------------------------------------------------
    # Vertical line centers: x_client = 3.2, x_server = 8.8
    x_client = 3.2
    x_server = 8.8
    box_w, box_h = 2.8, 0.95
    
    # Client box
    box_left = patches.Rectangle((x_client - box_w/2, 5.8), box_w, box_h, linewidth=2.0, edgecolor=box_border, facecolor=box_bg, zorder=3)
    ax.add_patch(box_left)
    ax.text(x_client, 6.4, "Client (Attaquant)", fontsize=13.5, weight='bold', color=text_color, ha='center', va='center')
    ax.text(x_client, 6.02, "Nmap (-sS)", fontsize=11, color=subtext_color, ha='center', va='center')

    # Server box
    box_right = patches.Rectangle((x_server - box_w/2, 5.8), box_w, box_h, linewidth=2.0, edgecolor=box_border, facecolor=box_bg, zorder=3)
    ax.add_patch(box_right)
    ax.text(x_server, 6.4, "Serveur (Cible)", fontsize=13.5, weight='bold', color=text_color, ha='center', va='center')
    ax.text(x_server, 6.02, "Port Ouvert (ex: 80 / HTTP)", fontsize=10.5, color=subtext_color, ha='center', va='center')

    # -------------------------------------------------------------
    # Vertical Timeline Bars
    # -------------------------------------------------------------
    y_top = 5.8
    y_bottom = 1.35
    ax.plot([x_client, x_client], [y_bottom, y_top], color=axis_line_color, linewidth=4.0, zorder=2)
    ax.plot([x_server, x_server], [y_bottom, y_top], color=axis_line_color, linewidth=4.0, zorder=2)

    # Margins for annotations
    pad = 0.35

    # -------------------------------------------------------------
    # Step 1: SYN [seq = m]
    # -------------------------------------------------------------
    y1_start, y1_end = 5.1, 4.5
    ax.annotate('', xy=(x_server, y1_end), xytext=(x_client, y1_start),
                arrowprops=dict(arrowstyle="-|>", color=red_color, lw=2.8, mutation_scale=20))
    
    # Label above arrow
    mid_x = (x_client + x_server) / 2
    ax.text(mid_x, 4.95, "SYN", fontsize=14, weight='bold', color=red_color, ha='center', va='center', rotation=-5.5)
    
    # Left annotation (Client sends)
    ax.text(x_client - pad, 5.25, "Envoie 'SYN'", fontsize=11, weight='bold', color=red_color, ha='right', va='center')
    ax.text(x_client - pad, 4.95, "(seq = m)", fontsize=10, color=red_color, ha='right', va='center')
    
    # Right annotation (Server receives)
    ax.text(x_server + pad, 4.65, "Reçoit 'SYN'", fontsize=11, weight='bold', color=red_color, ha='left', va='center')
    ax.text(x_server + pad, 4.35, "(seq = m)", fontsize=10, color=red_color, ha='left', va='center')

    # -------------------------------------------------------------
    # Step 2: SYN + ACK [seq = n, ack = m+1]
    # -------------------------------------------------------------
    y2_start, y2_end = 3.85, 3.25
    ax.annotate('', xy=(x_client, y2_end), xytext=(x_server, y2_start),
                arrowprops=dict(arrowstyle="-|>", color=blue_color, lw=2.8, mutation_scale=20))
    
    # Label above arrow
    ax.text(mid_x, 3.7, "SYN + ACK", fontsize=14, weight='bold', color=blue_color, ha='center', va='center', rotation=5.5)
    
    # Right annotation (Server sends)
    ax.text(x_server + pad, 4.0, "Envoie 'SYN + ACK'", fontsize=11, weight='bold', color=blue_color, ha='left', va='center')
    ax.text(x_server + pad, 3.7, "(seq = n, ack = m+1)", fontsize=9.5, color=blue_color, ha='left', va='center')
    
    # Left annotation (Client receives)
    ax.text(x_client - pad, 3.4, "Reçoit 'SYN + ACK'", fontsize=11, weight='bold', color=blue_color, ha='right', va='center')
    ax.text(x_client - pad, 3.1, "(Port confirmé OUVERT)", fontsize=9.5, color=blue_color, ha='right', va='center')

    # -------------------------------------------------------------
    # Step 3: RST [Reset] - The Stealth Attack Signature
    # -------------------------------------------------------------
    y3_start, y3_end = 2.55, 1.95
    ax.annotate('', xy=(x_server, y3_end), xytext=(x_client, y3_start),
                arrowprops=dict(arrowstyle="-|>", color=yellow_color, lw=2.8, mutation_scale=20))
    
    # Label above arrow
    ax.text(mid_x, 2.4, "RST (Reset)", fontsize=14, weight='bold', color=yellow_color, ha='center', va='center', rotation=-5.5)
    
    # Left annotation (Client sends RST instead of final ACK)
    ax.text(x_client - pad, 2.7, "Envoie 'RST' (Pas d'ACK !)", fontsize=11, weight='bold', color=yellow_color, ha='right', va='center')
    ax.text(x_client - pad, 2.4, "(Interrompt la connexion)", fontsize=9.5, color=yellow_color, ha='right', va='center')
    
    # Right annotation (Server closes half-open socket)
    ax.text(x_server + pad, 2.1, "Reçoit 'RST'", fontsize=11, weight='bold', color=yellow_color, ha='left', va='center')
    ax.text(x_server + pad, 1.8, "(Ferme sans log applicatif)", fontsize=9.5, color=yellow_color, ha='left', va='center')

    # -------------------------------------------------------------
    # Bottom Title (styled with underline / bold like user's image)
    # -------------------------------------------------------------
    main_title = "TCP SYN Stealth Scan (Nmap -sS) — Connexion « Half-Open »"
    ax.text(6.0, 0.85, main_title, fontsize=15, weight='bold', color=text_color, ha='center', va='center')
    
    # Underline
    ax.plot([1.8, 10.2], [0.66, 0.66], color=text_color, linewidth=1.5)
    
    # Sub-caption
    caption = "L'attaquant n'envoie jamais le dernier 'ACK' : la connexion n'est jamais établie → Furtif et invisible dans les logs applicatifs"
    ax.text(6.0, 0.45, caption, fontsize=9.5, style='italic', color=subtext_color, ha='center', va='center')

    plt.tight_layout()
    plt.savefig(filename, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"Generated: {filename}")

draw_syn_scan_diagram(theme='light', filename='schema_nmap_syn_scan_fr.png')
draw_syn_scan_diagram(theme='dark', filename='schema_nmap_syn_scan_fr_dark.png')
