"""
geoip_resolver.py -- NetScan GeoIP & Threat Origin Resolution
==============================================================
Author: Mohamed Reda QIYAOUI
Network Intrusion Detection & Analysis System (NIDS/NIPS)

Resolves IP addresses to their geographical origin (Country, City, ISP/Org).
Features:
  - Immediate local RFC 1918 recognition (LAN, Loopback, Carrier-Grade NAT)
  - In-memory LRU caching to eliminate redundant lookups
  - Non-blocking timeout (1.5s max) with graceful offline fallback
  - Pure ASCII formatting (no emojis, professional cyber notation like [FR], [US], [LAN])
"""

import functools
import ipaddress
import logging
import urllib.request
import json
from typing import Dict, Any

logger = logging.getLogger(__name__)


def is_private_or_special_ip(ip_str: str) -> bool:
    """Check if an IP address is private, loopback, link-local, or reserved."""
    try:
        clean_ip = str(ip_str).split()[0].strip()
        ip_obj = ipaddress.ip_address(clean_ip)
        return (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_reserved
            or ip_obj.is_multicast
        )
    except Exception:
        return True


@functools.lru_cache(maxsize=2048)
def resolve_ip_geo(ip_str: str) -> Dict[str, Any]:
    """
    Resolve IP to geographic origin with caching and offline resilience.
    Returns:
      {
        "country": str,
        "country_code": str,
        "city": str,
        "org": str,
        "is_private": bool,
        "display": str
      }
    """
    if not ip_str or ip_str in ("-", "N/A", "None", "Inconnue", "localhost"):
        return {
            "country": "Inconnu",
            "country_code": "N/A",
            "city": "-",
            "org": "Non identifie",
            "is_private": False,
            "display": "[--] Inconnu",
        }

    clean_ip = str(ip_str).split()[0].strip()

    # Validate IP address format
    try:
        ip_obj = ipaddress.ip_address(clean_ip)
    except Exception:
        return {
            "country": "Non-IP",
            "country_code": "N/A",
            "city": "-",
            "org": "Format Invalide",
            "is_private": False,
            "display": "[--] Non-IP",
        }

    # Handle Private / Local Subnets immediately without network requests
    if ip_obj.is_loopback:
        return {
            "country": "Hote Local",
            "country_code": "HOST",
            "city": "Loopback",
            "org": "127.0.0.1",
            "is_private": True,
            "display": "[HOST] Hote Local (127.0.0.1)",
        }

    if ip_obj.is_private or ip_obj.is_link_local or ip_obj.is_reserved:
        return {
            "country": "Reseau Prive",
            "country_code": "LAN",
            "city": "Segment Local",
            "org": "RFC 1918",
            "is_private": True,
            "display": "[LAN] Reseau Prive (Interne)",
        }

    # Public WAN IP Resolution via lightweight REST endpoint
    url = f"http://ip-api.com/json/{clean_ip}?fields=status,message,country,countryCode,city,isp,org,as"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "NetScan-NIDS-SOC/1.0"},
    )

    try:
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "success":
                    country = data.get("country", "Inconnu")
                    cc = data.get("countryCode", "WAN")
                    city = data.get("city", "")
                    org = data.get("org") or data.get("isp") or "Fournisseur Inconnu"
                    
                    loc_part = f"{city}, {country}" if city else country
                    display_str = f"[{cc}] {loc_part} ({org})"

                    return {
                        "country": country,
                        "country_code": cc,
                        "city": city,
                        "org": org,
                        "is_private": False,
                        "display": display_str,
                    }
    except Exception as exc:
        logger.debug("GeoIP lookup failed for %s: %s", clean_ip, exc)

    # Offline / Fallback resolution for public IP
    return {
        "country": "Public WAN",
        "country_code": "WAN",
        "city": "Externe",
        "org": "Non resolu",
        "is_private": False,
        "display": "[WAN] Public Externe",
    }
