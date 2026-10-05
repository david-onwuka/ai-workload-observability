import time
import random
from dotenv import load_dotenv
from langfuse import get_client, observe
from prometheus_client import Counter, Histogram, start_http_server

load_dotenv()

langfuse = get_client()

# Prometheus metrics
WORKLOAD_TOTAL = Counter(
    "ai_workload_total",
    "Total number of AI workloads executed",
)

WORKLOAD_BY_TYPE = Counter(
    "ai_workload_by_type_total",
    "AI workloads executed by workload type",
    ["workload_type"],
)

WORKLOAD_DURATION = Histogram(
    "ai_workload_duration_seconds",
    "AI workload execution duration in seconds",
    ["workload_type"],
)

SLOW_WORKLOAD_TOTAL = Counter(
    "ai_slow_workload_total",
    "Total number of slow AI workloads",
)


@observe(name="ai-support-workload")
def run_support_workload():
    start = time.perf_counter()

    workload_type = random.choice(["fast", "normal", "slow"])

    delays = {
        "fast": 0.2,
        "normal": 0.8,
        "slow": 2.0,
    }

    time.sleep(delays[workload_type])

    duration_seconds = time.perf_counter() - start
    duration_ms = round(duration_seconds * 1000)

    WORKLOAD_TOTAL.inc()
    WORKLOAD_BY_TYPE.labels(workload_type=workload_type).inc()
    WORKLOAD_DURATION.labels(workload_type=workload_type).observe(
        duration_seconds
    )

    if workload_type == "slow":
        SLOW_WORKLOAD_TOTAL.inc()

    return {
        "status": "completed",
        "workload_type": workload_type,
        "duration_ms": duration_ms,
        "finding": "Elevated API latency detected"
        if workload_type == "slow"
        else "API latency within expected range",
    }


if __name__ == "__main__":
    start_http_server(8000)

    while True:
        result = run_support_workload()
        langfuse.flush()

        print(result)

        time.sleep(2)
