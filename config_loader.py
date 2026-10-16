"""
config_loader.py — NetScan Configuration Loader
================================================
Author: Mohamed Reda QIYAOUI

Reads config.yaml once at startup and exposes a typed get() helper.
Falls back to safe defaults if the file is missing or malformed.
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
_config: dict[str, Any] = {}


def load_config(path: str = _CONFIG_PATH) -> dict[str, Any]:
    """Parse config.yaml and cache the result. Call once at startup."""
    global _config
    try:
        import yaml  # optional dependency
        with open(path, "r", encoding="utf-8") as f:
            _config = yaml.safe_load(f) or {}
        logger.info("Config loaded from %s", path)
    except ImportError:
        logger.warning("PyYAML not installed — using built-in defaults. Run: pip install pyyaml")
        _config = _defaults()
    except FileNotFoundError:
        logger.warning("config.yaml not found at %s — using defaults", path)
        _config = _defaults()
    except Exception as exc:
        logger.error("Failed to load config.yaml: %s — using defaults", exc)
        _config = _defaults()
    return _config


def get(key: str, default: Any = None) -> Any:
    """
    Retrieve a config value using dot-notation.

    Examples
    --------
    get("layer2.contamination")  -> 0.02
    get("live.calibration_seconds") -> 120
    get("app.default_language") -> "fr"
    """
    if not _config:
        load_config()
    parts = key.split(".")
    node: Any = _config
    for part in parts:
        if isinstance(node, dict):
            node = node.get(part)
        else:
            return default
        if node is None:
            return default
    return node


def setup_logging() -> None:
    """Configure application-wide logging from config.yaml settings."""
    if not _config:
        load_config()
    level_str: str = get("app.log_level", "INFO")
    log_file: str | None = get("app.log_file")
    level = getattr(logging, level_str.upper(), logging.INFO)

    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    logging.getLogger("pyshark").setLevel(logging.WARNING)
    logger.info("Logging initialised — level=%s  file=%s", level_str, log_file or "console only")


def _defaults() -> dict[str, Any]:
    """Minimal safe defaults if config.yaml cannot be read."""
    return {
        "app": {"version": "1.0.0", "default_language": "fr", "log_level": "INFO", "log_file": None},
        "layer1": {"contamination": 0.05, "random_state": 42, "features": ["Length", "Timestamp"]},
        "layer2": {
            "contamination": 0.02, "random_state": 42, "window_size_seconds": 5,
            "features": ["packet_count", "avg_packet_length", "unique_dst_ports", "unique_dst_ips", "syn_count"],
            "scan": {"min_packets": 2, "broad_sweep_ports": 15, "stealth_min_ports": 8, "stealth_ratio": 0.60,
                     "syn_min_ports": 5, "syn_count_min": 5, "syn_ratio_min": 0.35,
                     "hard_scan_min_ports": 25, "hard_scan_min_ratio": 0.50},
            "flood": {"syn_flood_min": 15, "syn_flood_ratio_min": 8, "syn_ratio_trigger": 0.20,
                      "volumetric_min_packets": 400, "volumetric_max_ports": 3,
                      "volumetric_min_avg_len": 900, "volumetric_extreme_pkt": 1200,
                      "hard_flood_syn_min": 30, "hard_flood_pkt_min": 500,
                      "hard_flood_avg_len_min": 800, "hard_flood_extreme_pkt": 1200},
        },
        "live": {"calibration_seconds": 120, "monitor_window_seconds": 5, "exclude_local_ip": True},
        "alerting": {"log_file": "alerts_history.json", "max_entries": 1000, "auto_firewall_rule": True},
        "dashboard": {"page_title": "NetScan — NIDS/IPS", "max_packets_display": 5000, "chart_height": 340},
    }

