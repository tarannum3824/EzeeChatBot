import json
import os

STATS_FILE = "storage/stats.json"

def update_stats(bot_id, latency, answered):
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump({}, f)

    with open(STATS_FILE, "r") as f:
        data = json.load(f)

    if bot_id not in data:
        data[bot_id] = {
            "messages": 0,
            "total_latency": 0,
            "unanswered": 0
        }

    data[bot_id]["messages"] += 1
    data[bot_id]["total_latency"] += latency

    if not answered:
        data[bot_id]["unanswered"] += 1

    with open(STATS_FILE, "w") as f:
        json.dump(data, f)

def get_stats(bot_id):
    with open(STATS_FILE, "r") as f:
        data = json.load(f)

    bot = data.get(bot_id, {})

    avg_latency = (
        bot["total_latency"] / bot["messages"]
        if bot.get("messages") else 0
    )

    return {
        "total_messages": bot.get("messages", 0),
        "avg_latency_ms": avg_latency,
        "unanswered": bot.get("unanswered", 0)
    }