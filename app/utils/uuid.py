import os
import time
import uuid
from collections.abc import Callable
from uuid import UUID

UUID7_FUNCTION: Callable[[], UUID] | None = getattr(uuid, "uuid7", None)


def generate_uuid7() -> UUID:
    if UUID7_FUNCTION is not None:
        return UUID7_FUNCTION()

    timestamp_ms = time.time_ns() // 1_000_000
    random_bits = int.from_bytes(os.urandom(10), byteorder="big") & ((1 << 74) - 1)
    rand_a = random_bits >> 62
    rand_b = random_bits & ((1 << 62) - 1)
    return UUID(
        int=(timestamp_ms << 80) | (0x7 << 76) | (rand_a << 64) | (0b10 << 62) | rand_b
    )
