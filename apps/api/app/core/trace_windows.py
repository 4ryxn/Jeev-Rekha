"""Transparent operational review windows for the fictional synthetic demo dataset.

These settings are not clinical guidance, a diagnosis model, or a prediction model.
They exist solely to make the deterministic Trace Lab review window explicit.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TraceReviewWindow:
    canonical_name: str
    review_window_days: int
    source_label: str = "Configured synthetic demonstration review window — requires veterinary validation."


TRACE_REVIEW_WINDOWS: dict[str, TraceReviewWindow] = {
    "foot-and-mouth disease": TraceReviewWindow("Foot-and-mouth disease", 14),
    "peste des petits ruminants": TraceReviewWindow("Peste des petits ruminants", 14),
    "haemorrhagic septicaemia": TraceReviewWindow("Haemorrhagic septicaemia", 10),
}

DEFAULT_TRACE_REVIEW_WINDOW = TraceReviewWindow("Unconfigured synthetic disease", 14)


def get_trace_review_window(disease_name: str) -> TraceReviewWindow:
    """Return an explicit synthetic operational window for a stored disease name."""
    return TRACE_REVIEW_WINDOWS.get(disease_name.strip().casefold(), DEFAULT_TRACE_REVIEW_WINDOW)
