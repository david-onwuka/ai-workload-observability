# Troubleshooting & Root Cause Analysis

## 1. Prometheus Workload Target Connectivity

**Symptom:** Prometheus initially could not scrape the Python workload metrics endpoint.

**Root Cause:** The workload generator was running on the host/WSL environment while Prometheus was running inside Docker. The initial target used the WSL gateway address, which was not reachable from the Prometheus container.

**Resolution:** Updated the Prometheus target to `host.docker.internal:8000` and configured Docker host-gateway resolution with `extra_hosts`.

**Result:** The `ai-workload` Prometheus target became healthy (`UP`) and workload metrics were successfully collected.

---

## 2. Docker Port Conflict

**Symptom:** The dedicated project ClickHouse container could not start because port `8123` was already allocated.

**Root Cause:** The local Langfuse stack was already running a ClickHouse container using ports `8123` and `9000`.

**Resolution:** Identified the existing `langfuse-clickhouse-1` container and reused the running ClickHouse service for project analytics. Created the project-specific `observability.workload_events` table using a MergeTree engine.

**Result:** ClickHouse SQL analytics were completed successfully without starting another ClickHouse instance or downloading another image.

---

## 3. WSL/Docker Environment Interruption

**Symptom:** A WSL environment restart interrupted running workload and monitoring processes.

**Root Cause:** Restarting the WSL environment terminates active WSL processes and associated development sessions.

**Resolution:** Restarted the required services and continued development using separate Ubuntu terminal sessions instead of repeatedly restarting the WSL environment.

**Result:** The monitoring and workload services were restored and verified.

---

## 4. General Troubleshooting Approach

The project followed a practical infrastructure troubleshooting workflow:

1. Identify the failing service or connection.
2. Inspect container status, ports, and service endpoints.
3. Test connectivity independently with `curl` and service APIs.
4. Check Docker networking and host/container resolution.
5. Apply the smallest configuration change required.
6. Re-test the affected service.
7. Preserve working components instead of unnecessarily recreating or pulling additional infrastructure.

This resulted in verified workload metrics, Prometheus scraping, Langfuse traces, Grafana monitoring panels, and ClickHouse SQL analytics.
