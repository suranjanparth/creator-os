"""Creator-scoped ingestion: normalize and persist creator identity and content."""

from app.domains.ingestion.service import import_creator

__all__ = ["import_creator"]
