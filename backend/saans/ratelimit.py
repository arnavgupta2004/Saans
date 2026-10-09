"""Per-IP fixed-window rate limit for /api/ask.

AWS: a DynamoDB counter in saans-cache (key "rl#ask#<ip>#<window>", attribute `ttl` so DynamoDB deletes it).
Local/tests: an in-memory counter with the same interface.
"""
from __future__ import annotations

import os
import time
from typing import Any

ASK_LIMIT_PER_MIN = 10
WINDOW_S = 60


class MemoryRateLimiter:
    def __init__(self, limit: int = ASK_LIMIT_PER_MIN, window_s: int = WINDOW_S):
        self.limit, self.window_s, self.counts = limit, window_s, {}

    def hit(self, ip: str) -> int:
        key = (ip, int(time.time() // self.window_s))
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    def reset(self) -> None:
        self.counts.clear()


class DynamoRateLimiter:
    def __init__(self, table: Any = None, limit: int = ASK_LIMIT_PER_MIN, window_s: int = WINDOW_S):
        if table is None:
            import boto3
            table = boto3.resource("dynamodb").Table(os.getenv("CACHE_TABLE", "saans-cache"))
        self.table, self.limit, self.window_s = table, limit, window_s

    def hit(self, ip: str) -> int:
        window = int(time.time() // self.window_s)
        out = self.table.update_item(
            Key={"key": f"rl#ask#{ip}#{window}"},
            UpdateExpression="ADD n :one SET #ttl = :ttl",
            ExpressionAttributeNames={"#ttl": "ttl"},
            ExpressionAttributeValues={":one": 1, ":ttl": (window + 2) * self.window_s},
            ReturnValues="UPDATED_NEW",
        )
        return int(out["Attributes"]["n"])

    def reset(self) -> None:  # counters expire via DynamoDB TTL
        pass


def get_rate_limiter():
    return DynamoRateLimiter() if os.getenv("STORE", "json") == "dynamo" else MemoryRateLimiter()
