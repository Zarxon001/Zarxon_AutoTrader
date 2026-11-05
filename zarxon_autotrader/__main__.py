import argparse
import json
from pathlib import Path
from .market import load_csv, number
from .strategy import Config, signal


def main():
    parser = argparse.ArgumentParser(description="Zarxon: mahalliy CSV, demo signal, real ijro o'chirilgan.")
    parser.add_argument("--csv", type=Path, default=Path(__file__).resolve().parent.parent / "data" / "demo.csv")
    parser.add_argument("--symbol", default="DEMO-XAUUSD")
    parser.add_argument("--short", type=int, default=3)
    parser.add_argument("--long", type=int, default=5)
    parser.add_argument("--stop-percent", default="1")
    parser.add_argument("--reward-ratio", default="2")
    parser.add_argument("--decimals", type=int, default=2)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        config = Config(args.short, args.long, number(args.stop_percent, "stop_percent"),
                        number(args.reward_ratio, "reward_ratio"), args.decimals)
        result = signal(load_csv(args.csv), config, args.symbol)
    except (ValueError, OSError, ArithmeticError) as error:
        parser.exit(2, f"Xato: {error}\n")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("ZARXON — FAQAT DEMO | REAL IJRO O'CHIRILGAN")
        print(f"{result['symbol']}: {result['direction']} | {result['reason']}")
        print(f"Entry: {result['entry']} | SL: {result['sl']} | TP: {result['tp']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
