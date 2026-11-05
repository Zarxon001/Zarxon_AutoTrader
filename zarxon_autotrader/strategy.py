"""SMA crossover demo. Returns data; has no execution interface."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from .market import number


@dataclass(frozen=True)
class Config:
    short: int = 3
    long: int = 5
    stop_percent: Decimal = Decimal("1")
    reward_ratio: Decimal = Decimal("2")
    decimals: int = 2

    def validate(self):
        if type(self.short) is not int or type(self.long) is not int or not (1 <= self.short < self.long <= 10000):
            raise ValueError("SMA davrlari: 1 <= short < long <= 10000.")
        stop = number(self.stop_percent, "stop_percent")
        ratio = number(self.reward_ratio, "reward_ratio")
        if stop >= 100 or ratio > 100:
            raise ValueError("stop_percent 100 dan kichik, reward_ratio 100 dan katta bo'lmasin.")
        if type(self.decimals) is not int or not 0 <= self.decimals <= 8:
            raise ValueError("decimals 0–8 oralig'idagi butun son bo'lsin.")
        return stop, ratio


def signal(candles, config=Config(), symbol="DEMO-XAUUSD"):
    stop, ratio = config.validate()
    if len(candles) < config.long + 1:
        raise ValueError(f"Kamida {config.long + 1} ta sham kerak.")
    closes = [number(c.close, "close") for c in candles]
    average = lambda values, count: sum(values[-count:]) / Decimal(count)
    previous = closes[:-1]
    prev_short, prev_long = average(previous, config.short), average(previous, config.long)
    short, long = average(closes, config.short), average(closes, config.long)
    direction = "HOLD"
    if prev_short <= prev_long and short > long:
        direction = "BUY"
    elif prev_short >= prev_long and short < long:
        direction = "SELL"
    result = {
        "symbol": symbol, "direction": direction,
        "demo_only": True, "execution": "disabled",
        "timestamp_utc": candles[-1].timestamp.isoformat(),
        "reason": (f"SMA({config.short}) SMA({config.long})ni " +
                   ("yuqoriga kesib o'tdi." if direction == "BUY" else "pastga kesib o'tdi." if direction == "SELL" else "yangi kesishuv sodir bo'lmadi.")),
        "sma": {"short": str(short), "long": str(long)},
        "entry": None, "sl": None, "tp": None, "reward_ratio": None,
    }
    if direction == "HOLD":
        return result
    quantum = Decimal(1).scaleb(-config.decimals)
    rounded = lambda value: value.quantize(quantum, rounding=ROUND_HALF_UP)
    entry = rounded(closes[-1])
    sign = Decimal(1 if direction == "BUY" else -1)
    sl = rounded(entry * (1 - sign * stop / 100))
    distance = abs(entry - sl)
    tp = rounded(entry + sign * distance * ratio)
    if min(entry, sl, tp) <= 0 or distance == 0 or sign * (tp - entry) <= 0:
        raise ValueError("Yaxlitlash yoki parametrlar yaroqli SL/TP bermadi.")
    result.update(entry=str(entry), sl=str(sl), tp=str(tp), reward_ratio=str(abs(tp - entry) / distance))
    return result
