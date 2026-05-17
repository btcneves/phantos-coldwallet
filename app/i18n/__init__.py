from __future__ import annotations

from app.i18n.strings import STRINGS

_lang: str = "pt_BR"


def set_language(lang: str) -> None:
    global _lang
    if lang in STRINGS:
        _lang = lang


def current_language() -> str:
    return _lang


def tr(key: str, **kwargs: object) -> str:
    catalog = STRINGS.get(_lang, STRINGS["pt_BR"])
    text = catalog.get(key, STRINGS["pt_BR"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text
