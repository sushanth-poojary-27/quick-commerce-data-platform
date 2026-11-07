import os
import json
from datetime import datetime, timezone

STATE_FILE_PATH = os.path.join("data", "_state.json")


def get_last_watermark(table_name: str) -> str | None:
    """Reads data/_state.json and returns last_watermark for table_name, or None."""
    if not os.path.exists(STATE_FILE_PATH):
        return None

    try:
        with open(STATE_FILE_PATH, "r") as f:
            state = json.load(f)
            return state.get(table_name, {}).get("last_watermark")
    except (json.JSONDecodeError, OSError):
        return None


def update_watermark(table_name: str, watermark_col: str, new_watermark: str) -> None:
    """Updates data/_state.json with the new watermark and current UTC run timestamp."""
    state = {}
    if os.path.exists(STATE_FILE_PATH):
        try:
            with open(STATE_FILE_PATH, "r") as f:
                state = json.load(f)
        except (json.JSONDecodeError, OSError):
            state = {}

    state[table_name] = {
        "watermark_column": watermark_col,
        "last_watermark": new_watermark,
        "last_run_at": datetime.now(timezone.utc).isoformat(),
    }

    # Ensure parent directory exists before writing
    os.makedirs(os.path.dirname(STATE_FILE_PATH), exist_ok=True)
    with open(STATE_FILE_PATH, "w") as f:
        json.dump(state, f, indent=2)