# API Latency Runbook
Symptoms: increased response time, timeouts, reduced throughput.
Investigation: identify affected endpoints; check downstream/database latency; check CPU, memory, connection pools and worker saturation; review recent deployments.
Remediation: investigate slow queries, restore dependency performance, roll back confirmed regressions, scale capacity when saturation is confirmed, verify recovery.
