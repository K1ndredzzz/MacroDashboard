"""
Shared FRED series configuration.
Supports configurable gold series skip/replace behavior.
"""
from __future__ import annotations

import os
from typing import Iterable, List, Optional

DEFAULT_GOLD_SERIES_ID = "GOLDPMGBD228NLBM"

# Collector (PostgreSQL) series coverage
COLLECTOR_BASE_SERIES = [
    "DGS2",         # US 2Y Treasury
    "DGS10",        # US 10Y Treasury
    "FEDFUNDS",     # Federal Funds Rate
    "DEXUSEU",      # EUR/USD
    "DEXCHUS",      # USD/CNY
    "DEXJPUS",      # USD/JPY
    "DCOILWTICO",   # WTI Oil
    "CPIAUCSL",     # CPI
    "CPILFESL",     # Core CPI
    "UNRATE",       # Unemployment Rate
    "PAYEMS",       # Nonfarm Payrolls
    "CIVPART",      # Labor Force Participation
    "AHETPI"        # Average Hourly Earnings
]

# Cloud Function (BigQuery) series coverage
CLOUD_FUNCTION_BASE_SERIES = [
    "DGS2",         # US 2Y Treasury
    "DGS10",        # US 10Y Treasury
    "DGS30",        # US 30Y Treasury
    "DEXUSEU",      # EUR/USD
    "DEXJPUS",      # USD/JPY
    "DEXUSUK",      # GBP/USD
    "DCOILWTICO",   # WTI Oil
    "CPIAUCSL",     # CPI
    "CPILFESL",     # Core CPI
    "PPIACO",       # PPI
    "UNRATE",       # Unemployment Rate
    "PAYEMS"        # Nonfarm Payrolls
]

_TRUE_VALUES = {"1", "true", "yes", "y", "on"}
_FALSE_VALUES = {"0", "false", "no", "n", "off"}


def _parse_bool(value: object, default: bool, logger=None) -> bool:
    """Best-effort bool parser for env/request values."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in _TRUE_VALUES:
        return True
    if text in _FALSE_VALUES:
        return False

    if logger:
        logger.warning(f"Invalid boolean value '{value}', fallback to default={default}")
    return default


def _dedupe_keep_order(values: Iterable[str]) -> List[str]:
    """Deduplicate while preserving order."""
    output: List[str] = []
    for item in values:
        normalized = (item or "").strip()
        if not normalized:
            continue
        if normalized not in output:
            output.append(normalized)
    return output


def build_fred_series(
    base_series: Iterable[str],
    *,
    skip_gold_series: Optional[object] = None,
    gold_series_id: Optional[str] = None,
    logger=None
) -> List[str]:
    """
    Build final FRED series list.

    Behavior:
    - `SKIP_GOLD_SERIES=true` (default) => do not collect gold.
    - `SKIP_GOLD_SERIES=false` + `GOLD_SERIES_ID=...` => collect the configured gold series.
    """
    series = _dedupe_keep_order(base_series)

    if skip_gold_series is None:
        skip_gold_series = os.getenv("SKIP_GOLD_SERIES")
    skip_gold = _parse_bool(skip_gold_series, default=True, logger=logger)

    selected_gold_series = (gold_series_id or os.getenv("GOLD_SERIES_ID") or DEFAULT_GOLD_SERIES_ID).strip()

    if skip_gold:
        if logger:
            logger.info("Gold series collection is disabled (SKIP_GOLD_SERIES=true)")
        return series

    if not selected_gold_series:
        if logger:
            logger.warning("Gold series is enabled but GOLD_SERIES_ID is empty, skipping gold collection")
        return series

    if selected_gold_series in series:
        return series

    # Keep gold near oil for readability.
    if "DCOILWTICO" in series:
        insert_idx = series.index("DCOILWTICO") + 1
        series.insert(insert_idx, selected_gold_series)
    else:
        series.append(selected_gold_series)

    if logger:
        logger.info(f"Gold series enabled: {selected_gold_series}")
    return series
