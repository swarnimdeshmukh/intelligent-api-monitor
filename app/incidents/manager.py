from datetime import datetime, timezone
from uuid import uuid4

from app.db import connection


def severity(m):
    if m.status_code is None or (m.status_code and m.status_code >= 500):
        return "CRITICAL"
    if m.latency_ms >= 3000:
        return "HIGH"
    if m.latency_ms >= 1000:
        return "MEDIUM"
    return "LOW"


def _reason_pattern(reason):
    """
    Normalize dynamic anomaly messages so repeated detections
    of the same problem reuse the existing incident.
    """
    if reason.startswith("HTTP "):
        return "HTTP %"
    if reason.startswith("Critical latency:"):
        return "Critical latency:%"
    if reason.startswith("High latency:"):
        return "High latency:%"
    if reason.startswith("Target unreachable"):
        return "Target unreachable%"
    if reason.startswith("Isolation Forest anomaly"):
        return "Isolation Forest anomaly%"
    return reason


def create(m, score, reason):
    sev = severity(m)
    pattern = _reason_pattern(reason)

    details = (
        f"Latency={m.latency_ms:.2f} ms | "
        f"HTTP={m.status_code} | "
        f"Error rate={m.error_rate:.2f} | "
        f"Throughput={m.throughput:.2f} req/s"
    )

    now = datetime.now(timezone.utc).isoformat()

    with connection() as db:
        # Check whether an equivalent incident is already OPEN.
        existing = db.execute(
            """
            SELECT incident_id
            FROM incidents
            WHERE target = ?
              AND status = 'OPEN'
              AND anomaly_reason LIKE ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (m.target, pattern),
        ).fetchone()

        if existing:
            iid = existing["incident_id"]

            # Refresh the existing incident with the latest observation.
            db.execute(
                """
                UPDATE incidents
                SET timestamp = ?,
                    severity = ?,
                    details = ?,
                    anomaly_score = ?
                WHERE incident_id = ?
                """,
                (now, sev, details, score, iid),
            )

            db.commit()
            return iid

        # No matching OPEN incident exists, so create a new one.
        iid = "INC-" + uuid4().hex[:8].upper()
        title = f"{sev}: anomaly detected on {m.target}"

        db.execute(
            """
            INSERT INTO incidents(
                incident_id,
                timestamp,
                target,
                severity,
                status,
                title,
                details,
                anomaly_score,
                anomaly_reason,
                analysis,
                evidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                iid,
                now,
                m.target,
                sev,
                "OPEN",
                title,
                details,
                score,
                reason,
                "",
                "",
            ),
        )

        db.commit()

    return iid


def recent(limit=50):
    with connection() as db:
        rows = db.execute(
            "SELECT * FROM incidents ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(x) for x in rows]


def update(iid, analysis, evidence):
    with connection() as db:
        db.execute(
            """
            UPDATE incidents
            SET analysis = ?, evidence = ?
            WHERE incident_id = ?
            """,
            (analysis, evidence, iid),
        )
        db.commit()
