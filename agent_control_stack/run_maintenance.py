from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .store import FileSystemRunStore


DEFAULT_RUNS = Path("runs")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect or clean expired persisted runs.")
    parser.add_argument("--store-dir", type=Path, default=DEFAULT_RUNS)
    parser.add_argument("--delete", action="store_true", help="Delete expired runs instead of reporting only.")
    args = parser.parse_args()

    store = FileSystemRunStore(args.store_dir)
    report = {
        "store_dir": str(args.store_dir),
        "action": "delete" if args.delete else "dry_run",
        "expired_runs": [],
    }

    if args.delete:
        report["expired_runs"] = store.delete_expired_runs()
    else:
        now = datetime.now(timezone.utc)
        for summary in store.list_runs():
            expires_at = summary.get("expires_at")
            if not isinstance(expires_at, str):
                continue
            if _parse_datetime(expires_at) <= now:
                report["expired_runs"].append(
                    {
                        "run_id": summary.get("run_id"),
                        "expires_at": expires_at,
                    }
                )

    report["expired_count"] = len(report["expired_runs"])
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def _parse_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
