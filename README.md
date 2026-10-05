# AI Workload Observability & Analytics Platform

A local DevOps, infrastructure, and observability platform for monitoring AI-style workload execution, collecting operational metrics, tracing workload requests, analyzing latency, and troubleshooting containerized services.

The project was built locally on Ubuntu using Docker and demonstrates practical experience with **observability, monitoring, distributed tracing, Docker networking, service troubleshooting, Prometheus, Grafana, Langfuse, ClickHouse, and SQL/OLAP analytics**.

---

## Project Goal

The objective was to build a realistic local observability environment capable of answering operational questions such as:

- How many workloads are being executed?
- What types of workloads are running?
- How frequently are slow workloads occurring?
- How long do different workload types take?
- How can an individual workload execution be traced?
- How can workload events be analyzed using SQL?
- How can connectivity and infrastructure failures be diagnosed?
- How can metrics, traces, and analytical data be used together during troubleshooting?

The project was deliberately designed as a **DevOps/infrastructure observability project**, rather than an AI/ML model-development project.

---

## Architecture

```text
                         ┌──────────────────────┐
                         │  Python Workload      │
                         │     Generator         │
                         │                      │
                         │ Fast / Normal / Slow │
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │  Prometheus  │  │   Langfuse   │  │  ClickHouse  │
          │   Metrics    │  │    Traces    │  │ SQL / OLAP   │
          └──────┬───────┘  └──────────────┘  └──────────────┘
                 │
                 ▼
          ┌──────────────┐
          │   Grafana    │
          │  Monitoring  │
          └──────────────┘
```

The Python workload generator is the central workload source.

Prometheus collects operational metrics from the workload generator.

Grafana visualizes the Prometheus metrics.

Langfuse provides request-level tracing and workload latency investigation.

ClickHouse provides a local analytical SQL/OLAP layer for workload event analysis.

---

## Technology Stack

- Ubuntu 24.04.4 LTS
- Python 3.12.3
- Docker
- Docker Compose
- Prometheus
- Grafana
- Langfuse OSS
- ClickHouse
- SQL
- Bash
- Linux networking
- Docker networking
- Git/GitHub

---

## Environment

The project was developed locally using:

- Ubuntu 24.04.4 LTS
- Python 3.12.3
- Docker Desktop / WSL2
- 8 allocated Docker CPUs
- Approximately 4 GB Docker memory

The project was designed to run locally without AWS, cloud infrastructure, or paid services.

---

## Project Structure

```text
ai-workload-observability/
├── app/
│   └── workload.py
│
├── docker/
│
├── sql/
│
├── docs/
│   └── TROUBLESHOOTING-RCA.md
│
├── screenshots/
│
├── .venv/
│
└── README.md
```

---

## 1. Python Workload Generator

The project began with a Python workload generator that simulates different workload execution patterns.

The generator produces three workload categories:

| Workload Type | Approximate Duration |
| ------------- | -------------------- |
| Fast          | \~0.2 seconds        |
| Normal        | \~0.8 seconds        |
| Slow          | \~2.0 seconds        |

Each execution produces information including:

- workload status
- workload type
- execution duration
- diagnostic finding

Example output:

```text
{
    'status': 'completed',
    'workload_type': 'slow',
    'duration_ms': 2000,
    'finding': 'Elevated API latency detected'
}
```

The workload generator also exposes Prometheus-compatible metrics on:

```text
http://localhost:8000/metrics
```

---

## 2. Prometheus Metrics

Prometheus was introduced to collect operational metrics from the Python workload generator.

The workload exporter exposes metrics including:

- total workload executions
- workload counts by type
- slow workload count
- workload duration histogram
- workload duration sums
- workload duration counts

Examples include:

```text
ai_workload_total
```

```text
ai_workload_by_type_total
```

```text
ai_slow_workload_total
```

```text
ai_workload_duration_seconds
```

Prometheus was configured to scrape the workload generator using:

```text
host.docker.internal:8000
```

Prometheus itself was exposed locally through:

```text
http://localhost:9092
```

The Prometheus target was verified as healthy and successfully scraping the workload metrics.

---

## 3. Docker Networking Troubleshooting

One of the important infrastructure troubleshooting tasks involved connecting the Prometheus container to the Python workload running on the host/WSL environment.

The initial networking approach using the WSL gateway did not work reliably from inside the Prometheus container.

The target was changed to:

```text
host.docker.internal:8000
```

Docker host-gateway resolution was also configured using:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

After the change, the Prometheus workload target became:

```text
UP
```

and Prometheus successfully collected metrics from the Python workload generator.

This demonstrated practical troubleshooting of:

- Docker networking
- host/container communication
- service connectivity
- Prometheus target health
- endpoint verification

---

## 4. Grafana Monitoring

Grafana was configured as the visualization layer for Prometheus.

Grafana was exposed locally through:

```text
http://localhost:3001
```

The Prometheus datasource was configured using the Docker service address:

```text
http://prometheus:9090
```

The datasource connection was successfully tested.

### Completed Monitoring Panels

#### Total Workloads

A Grafana panel was created to monitor the total workload execution activity.

This demonstrated that the Python workload generator was producing measurable operational activity and that Prometheus was collecting it.

#### Slow Workload Rate

A second Grafana panel was created to monitor the rate of slow workloads.

The PromQL expression used was:

```text
rate(ai_slow_workload_total[$__rate_interval])
```

This provided a practical operational signal for identifying periods where slow workload executions were occurring.

The following Grafana evidence was captured:

```text
AI-Observability-Grafana-Total-Workloads.png
AI-Observability-Grafana-Slow-Workload-Rate.png
```

Latency visualization was investigated during development, but the average/P95/P99 Grafana queries did not return usable panel data in the final dashboard. Rather than artificially claiming those panels worked, latency analysis was supported through Langfuse traces and ClickHouse SQL analytics.

---

## 5. Langfuse Distributed Tracing

Langfuse OSS was integrated into the project to provide request-level tracing.

The project used Langfuse OSS 4.50.0 with the Python SDK.

The final instrumentation used the current SDK pattern:

```text
from langfuse import get_client, observe

langfuse = get_client()

@observe(name="ai-support-workload")
def run_support_workload():
    ...
    
langfuse.flush()
```

The workload generator was instrumented so that workload executions could be investigated through traces.

---

## 6. Langfuse Trace Verification

Multiple workload traces were successfully generated and verified.

The traces demonstrated:

- individual workload executions
- different workload types
- execution latency variation
- request-level observability
- slow versus faster workload behavior

Evidence was captured in:

```text
AI-Observability-Langfuse-Trace-Verified.png
AI-Observability-Langfuse-Multiple-Traces.png
AI-Observability-Langfuse-Latency-Variation.png
```

The observed workload behavior showed the intended latency pattern:

```text
Fast   → approximately 0.2 seconds
Normal → approximately 0.8 seconds
Slow   → approximately 2.0 seconds
```

This provided a second observability signal alongside Prometheus metrics.

Prometheus answered questions about **aggregate workload behavior**, while Langfuse provided **request-level tracing**.

---

## 7. ClickHouse Analytics

ClickHouse was included as the project's local analytical SQL/OLAP layer.

A dedicated ClickHouse container was initially planned for the project.

However, during development, the expected ClickHouse ports:

```text
8123
9000
```

were already being used by the running Langfuse ClickHouse service.

Instead of downloading and running another ClickHouse instance unnecessarily, the existing local ClickHouse service was reused.

A project-specific database and table were created:

```text
CREATE DATABASE IF NOT EXISTS observability;
```

The workload event table was:

```text
CREATE TABLE IF NOT EXISTS observability.workload_events
(
    event_time DateTime,
    workload_type String,
    duration_ms Float64,
    status String
)
ENGINE = MergeTree
ORDER BY event_time;
```

This provided a dedicated analytical dataset for the project without requiring another ClickHouse container.

---

## 8. ClickHouse Workload Analytics

Representative workload events based on the observed workload behavior were inserted into ClickHouse.

The dataset contained fast, normal, and slow workload examples.

Example records included:

```text
fast   → 200 ms
fast   → 220 ms

normal → 780 ms
normal → 820 ms
normal → 850 ms

slow   → 1950 ms
slow   → 2000 ms
slow   → 2100 ms
```

These records were used to demonstrate real ClickHouse SQL/OLAP analysis.

The data is intentionally a **small representative analytical sample**, not a claim of the entire live workload history.

---

## 9. ClickHouse Query: Workload Volume and Average Latency

The first analytical query calculated workload count and average latency by workload type:

```text
SELECT
    workload_type,
    count() AS workload_count,
    round(avg(duration_ms), 2) AS avg_latency_ms
FROM observability.workload_events
GROUP BY workload_type
ORDER BY avg_latency_ms;
```

Result:

| Workload Type | Workload Count | Average Latency |
| ------------- | -------------- | --------------- |
| fast          | 2              | 210 ms          |
| normal        | 3              | 816.67 ms       |
| slow          | 3              | 2016.67 ms      |

This demonstrated how ClickHouse can be used to perform analytical workload comparisons using SQL.

---

## 10. ClickHouse Query: Slow Workload Analysis

A second query was used to identify workloads exceeding a 1000 ms latency threshold:

```text
SELECT
    workload_type,
    count() AS slow_workloads,
    round(max(duration_ms), 2) AS max_latency_ms
FROM observability.workload_events
WHERE duration_ms >= 1000
GROUP BY workload_type
ORDER BY max_latency_ms DESC;
```

Result:

| Workload Type | Slow Workloads | Maximum Latency |
| ------------- | -------------- | --------------- |
| slow          | 3              | 2100 ms         |

This demonstrated a basic operational analytics use case:

**identify slow workloads → quantify them → determine maximum observed latency.**

---

## 11. Infrastructure Troubleshooting

Troubleshooting was an important part of the project rather than simply configuring services.

The project required investigation of:

- Docker-to-host networking
- Prometheus connectivity
- Prometheus target health
- host/container name resolution
- WSL/Docker environment availability
- container restarts
- ClickHouse port conflicts
- service endpoint verification

---

## 12. WSL/Docker Environment Interruption

During development, the WSL environment was restarted, which terminated active WSL processes and interrupted running workload/monitoring sessions.

The required services were subsequently restarted and development continued using separate Ubuntu terminal sessions.

This highlighted an important operational consideration when running local infrastructure through Docker Desktop and WSL2:

> Restarting the WSL environment terminates active development processes and running sessions.

---

## 13. ClickHouse Port Conflict RCA

The dedicated project ClickHouse container could not start because port `8123` was already allocated.

Investigation showed that the Langfuse ClickHouse container was already using:

```text
127.0.0.1:8123
127.0.0.1:9000
```

Instead of creating another ClickHouse instance, the existing service was reused.

The project then created:

```text
observability.workload_events
```

inside the existing ClickHouse server.

This resolved the port conflict while avoiding an unnecessary Docker image download and duplicate database service.

---

## 14. Prometheus Connectivity RCA

The initial Prometheus workload target could not be reached from inside the container.

The root cause was the networking boundary between the Docker container and the Python workload running on the host/WSL environment.

The target was changed from the WSL gateway approach to:

```text
host.docker.internal:8000
```

and Docker host-gateway resolution was configured.

The result was a healthy Prometheus target and successful workload metric collection.

---

## 15. Observability Evidence

The project contains screenshots documenting the major working components.

### Langfuse

```text
AI-Observability-Langfuse-Trace-Verified.png
AI-Observability-Langfuse-Multiple-Traces.png
AI-Observability-Langfuse-Latency-Variation.png
```

These demonstrate:

- verified traces
- multiple workload executions
- latency variation

### Prometheus

```text
AI-Observability-Prometheus-Target-UP.png
```

This demonstrates that the workload target was successfully being scraped.

### Grafana

```text
AI-Observability-Grafana-Total-Workloads.png
AI-Observability-Grafana-Slow-Workload-Rate.png
```

These demonstrate:

- workload monitoring
- slow-workload monitoring

---

## 16. Troubleshooting Documentation

A dedicated RCA document was created:

```text
docs/TROUBLESHOOTING-RCA.md
```

It documents:

1. Prometheus workload target connectivity
2. Docker/ClickHouse port conflict
3. WSL/Docker environment interruption
4. The general troubleshooting methodology used throughout the project

The troubleshooting approach was:

```text
Identify failure
      ↓
Inspect service/container state
      ↓
Check ports and endpoints
      ↓
Test connectivity independently
      ↓
Inspect Docker networking
      ↓
Apply the smallest required change
      ↓
Re-test
      ↓
Document the result
```

---

## 17. Engineering Practices Demonstrated

The project demonstrates several practical engineering practices.

### Infrastructure Troubleshooting

Diagnosed service connectivity and container networking issues rather than simply rebuilding the environment.

### Observability

Used multiple observability layers:

```text
Metrics → Prometheus
Visualization → Grafana
Tracing → Langfuse
Analytics → ClickHouse
```

### SQL / OLAP

Used ClickHouse SQL to aggregate workload events and investigate slow executions.

### Containerized Infrastructure

Used Docker-based services and Docker networking to create a reproducible local environment.

### Resource Awareness

Reused an existing ClickHouse service when a port conflict was discovered rather than downloading and running another database unnecessarily.

### Evidence-Based Validation

Working components were verified through:

- service endpoints
- Prometheus target health
- workload metrics
- Langfuse traces
- Grafana panels
- ClickHouse query results
- screenshots

---

## 18. Project Scope and Limitations

This is a **local observability laboratory**, not a production-scale monitoring platform.

The project does not claim:

- production Kubernetes deployment
- AWS infrastructure
- large-scale distributed workloads
- production-scale ClickHouse ingestion
- production SLO/SLA monitoring
- full Grafana P95/P99 latency dashboards

The ClickHouse dataset used for the final SQL demonstration is a small representative workload-event sample based on the observed workload behavior.

The strength of the project is its practical demonstration of:

**containerized infrastructure + metrics + tracing + analytics + troubleshooting.**

---

## 19. What This Project Demonstrates

The complete workflow is:

```text
Generate Workloads
       ↓
Expose Metrics
       ↓
Prometheus Collection
       ↓
Grafana Monitoring
       ↓
Langfuse Distributed Tracing
       ↓
Latency Investigation
       ↓
ClickHouse SQL / OLAP Analysis
       ↓
Troubleshooting & RCA
```

This demonstrates practical experience across the observability stack rather than familiarity with only one monitoring tool.

---

## 20. Portfolio Summary

The project demonstrates practical DevOps and infrastructure experience with:

- Linux
- Docker
- Docker networking
- Python
- Prometheus
- Grafana
- Langfuse
- ClickHouse
- SQL
- Metrics
- Distributed tracing
- Latency analysis
- Service troubleshooting
- Root-cause analysis
- Technical documentation

The project was completed entirely locally without AWS or paid infrastructure.

---

## Final Project Positioning

**AI Workload Observability & Analytics Platform**

Built a local observability platform for monitoring AI-style workload execution, collecting Prometheus metrics, visualizing workload behavior in Grafana, tracing individual executions with Langfuse, and analyzing workload events using ClickHouse SQL/OLAP. Troubleshot Docker networking, Prometheus connectivity, WSL/Docker interruptions, and container port conflicts, documenting the resulting root causes and resolutions.
