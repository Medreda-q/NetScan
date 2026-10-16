"""
i18n.py — NetScan Internationalisation Helper
==============================================
Author: Mohamed Reda QIYAOUI

Loads locale JSON files from the locales/ directory and exposes a simple
t(key, **kwargs) function to translate UI strings.

Supported languages: French (fr), English (en), Spanish (es).
"""

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_LOCALE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales")
_SUPPORTED = {"fr": "Français ", "en": "English ", "es": "Español "}
_DEFAULT_LANG = "fr"

_cache: dict[str, dict[str, Any]] = {}


def load_locale(lang: str) -> dict[str, Any]:
    """Load and cache a locale file. Falls back to French on error."""
    if lang in _cache:
        return _cache[lang]
    path = os.path.join(_LOCALE_DIR, f"{lang}.json")
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        _cache[lang] = data
        logger.debug("Locale loaded: %s", lang)
        return data
    except FileNotFoundError:
        logger.warning("Locale file not found for lang=%s", lang)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse locale %s: %s", lang, exc)
    # Fallback: return empty dict (avoids infinite recursion if default is also broken)
    if lang != _DEFAULT_LANG:
        return load_locale(_DEFAULT_LANG)
    _cache[lang] = {}
    return {}


def t(key: str, lang: str = _DEFAULT_LANG, **kwargs: Any) -> str:
    """
    Translate a UI string key into the chosen language.

    Parameters
    ----------
    key  : str — key from the locale JSON (e.g. "kpi_total")
    lang : str — language code ("fr", "en", "es")
    **kwargs : optional format substitutions (e.g. type="Port Scan", ip="10.0.0.1")

    Returns
    -------
    Translated string, or the key itself if not found.
    """
    locale = load_locale(lang)
    text = locale.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text


def get_supported_languages() -> dict[str, str]:
    """Return {code: display_name} for all supported languages."""
    return dict(_SUPPORTED)

