import streamlit as st
import time
import threading

from engines.cyber_engine import CyberEngine
from engines.qa_engine import QAEngine
from engines.devops_engine import DevOpsEngine
from ai.brain import get_engineer_advice
from data.mock_telemetry import get_telemetry
from voice.engineer import VoiceEngineer

st.set_page_config(
    page_title="F1 Command Center",
    layout="wide",
    page_icon="🏎",
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.header("⚙ Settings")
accent = st.sidebar.selectbox("Voice accent", ["uk", "us", "india", "aussie"])
volume = st.sidebar.slider("Radio volume", 0.3, 1.0, 0.8, 0.05)
mute   = st.sidebar.toggle("🔇 Mute voice", False)

voice = VoiceEngineer(accent=accent, volume=volume)

if st.sidebar.button("📻 Radio check"):
    st.toast("Engineer radio check...", icon="🎙")
    voice.speak("Radio check. Command center is live.")

st.sidebar.markdown("---")
st.sidebar.caption("F1 Command Center · v1.0.0")

# ── Session state ─────────────────────────────────────────────────────────────
if "running" not in st.session_state:
    st.session_state["running"] = False
if "lap" not in st.session_state:
    st.session_state["lap"] = 1

# ── Engines ───────────────────────────────────────────────────────────────────
cyber_engine  = CyberEngine()
qa_engine     = QAEngine()
devops_engine = DevOpsEngine()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏎 F1 Command Center")
st.caption("Cybersecurity · QA · IT/DevOps — unified race intelligence")

col_start, col_stop, col_lap = st.columns([1, 1, 6])
with col_start:
    if st.button("▶ Start race", use_container_width=True):
        st.session_state["running"] = True
        st.session_state["lap"] = 1
with col_stop:
    if st.button("⏹ Stop", use_container_width=True):
        st.session_state["running"] = False

st.markdown("---")

# ── Main live loop ────────────────────────────────────────────────────────────
placeholder = st.empty()

if st.session_state["running"]:
    lap = st.session_state["lap"]
    total_laps = 57

    telemetry = get_telemetry(lap)
    c_data    = cyber_engine.scan(telemetry)
    q_data    = qa_engine.run_suite(telemetry)
    d_data    = devops_engine.check()

    with placeholder.container():
        st.subheader(f"Lap {lap} / {total_laps}")

        col1, col2, col3 = st.columns(3)

        # ── Cybersecurity panel ───────────────────────────────────────────────
        with col1:
            score = c_data["threat_score"]
            st.subheader("🔒 Cybersecurity")
            st.metric(
                "Threat Score",
                f"{score} / 100",
                delta="CRITICAL" if score > 70 else ("HIGH" if score > 40 else "OK"),
                delta_color="inverse",
            )
            st.progress(score / 100)

            if c_data["anomalies"]:
                for a in c_data["anomalies"]:
                    st.error(f"⚠ **{a['type']}** — {a['detail']}")
            else:
                st.success("No anomalies detected")

            st.markdown("**Active CVEs**")
            for cve in c_data["cves"]:
                sev = cve["severity"]
                color = "🔴" if sev == "HIGH" else ("🟡" if sev == "MEDIUM" else "🟢")
                st.caption(f"{color} `{cve['id']}` [{sev}] — {cve['desc']}")

            st.caption(f"Encryption: {'✅ AES-256 OK' if c_data['encryption_ok'] else '❌ FAILED'}")

        # ── QA panel ──────────────────────────────────────────────────────────
        with col2:
            st.subheader("🧪 QA / Testing")
            st.metric("Coverage", f"{q_data['coverage']}%")

            st.markdown("**Test suite results**")
            for test, res in q_data["results"].items():
                label = test.replace("_", " ").title()
                if res["status"] == "PASS":
                    st.success(f"✅ {label}")
                else:
                    st.error(f"❌ {label}")
                    st.caption(f"Bug #{res['bug']}: {res['detail']}")

            if q_data["failures"]:
                st.warning(f"⚠ {len(q_data['failures'])} test(s) failing — review before pit call")
            else:
                st.success("All tests passing")

        # ── DevOps panel ──────────────────────────────────────────────────────
        with col3:
            st.subheader("🖥 IT / DevOps")

            m1, m2 = st.columns(2)
            m1.metric("Telemetry latency",  f"{d_data['telemetry_latency_ms']}ms")
            m2.metric("Strategy API",        f"{d_data['strategy_api_latency_ms']}ms")
            m1.metric("Radio encoder",       f"{d_data['radio_encoder_latency_ms']}ms")
            m2.metric("Pit wall uptime",     f"{d_data['pit_wall_uptime_pct']}%")

            cpu = d_data["strategy_cpu_pct"]
            st.metric(
                "Strategy CPU",
                f"{cpu}%",
                delta="High — auto-scaled" if cpu > 75 else "Normal",
                delta_color="inverse" if cpu > 75 else "normal",
            )
            st.progress(cpu / 100)

            cicd = d_data["cicd_status"]
            if cicd == "passing":
                st.success("✅ CI/CD pipeline passing")
            else:
                st.error(f"❌ CI/CD: {cicd}")

        # ── AI Engineer advice ────────────────────────────────────────────────
        st.markdown("---")
        with st.spinner("Engineer computing advice..."):
            advice = get_engineer_advice(c_data, q_data, d_data, lap)

        st.info(f"📻 **Engineer (Lap {lap}):** {advice}")

        if not mute:
            threading.Thread(
                target=voice.speak, args=(advice,), daemon=True
            ).start()

    # Advance lap
    if lap < total_laps:
        st.session_state["lap"] = lap + 1
        time.sleep(4)
        st.rerun()
    else:
        st.session_state["running"] = False
        st.balloons()
        st.success("🏁 Race complete — chequered flag!")

else:
    st.info("Press **▶ Start race** to begin the live simulation.")
