from collections import defaultdict

import numpy as np
from sklearn.ensemble import IsolationForest


class HybridDetector:
    def __init__(self):
        self.history = defaultdict(list)
        self.models = {}

    def features(self, m):
        return [
            m.latency_ms,
            m.error_rate,
            m.throughput,
            float(m.status_code or 0),
        ]

    def detect(self, m):
        # Hard rules: always detect genuine service failures.
        if m.status_code is not None and m.status_code >= 500:
            return -1.0, True, f"HTTP {m.status_code} server error"

        if m.status_code is None:
            return -1.0, True, "Target unreachable or request timed out"

        if m.latency_ms >= 3000:
            return -0.8, True, f"Critical latency: {m.latency_ms:.0f} ms"

        if m.latency_ms >= 1000:
            return -0.5, True, f"High latency: {m.latency_ms:.0f} ms"

        # Build endpoint-specific baseline.
        history = self.history[m.target]
        history.append(self.features(m))

        if len(history) < 20:
            return 0.0, False, "Collecting baseline"

        # Keep only a bounded history.
        history[:] = history[-200:]

        model = self.models.setdefault(
            m.target,
            IsolationForest(
                n_estimators=200,
                contamination="auto",
                random_state=42,
            ),
        )

        x = np.asarray(history, dtype=float)
        model.fit(x)

        current = np.asarray([self.features(m)], dtype=float)

        score = float(model.decision_function(current)[0])
        prediction = int(model.predict(current)[0])

        # Isolation Forest is advisory here.
        # Require a meaningfully negative score instead of treating
        # every model outlier as an incident.
        abnormal = prediction == -1 and score < -0.15

        if abnormal:
            return score, True, "Isolation Forest anomaly"

        return score, False, "Normal"
