"""Token accounting for the Opus harness.

Prices are USD per million tokens. input_tokens, cache writes, and cache
reads are disjoint in the Messages API usage object, so each token is priced
once. A missing cache-write split is treated as a 5-minute write, which is
the default ephemeral TTL.
"""

from __future__ import annotations

import fcntl
import json
import os
from dataclasses import dataclass
from pathlib import Path


class BudgetError(RuntimeError):
    """The ledger cannot be trusted, so spending stops."""


@dataclass(frozen=True)
class Prices:
    input: float
    output: float
    cache_write_5m: float
    cache_write_1h: float
    cache_read: float

    def cost(
        self,
        *,
        input_tokens: int,
        output_tokens: int,
        cache_write_5m_tokens: int,
        cache_write_1h_tokens: int,
        cache_read_tokens: int,
    ) -> float:
        million = 1_000_000.0
        return (
            input_tokens * self.input
            + output_tokens * self.output
            + cache_write_5m_tokens * self.cache_write_5m
            + cache_write_1h_tokens * self.cache_write_1h
            + cache_read_tokens * self.cache_read
        ) / million


def load_prices(path: Path | None = None) -> Prices:
    """Load pricing.json, then let OPUS_PRICE_*_PER_MTOK override a rate."""
    default = Path(__file__).resolve().parent / "pricing.json"
    payload = json.loads((path or default).read_text(encoding="utf-8"))
    rates = payload["usd_per_mtok"]

    def rate(env_name: str, key: str) -> float:
        raw = os.environ.get(env_name, "").strip()
        if raw:
            return float(raw)
        return float(rates[key])

    return Prices(
        input=rate("OPUS_PRICE_INPUT_PER_MTOK", "input"),
        output=rate("OPUS_PRICE_OUTPUT_PER_MTOK", "output"),
        cache_write_5m=rate("OPUS_PRICE_CACHE_WRITE_5M_PER_MTOK", "cache_write_5m"),
        cache_write_1h=rate("OPUS_PRICE_CACHE_WRITE_1H_PER_MTOK", "cache_write_1h"),
        cache_read=rate("OPUS_PRICE_CACHE_READ_PER_MTOK", "cache_read"),
    )


def parse_usage(usage: dict | None) -> dict[str, int]:
    """Split a Messages usage object into billable buckets.

    cache_creation_input_tokens equals the sum of the cache_creation split.
    Pricing uses the split so a 1-hour write is not also billed as a 5-minute
    write. With no split, the whole creation total is a 5-minute write.
    """
    usage = usage or {}
    creation = usage.get("cache_creation") or {}
    write_5m = creation.get("ephemeral_5m_input_tokens")
    write_1h = creation.get("ephemeral_1h_input_tokens")
    total_creation = int(usage.get("cache_creation_input_tokens") or 0)
    if write_5m is None and write_1h is None:
        five = total_creation
        hour = 0
    else:
        five = int(write_5m or 0)
        hour = int(write_1h or 0)
    return {
        "input_tokens": int(usage.get("input_tokens") or 0),
        "output_tokens": int(usage.get("output_tokens") or 0),
        "cache_write_5m_tokens": five,
        "cache_write_1h_tokens": hour,
        "cache_read_tokens": int(usage.get("cache_read_input_tokens") or 0),
    }


def global_cap(cli_value: float | None) -> float:
    if cli_value is not None:
        return float(cli_value)
    raw = os.environ.get("OPUS_BUDGET_USD", "").strip()
    if raw:
        return float(raw)
    return 21.0


class Ledger:
    """Append-only spend log. A corrupt line refuses further spending."""

    def __init__(self, path: Path, cap_usd: float):
        self.path = path
        self.cap_usd = float(cap_usd)

    def spent(self) -> float:
        return self._read_total()

    def remaining(self) -> float:
        return self.cap_usd - self.spent()

    def charge(self, row: dict) -> dict:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            handle.seek(0)
            total = _sum_lines(handle.read(), self.path)
            cost = float(row["cost_usd"])
            spent = total + cost
            recorded = dict(row)
            recorded["spent_usd"] = round(spent, 8)
            recorded["remaining_usd"] = round(self.cap_usd - spent, 8)
            recorded["cap_usd"] = self.cap_usd
            handle.seek(0, os.SEEK_END)
            handle.write(json.dumps(recorded, sort_keys=True) + "\n")
            handle.flush()
        return recorded

    def _read_total(self) -> float:
        if not self.path.exists():
            return 0.0
        with self.path.open("r", encoding="utf-8") as handle:
            fcntl.flock(handle, fcntl.LOCK_SH)
            return _sum_lines(handle.read(), self.path)


def _sum_lines(text: str, path: Path) -> float:
    total = 0.0
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            total += float(row["cost_usd"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise BudgetError(
                f"ledger {path} line {line_number} is unreadable; refusing to spend"
            ) from exc
    return total
