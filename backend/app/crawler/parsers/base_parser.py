from abc import ABC, abstractmethod


class BaseParser(ABC):
    """Base interface for source-specific parsers."""

    @abstractmethod
    def parse(self, html: str, source_url: str) -> list[dict]:
        """Extract advisory records from HTML."""
        raise NotImplementedError

    def get_next_page(
        self,
        html: str,
        current_url: str,
    ) -> str | None:
        """Return the next page URL if pagination exists."""
        return None