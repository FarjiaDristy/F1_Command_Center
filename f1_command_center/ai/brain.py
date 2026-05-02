"""
AI Brain — uses Claude to reason across all three disciplines simultaneously.

Requires: ANTHROPIC_API_KEY in your environment (see README.md).
"""

from __future__ import annotations
import os
import anthropic

# Initialise the client once — it reads ANTHROPIC_API_KEY automatically
client = anthropic.Anthropic()

SYSTEM_PROMPT = """You are a senior F1 race engineer with deep expertise across three domains:
1. Cybersecurity — you monitor for threats, CVEs, and anomalous telemetry patterns.
2. Quality Assurance — you validate strategy models, track bugs, and flag regressions.
3. IT/DevOps — you maintain pit wall infrastructure, monitor latency, and manage CI/CD.

Your job is to synthesise signals from all three domains and deliver urgent, actionable,
radio-style race engineer messages. Think like a real F1 engineer: concise, precise, no fluff.
Cross-discipline correlations are your speciality — e.g. a QA failure + high CPU + active CVE
is a coordinated risk, not three separate issues."""


def get_engineer_advice(
    cyber: dict,
    qa: dict,
    devops: dict,
    lap: int,
) -> str:
    """
    Returns a single radio-style engineer message synthesising all three domains.
    Max ~2 sentences. Flags the highest cross-discipline risk first.
    """

    prompt = f"""
Race state — Lap {lap} / 57

── CYBERSECURITY ────────────────────────────────
Threat score: {cyber['threat_score']} / 100
Anomalies: {cyber['anomalies'] or 'none'}
Active CVEs: {[c['id'] + ' [' + c['severity'] + ']' for c in cyber['cves']]}
Encryption OK: {cyber['encryption_ok']}

── QA / TESTING ─────────────────────────────────
Tests passed: {qa['passed']} / {qa['total']}
Coverage: {qa['coverage']}%
Failures: {qa['failures'] or 'none'}
{chr(10).join(f"  Bug #{v['bug']}: {v['detail']}" for k, v in qa['results'].items() if v['status'] == 'FAIL')}

── IT / DEVOPS ───────────────────────────────────
Telemetry latency: {devops['telemetry_latency_ms']}ms
Strategy API latency: {devops['strategy_api_latency_ms']}ms
Strategy CPU: {devops['strategy_cpu_pct']}%
CI/CD: {devops['cicd_status']}
Infrastructure alerts: {devops.get('alerts') or 'none'}

Give me ONE radio-style engineer message (max 2 sentences, plain text only, no markdown).
Flag the most critical cross-discipline issue first. If everything is clean, confirm nominal status.
"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=150,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()
