from __future__ import annotations

import os
from ..utils.key_store import KeyStore


def ensure_environment_from_store() -> None:
    store = KeyStore.load()
    if store.google_api_key and not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = store.google_api_key
    if store.tavily_api_key and not os.environ.get("TAVILY_API_KEY"):
        os.environ["TAVILY_API_KEY"] = store.tavily_api_key


