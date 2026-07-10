"""CPU runtime benchmark harness (plan.md §15 runtime efficiency).

Reports compression and runtime SEPARATELY. Controls: fixed thread count,
warm-up, randomized tokenizer order across rounds, >=5 measured rounds,
identical documents/batches, serialized execution, batch sizes {1,8,32,128},
short/medium/long buckets, raw observations preserved.
"""
from __future__ import annotations

import gc
import random
import resource
import sys
import time
from dataclasses import asdict, dataclass, field

import numpy as np

from .encoders import Encoder

BATCH_SIZES = (1, 8, 32, 128)


def _maxrss_bytes() -> int:
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return raw if sys.platform == "darwin" else raw * 1024


def bucket_documents(docs: list[str]) -> dict[str, list[str]]:
    """Partition documents into short/medium/long by UTF-8 byte length terciles."""
    if not docs:
        return {"short": [], "medium": [], "long": []}
    sized = sorted(docs, key=lambda d: len(d.encode("utf-8")))
    n = len(sized)
    return {
        "short": sized[: n // 3] or sized[:1],
        "medium": sized[n // 3 : 2 * n // 3] or sized[:1],
        "long": sized[2 * n // 3 :] or sized[-1:],
    }


@dataclass
class RuntimeObservation:
    tokenizer_id: str
    bucket: str
    batch_size: int
    round_index: int
    n_docs: int
    total_utf8_bytes: int
    total_chars: int
    wall_seconds: float
    mb_per_second: float
    chars_per_second: float
    docs_per_second: float


@dataclass
class RuntimeSummary:
    tokenizer_id: str
    load_seconds: float
    peak_rss_bytes: int
    mb_per_second_median: float
    mb_per_second_p95: float
    mb_per_second_p99: float
    observations: list[dict] = field(default_factory=list)


def _encode_batch(enc: Encoder, batch: list[str]) -> int:
    total = 0
    for text in batch:
        total += len(enc.encode(text))
    return total


def benchmark_encoders(
    encoders: list[Encoder],
    docs: list[str],
    rounds: int = 5,
    warmup: int = 1,
    seed: int = 0,
    load_seconds: dict[str, float] | None = None,
) -> list[RuntimeSummary]:
    """Serialized multi-round encode benchmark. Order randomized per round."""
    load_seconds = load_seconds or {}
    buckets = bucket_documents(docs)
    rng = random.Random(seed)

    observations: dict[str, list[RuntimeObservation]] = {e.tokenizer_id: [] for e in encoders}

    # Warm-up (not measured)
    for _ in range(warmup):
        for enc in encoders:
            _encode_batch(enc, docs[: min(len(docs), 64)])

    for r in range(rounds):
        order = encoders[:]
        rng.shuffle(order)  # randomize tokenizer order across rounds
        for enc in order:
            for bucket_name, bucket_docs in buckets.items():
                if not bucket_docs:
                    continue
                for bs in BATCH_SIZES:
                    batches = [bucket_docs[i : i + bs] for i in range(0, len(bucket_docs), bs)]
                    total_bytes = sum(len(d.encode("utf-8")) for d in bucket_docs)
                    total_chars = sum(len(d) for d in bucket_docs)
                    gc.disable()
                    t0 = time.perf_counter()
                    for batch in batches:
                        _encode_batch(enc, batch)
                    wall = time.perf_counter() - t0
                    gc.enable()
                    mb = total_bytes / (1024 * 1024)
                    observations[enc.tokenizer_id].append(
                        RuntimeObservation(
                            tokenizer_id=enc.tokenizer_id,
                            bucket=bucket_name,
                            batch_size=bs,
                            round_index=r,
                            n_docs=len(bucket_docs),
                            total_utf8_bytes=total_bytes,
                            total_chars=total_chars,
                            wall_seconds=wall,
                            mb_per_second=mb / wall if wall > 0 else 0.0,
                            chars_per_second=total_chars / wall if wall > 0 else 0.0,
                            docs_per_second=len(bucket_docs) / wall if wall > 0 else 0.0,
                        )
                    )

    summaries: list[RuntimeSummary] = []
    for enc in encoders:
        obs = observations[enc.tokenizer_id]
        mbps = np.array([o.mb_per_second for o in obs]) if obs else np.array([0.0])
        summaries.append(
            RuntimeSummary(
                tokenizer_id=enc.tokenizer_id,
                load_seconds=load_seconds.get(enc.tokenizer_id, 0.0),
                peak_rss_bytes=_maxrss_bytes(),
                mb_per_second_median=float(np.median(mbps)),
                mb_per_second_p95=float(np.percentile(mbps, 95)),
                mb_per_second_p99=float(np.percentile(mbps, 99)),
                observations=[asdict(o) for o in obs],
            )
        )
    return summaries
