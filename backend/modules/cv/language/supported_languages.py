from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SupportedLanguage:
    """
    Supported language definition.
    """

    code: str
    name: str


SUPPORTED_LANGUAGES: dict[str, SupportedLanguage] = {
    "en": SupportedLanguage("en", "English"),
    "es": SupportedLanguage("es", "Spanish"),
    "pt": SupportedLanguage("pt", "Portuguese"),
    "fr": SupportedLanguage("fr", "French"),
    "de": SupportedLanguage("de", "German"),
    "it": SupportedLanguage("it", "Italian"),
    "nl": SupportedLanguage("nl", "Dutch"),
    "pl": SupportedLanguage("pl", "Polish"),
    "sv": SupportedLanguage("sv", "Swedish"),
    "no": SupportedLanguage("no", "Norwegian"),
    "da": SupportedLanguage("da", "Danish"),
    "fi": SupportedLanguage("fi", "Finnish"),
}


DEFAULT_LANGUAGE = SupportedLanguage(
    code="unknown",
    name="Unknown",
)