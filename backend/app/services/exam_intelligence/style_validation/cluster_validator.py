"""Cluster membership sanity checks."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

# Expected: at least one matching topic substring should land in cluster
EXPECTED_CLUSTER_MEMBERS: dict[str, list[str]] = {
    "reading_heavy": [
        "kpss_turkce__paragraf",
        "yds_ingilizce__reading",
        "yokdil_ingilizce",
        "ydt_ingilizce__reading",
    ],
    "reasoning_heavy": [
        "ales_matematik__problemler",
        "tyt_matematik__problemler",
        "dgs_matematik__problemler",
    ],
}


def validate_clusters(contracts: list[dict[str, Any]]) -> dict[str, Any]:
    by_cluster: dict[str, list[str]] = defaultdict(list)
    by_topic = {c.get("topic_code"): c for c in contracts if c.get("topic_code")}

    for c in contracts:
        cluster = c.get("cluster") or "unknown"
        by_cluster[str(cluster)].append(str(c.get("topic_code")))

    issues: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    for cluster, expected_topics in EXPECTED_CLUSTER_MEMBERS.items():
        members = by_cluster.get(cluster, [])
        for topic in expected_topics:
            # exact or prefix match (yokdil_ingilizce*)
            found = any(m == topic or m.startswith(topic) for m in members)
            # also accept if topic exists but in another cluster (report miscluster)
            actual = None
            for code, c in by_topic.items():
                if code == topic or str(code).startswith(topic):
                    actual = c.get("cluster")
                    if actual == cluster:
                        found = True
                        break
            row = {
                "cluster": cluster,
                "expected_topic": topic,
                "found_in_cluster": found,
                "actual_cluster": actual,
            }
            checks.append(row)
            if not found:
                issues.append(
                    {
                        **row,
                        "issue": "missing_or_misclustered",
                    }
                )

    # Flag reading topics wrongly in calculation_heavy etc.
    for code, c in by_topic.items():
        slug = str(c.get("topic_slug") or "")
        cluster = c.get("cluster")
        if slug in ("paragraf", "reading") and cluster not in (
            "reading_heavy",
            "mixed_general",
        ):
            issues.append(
                {
                    "topic_code": code,
                    "cluster": cluster,
                    "issue": "reading_topic_wrong_cluster",
                }
            )
        if slug == "problemler" and cluster in ("language_rules", "knowledge_recall"):
            issues.append(
                {
                    "topic_code": code,
                    "cluster": cluster,
                    "issue": "problem_topic_wrong_cluster",
                }
            )

    return {
        "cluster_sizes": {k: len(v) for k, v in sorted(by_cluster.items())},
        "checks": checks,
        "issues": issues,
        "passed": len(issues) == 0,
    }
