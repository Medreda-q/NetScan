#!/usr/bin/env python3
"""
NetScan — Network Traffic Anomaly Detection Platform
DUT Cybersecurity Stage d'Initiation (Septembre 2026)
Author: Mohamed Reda QIYAOUI

Kali-Style Terminal Launcher & Automatic Environment Bootstrapper
"""

import sys
import os
import platform
import subprocess
import argparse
import time
import logging

# Suppress noisy Scapy startup warnings
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
os.environ["SCAPY_USE_PCAP"] = "yes"

# ==============================================================================
# TERMINAL COLORS & BANNER (ANSI)
# ==============================================================================

class Colors:
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

# Enable VT100 on Windows cmd/powershell
if platform.system() == "Windows":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass


def print_banner():
    banner = f"""{Colors.CYAN}{Colors.BOLD}
 _   _      _   ____                  
| \\ | | ___| |_/ ___|  ___ __ _ _ __  
|  \\| |/ _ \\ __\\___ \\ / __/ _` | '_ \\ 
| |\\  |  __/ |_ ___) | (_| (_| | | | |
|_| \\_|\\___|\\__|____/ \\___\\__,_|_| |_|
{Colors.BLUE}Système de Détection d'Anomalies Réseau — Apprentissage Non Supervisé
{Colors.DIM}Auteur : Mohamed Reda QIYAOUI — DUT Cybersécurité (Septembre 2026){Colors.RESET}
"""
    print(banner)


# ==============================================================================
# DEPENDENCY AUTO-BOOTSTRAPPER
# ==============================================================================

CORE_PACKAGES = {
    "pandas": "pandas",
    "scapy": "scapy",
    "pyshark": "pyshark",
    "sklearn": "scikit-learn",
    "matplotlib": "matplotlib",
    "streamlit": "streamlit",
}


def check_and_install_python_packages():
    """Check for missing Python packages and auto-install them via pip."""
    missing = []
    for import_name, pip_name in CORE_PACKAGES.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print(f"{Colors.YELLOW}[!] Dépendances Python manquantes : {', '.join(missing)}{Colors.RESET}")
        print(f"{Colors.CYAN}[*] Installation automatique des paquets requis via pip...{Colors.RESET}")
        req_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
        extra_args = ["--break-system-packages"] if platform.system() == "Linux" else []
        try:
            if os.path.exists(req_file):
                cmd = [sys.executable, "-m", "pip", "install"] + extra_args + ["-r", req_file]
            else:
                cmd = [sys.executable, "-m", "pip", "install"] + extra_args + missing
            
            subprocess.check_call(cmd)

            print(f"{Colors.GREEN}[+] Toutes les dépendances Python ont été installées avec succès !{Colors.RESET}\n")
        except Exception as e:
            print(f"{Colors.RED}[-] Échec de l'installation automatique : {e}{Colors.RESET}")
            print(f"{Colors.YELLOW}[*] Veuillez exécuter manuellement : pip install -r requirements.txt{Colors.RESET}\n")
            return False
    return True


def is_admin():
    """Check if the current process has administrative / root privileges."""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False


def is_npcap_installed():
    """Check whether Npcap service or driver exists on Windows."""
    if platform.system() != "Windows":
        return True
    
    # Check 1: Npcap directory
    npcap_dir = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "Npcap")
    if os.path.exists(npcap_dir):
        return True

    # Check 2: Scapy interface discovery
    try:
        from scapy.all import get_if_list
        if len(get_if_list()) > 0:
            return True
    except Exception:
        pass

    # Check 3: sc query npcap
    try:
        res = subprocess.run(["sc", "query", "npcap"], capture_output=True, text=True)
        if "RUNNING" in res.stdout or "STATE" in res.stdout:
            return True
    except Exception:
        pass

    return False


def install_npcap_windows():
    """Offer automatic installation of Npcap on Windows."""
    print(f"\n{Colors.CYAN}[*] Démarrage de l'installation du pilote Npcap...{Colors.RESET}")

    # Méthode 1 : Tenter via winget si disponible
    winget_path = None
    try:
        res = subprocess.run(["where", "winget"], capture_output=True, text=True)
        if res.returncode == 0:
            winget_path = "winget"
    except Exception:
        pass

    if winget_path:
        print(f"{Colors.CYAN}[*] Tentative d'installation via winget...{Colors.RESET}")
        try:
            cmd = ["winget", "install", "Insecure.Npcap", "--accept-package-agreements", "--accept-source-agreements"]
            ret = subprocess.call(cmd)
            if ret == 0:
                print(f"{Colors.GREEN}[+] Npcap installé avec succès via winget !{Colors.RESET}")
                return True
        except Exception as e:
            print(f"{Colors.YELLOW}[!] Échec de l'installation via winget : {e}{Colors.RESET}")

    # Méthode 2 : Télécharger l'installateur officiel
    import urllib.request
    import tempfile

    installer_url = "https://npcap.com/dist/npcap-1.80.exe"
    temp_dir = tempfile.gettempdir()
    installer_path = os.path.join(temp_dir, "npcap_installer.exe")

    print(f"{Colors.CYAN}[*] Téléchargement de l'installateur Npcap officiel depuis {installer_url}...{Colors.RESET}")
    try:
        urllib.request.urlretrieve(installer_url, installer_path)
        print(f"{Colors.GREEN}[+] Téléchargement terminé ! Lancement de l'installateur...{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}>> IMPORTANT : Cochez 'Install Npcap in WinPcap API-compatible Mode' lors de l'installation <<{Colors.RESET}")
        
        # Exécution de l'installateur avec élévation
        if hasattr(os, "startfile"):
            os.startfile(installer_path)
        else:
            subprocess.Popen([installer_path], shell=True)
            
        print(f"{Colors.CYAN}[*] Veuillez terminer l'installation dans la fenêtre qui s'est ouverte, puis revenez ici.{Colors.RESET}")
        input("Appuyez sur Entrée une fois l'installation de Npcap terminée...")
        return is_npcap_installed()
    except Exception as e:
        print(f"{Colors.RED}[-] Échec du téléchargement automatique : {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}[*] Veuillez télécharger manuellement depuis : https://npcap.com/#download{Colors.RESET}")
        return False


def check_driver_health(verbose=True):
    """Diagnose packet capture driver and OS permissions."""
    os_name = platform.system()
    has_admin = is_admin()

    if verbose:
        print(f"{Colors.CYAN}[*] Système d'exploitation :{Colors.RESET} {os_name} ({platform.release()})")
        print(f"{Colors.CYAN}[*] Privilèges élevés :{Colors.RESET} {'Oui' if has_admin else 'Non'}")

    if os_name == "Windows":
        installed = is_npcap_installed()
        if verbose:
            print(f"{Colors.CYAN}[*] Pilote de capture Npcap :{Colors.RESET} {'Installé [OK]' if installed else 'INTROUVABLE [!]'}")
        
        if not installed:
            print(f"\n{Colors.YELLOW}[!] Windows nécessite Npcap (compatibilité WinPcap) pour la capture réseau en direct.{Colors.RESET}")
            ans = input("Souhaitez-vous télécharger et installer Npcap automatiquement ? [O/n] : ").strip().lower()
            if ans in ("", "o", "oui", "y", "yes"):
                installed = install_npcap_windows()

        if installed and not has_admin and verbose:
            print(f"{Colors.YELLOW}[!] Remarque : Pour la capture en direct, veuillez exécuter le terminal en tant qu'Administrateur.{Colors.RESET}")

        return installed

    elif os_name in ("Linux", "Darwin"):
        if verbose:
            print(f"{Colors.CYAN}[*] Support des sockets bruts Linux :{Colors.RESET} Intégré")
        if not has_admin and verbose:
            print(f"{Colors.YELLOW}[!] Attention : La capture réseau sous Linux nécessite les droits root/sudo.{Colors.RESET}")
        return True

    return True


# ==============================================================================
# MENU ACTIONS
# ==============================================================================

def action_live_monitoring():
    """Launch terminal-based live detection engine."""
    check_driver_health(verbose=False)
    from detection_engine import get_available_interfaces, run_live_detection

    print(f"\n{Colors.BOLD}{Colors.CYAN}--- Mode Surveillance en Direct (Calibration → Monitoring) ---{Colors.RESET}")
    available_ifaces = get_available_interfaces()
    if available_ifaces:
        print(f"{Colors.GREEN}[+] Interfaces réseau détectées :{Colors.RESET}")
        for idx, iface_name in enumerate(available_ifaces, start=1):
            print(f"  [{idx}] {iface_name}")
        iface_sel = input("Entrez le nom ou le numéro de l'interface (Entrée pour défaut) : ").strip()
        if iface_sel.isdigit() and 1 <= int(iface_sel) <= len(available_ifaces):
            chosen_iface = available_ifaces[int(iface_sel) - 1]
        else:
            chosen_iface = iface_sel if iface_sel else None
    else:
        chosen_iface = input("Entrez le nom de l'interface réseau (Entrée pour défaut) : ").strip() or None

    try:
        calib_sec = int(input("Durée de calibration en secondes [défaut : 120] : ").strip() or "120")
    except ValueError:
        calib_sec = 120

    try:
        win_sec = int(input("Taille de la fenêtre temporelle en secondes [défaut : 5] : ").strip() or "5")
    except ValueError:
        win_sec = 5

    try:
        run_live_detection(
            interface=chosen_iface,
            calibration_duration=calib_sec,
            window_size=win_sec,
        )
    except (PermissionError, RuntimeError) as pe:
        print(f"\n{Colors.RED}{pe}{Colors.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[*] Surveillance en direct arrêtée par l'utilisateur.{Colors.RESET}")


def action_pcap_forensics(pcap_path=None):
    """Run full offline Layer 1 & Layer 2 forensics on a PCAP file."""
    from detection_engine import (
        extract_features,
        detect_anomalies,
        analyze_anomalies,
        aggregate_windows,
        detect_window_anomalies,
    )

    if not pcap_path:
        default_pcap = "sample_nmap_attack.pcap"
        prompt = f"Chemin vers le fichier PCAP [défaut : {default_pcap}] : "
        pcap_path = input(prompt).strip() or default_pcap

    if not os.path.exists(pcap_path):
        print(f"{Colors.RED}[-] Fichier introuvable : {pcap_path}{Colors.RESET}")
        return

    try:
        window_size = int(input("Taille de la fenêtre d'agrégation en secondes [défaut : 5] : ").strip() or "5")
    except ValueError:
        window_size = 5

    print(f"\n{Colors.CYAN}[1] Extraction des paquets depuis {pcap_path}...{Colors.RESET}")
    data = extract_features(pcap_path)

    print(f"{Colors.CYAN}[2] Détection des anomalies par paquet (Couche 1)...{Colors.RESET}")
    analyzed_data = detect_anomalies(data)

    print(f"{Colors.CYAN}[3] Analyse des anomalies paquets...{Colors.RESET}")
    analyze_anomalies(analyzed_data)

    print(f"{Colors.CYAN}[4] Agrégation du trafic en fenêtres de {window_size}s...{Colors.RESET}")
    window_df = aggregate_windows(analyzed_data, window_size=window_size)

    print(f"{Colors.CYAN}[5] Détection des anomalies comportementales fenêtrées (Couche 2)...{Colors.RESET}")
    window_results = detect_window_anomalies(window_df)

    port_scans = (window_results["Anomaly_Type"] == "Port Scan").sum()
    floods = (window_results["Anomaly_Type"] == "Flood / DDoS").sum()
    pkt_anomalies = (analyzed_data["Anomaly"] == -1).sum()

    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"RÉSUMÉ DE L'ANALYSE FORENSIQUE")
    print(f"{'='*60}{Colors.RESET}")
    print(f"  Paquets analysés au total  : {len(analyzed_data):,}")
    print(f"  Anomalies par paquet       : {pkt_anomalies:,}  (Couche 1)")
    print(f"  Fenêtres — Scan de ports   : {port_scans:,}  (Couche 2 — fenêtre {window_size}s)")
    print(f"  Fenêtres — Flood / DDoS    : {floods:,}  (Couche 2 — fenêtre {window_size}s)")
    print(f"{'='*60}\n")


def action_launch_dashboard():
    """Launch Streamlit dashboard."""
    print(f"\n{Colors.CYAN}[*] Démarrage du tableau de bord Streamlit interactif...{Colors.RESET}")
    dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.py")
    cmd = [sys.executable, "-m", "streamlit", "run", dashboard_path]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[*] Tableau de bord arrêté.{Colors.RESET}")


def action_run_diagnostics():
    """Run test_smoke.py."""
    print(f"\n{Colors.CYAN}[*] Exécution de la suite de tests NetScan...{Colors.RESET}")
    test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_smoke.py")
    subprocess.run([sys.executable, test_path])



def action_test_discord():
    """Configure and test Discord webhook from terminal."""
    from alerting import load_config, save_config, test_discord_webhook

    cfg = load_config()
    current_url = cfg.get("discord_webhook_url", "")
    print(f"\n{Colors.BOLD}{Colors.CYAN}--- Configuration Webhook Discord ---{Colors.RESET}")
    print(f"URL actuelle : {current_url or '[Non configurée]'}")

    new_url = input("Entrez la nouvelle URL (ou appuyez sur Entrée pour garder l'actuelle) : ").strip()
    if new_url:
        cfg["discord_webhook_url"] = new_url
        save_config(cfg)
        current_url = new_url

    if current_url:
        print(f"{Colors.CYAN}[*] Envoi d'un message d'alerte de test à Discord...{Colors.RESET}")
        ok, msg = test_discord_webhook(current_url)
        if ok:
            print(f"{Colors.GREEN}[+] {msg}{Colors.RESET}")
        else:
            print(f"{Colors.RED}[-] {msg}{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}[!] Aucune URL de webhook configurée.{Colors.RESET}")


def action_generate_report():
    """Generate executive incident report from terminal."""
    from report_generator import generate_html_incident_report
    from detection_engine import load_alerts

    alerts = load_alerts()

    stats = {
        "total_packets": sum(a.get("packet_count", 0) for a in alerts),
        "total_windows": len(alerts),
        "port_scan_count": sum(1 for a in alerts if a.get("anomaly_type") == "Port Scan"),
        "flood_count": sum(1 for a in alerts if a.get("anomaly_type") == "Flood / DDoS"),
        "packet_anomaly_count": len(alerts),
        "source_target": "Session Terminal NetScan",
    }

    html = generate_html_incident_report(
        session_stats=stats,
        anomalous_windows=alerts,
    )

    out_file = "rapport_incident_netscan.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n{Colors.GREEN}[+] Rapport exécutif généré avec succès dans : {out_file}{Colors.RESET}")
    print(f"{Colors.CYAN}[*] Vous pouvez ouvrir ce fichier dans votre navigateur et l'enregistrer en PDF.{Colors.RESET}")


# ==============================================================================
# MAIN INTERACTIVE LOOP
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="NetScan — Plateforme de Détection d'Anomalies Réseau")
    parser.add_argument("--live", action="store_true", help="Démarrer directement la surveillance en direct")
    parser.add_argument("--pcap", type=str, help="Analyser un fichier PCAP en mode forensique hors ligne")
    parser.add_argument("--dashboard", action="store_true", help="Lancer directement le tableau de bord Streamlit")
    parser.add_argument("--check", action="store_true", help="Effectuer un diagnostic des dépendances et des pilotes")
    args = parser.parse_args()

    print_banner()

    # Step 1: Auto-check and install Python dependencies
    print(f"{Colors.BOLD}[*] Initialisation de l'environnement NetScan...{Colors.RESET}")
    check_and_install_python_packages()

    if args.check:
        print(f"\n{Colors.BOLD}--- Diagnostics Système & Pilotes ---{Colors.RESET}")
        check_driver_health(verbose=True)
        return

    if args.dashboard:
        action_launch_dashboard()
        return

    if args.live:
        action_live_monitoring()
        return

    if args.pcap:
        action_pcap_forensics(args.pcap)
        return

    # Interactive Kali-style terminal menu
    while True:
        print(f"\n{Colors.BOLD}Sélectionnez un mode opérationnel :{Colors.RESET}")
        print(f"  {Colors.GREEN}[1]{Colors.RESET} Surveillance en Direct (Calibration → Monitoring)")
        print(f"  {Colors.GREEN}[2]{Colors.RESET} Analyse Forensique PCAP Hors Ligne (Couche 1 & Couche 2)")
        print(f"  {Colors.GREEN}[3]{Colors.RESET} Lancer le Tableau de Bord Web Interactif (Streamlit)")
        print(f"  {Colors.GREEN}[4]{Colors.RESET} Exécuter les Diagnostics Système & Tests")
        print(f"  {Colors.GREEN}[5]{Colors.RESET} Vérifier / Installer les Pilotes de Capture Réseau")
        print(f"  {Colors.GREEN}[6]{Colors.RESET} Tester les Alertes Webhook Discord")
        print(f"  {Colors.GREEN}[7]{Colors.RESET} Générer le Rapport d'Incident Forensique (PDF/HTML)")
        print(f"  {Colors.RED}[0]{Colors.RESET} Quitter")

        choice = input(f"\n{Colors.BOLD}netscan > {Colors.RESET}").strip()

        if choice == "1":
            action_live_monitoring()
        elif choice == "2":
            action_pcap_forensics()
        elif choice == "3":
            action_launch_dashboard()
        elif choice == "4":
            action_run_diagnostics()
        elif choice == "5":
            check_driver_health(verbose=True)
        elif choice == "6":
            action_test_discord()
        elif choice == "7":
            action_generate_report()
        elif choice in ("0", "exit", "quit", "q"):
            print(f"\n{Colors.CYAN}Au revoir !{Colors.RESET}")
            break
        else:
            print(f"{Colors.YELLOW}[!] Option invalide. Veuillez choisir entre 0 et 7.{Colors.RESET}")



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrompu.")
