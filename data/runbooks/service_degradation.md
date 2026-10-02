# Service Degradation Runbook
Symptoms: latency increases while throughput decreases or errors increase.
Investigation: determine whether degradation is isolated or systemic; compare current metrics with baseline; check infrastructure/dependencies; review deployments/configuration.
Remediation: mitigate bottlenecks, roll back confirmed regressions, restore capacity, continue monitoring until baseline returns.
