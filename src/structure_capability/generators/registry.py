from __future__ import annotations


class GeneratorRegistry:
    """Small explicit registry for built-in and downstream generator providers."""

    def __init__(self):
        self._by_alias = {}
        self._providers = []

    def register(self, provider):
        if provider in self._providers:
            return
        aliases = tuple(str(x).lower() for x in provider.aliases)
        if not aliases:
            raise ValueError("generator provider must declare at least one alias")
        for alias in aliases:
            if alias in self._by_alias:
                raise ValueError(f"generator alias already registered: {alias}")
            self._by_alias[alias] = provider
        self._providers.append(provider)

    def resolve(self, kind: str | None):
        return self._by_alias.get(str(kind or "").lower())

    def describe(self):
        return [provider.describe() for provider in self._providers]
