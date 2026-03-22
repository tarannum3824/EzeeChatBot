import json
import os
import logging

logger = logging.getLogger(__name__)

STATS_FILE = "storage/stats.json"


def _load_stats():
    if not os.path.exists(STATS_FILE):
        return {}
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        logger.warning("Corrupted stats.json — resetting.")
        return {}


def _save_stats(data):
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(STATS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def update_stats(bot_id, latency, answered):
    data = _load_stats()

    if bot_id not in data:
        data[bot_id] = {"messages": 0, "total_latency": 0, "unanswered": 0}

    data[bot_id]["messages"] += 1
    data[bot_id]["total_latency"] += latency

    if not answered:
        data[bot_id]["unanswered"] += 1

    _save_stats(data)


def get_stats(bot_id):
    data = _load_stats()
    bot = data.get(bot_id, {})

    total = bot.get("messages", 0)
    avg_latency = bot["total_latency"] / total if total else 0

    return {
        "total_messages": total,
        "avg_latency_ms": round(avg_latency, 2),
        "unanswered": bot.get("unanswered", 0),
    }
