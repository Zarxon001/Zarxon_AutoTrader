"""Strict local CSV reader. No network or broker dependencies."""
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


def number(value, field, *, allow_zero=False):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field}: son bo'lishi kerak.") from None
    if not result.is_finite() or result < 0 or (not allow_zero and result == 0):
        raise ValueError(f"{field}: chekli {'manfiy bo‘lmagan' if allow_zero else 'musbat'} son kerak.")
    return result


def load_csv(path):
    candles = []
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"timestamp", "open", "high", "low", "close", "volume"}
        if reader.fieldnames is None or set(reader.fieldnames) != required or len(reader.fieldnames) != len(required):
            raise ValueError("CSV ustunlari: timestamp,open,high,low,close,volume.")
        for row in reader:
            line = reader.line_num
            try:
                if None in row or any(value is None or not value.strip() for value in row.values()):
                    raise ValueError("Bo'sh yoki ortiqcha maydon.")
                stamp = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
                if stamp.tzinfo is None or stamp.utcoffset() is None:
                    raise ValueError("Vaqt uchun UTC Z yoki aniq timezone kerak.")
                stamp = stamp.astimezone(timezone.utc)
                if candles and stamp <= candles[-1].timestamp:
                    raise ValueError("Vaqtlar qat'iy o'sib borishi kerak.")
                prices = [number(row[key], key) for key in ("open", "high", "low", "close")]
                opening, high, low, close = prices
                if low > min(opening, close) or high < max(opening, close) or low > high:
                    raise ValueError("OHLC chegaralari noto'g'ri.")
                candles.append(Candle(stamp, *prices, number(row["volume"], "volume", allow_zero=True)))
            except (ValueError, TypeError) as error:
                raise ValueError(f"CSV {line}-qator: {error}") from None
    if not candles:
        raise ValueError("CSV bo'sh.")
    return candles
