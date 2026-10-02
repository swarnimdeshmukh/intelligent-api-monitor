# HTTP Error Runbook
Symptoms: HTTP 5xx responses and failed requests.
Investigation: identify endpoint/status code; review logs and deployments; check downstream services and database connectivity.
Remediation: restore failed dependencies, roll back confirmed faulty deployments, correct configuration/connectivity, verify error rate returns to baseline.
