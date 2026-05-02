# 🏎 F1 Command Center

A hybrid AI dashboard combining **Cybersecurity**, **QA/Testing**, and **IT/DevOps** intelligence for Formula 1 race operations — powered by Claude AI.

![Python](https://img.shields.io/badge/python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.35+-red)
![Claude](https://img.shields.io/badge/claude-opus--4--5-orange)

---

## What it does

Each lap, the dashboard:
- **Cybersecurity panel** — scans telemetry for anomalies (DRS spoofing, GPS drift, replay attacks), scores CVE threats
- **QA panel** — runs the strategy model test suite, catches regressions in real time
- **DevOps panel** — monitors pit wall latency, CPU load, CI/CD pipeline health
- **AI engineer** — Claude synthesises all three disciplines and delivers a radio-style race advisory

---

## Quickstart

### 1. Clone and set up

```bash
git clone https://github.com/YOUR_USERNAME/f1_command_center.git
cd f1_command_center

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Add your API key

```bash
cp .env.example .env
# Open .env and set ANTHROPIC_API_KEY=sk-ant-...your-key...
```

Get your key at [console.anthropic.com](https://console.anthropic.com/).

### 3. Run

```bash
streamlit run app.py
```

Open http://localhost:8501, press **▶ Start race**.

---

## What you need to modify

### 🔑 Required — will not work without this

| File | What to change | Why |
|---|---|---|
| `.env` | Set `ANTHROPIC_API_KEY` | Claude API calls will fail otherwise |

---

### 🔧 Recommended — improves realism significantly

#### Real telemetry with FastF1

Replace `data/mock_telemetry.py` with actual F1 session data:

```bash
pip install fastf1
```

```python
# data/real_telemetry.py
import fastf1

session = fastf1.get_session(2024, 5, "R")
session.load()
car_data = session.laps.pick_driver("VER").get_car_data()
```

Set `FASTF1_CACHE_DIR=./fastf1_cache` in your `.env`.

#### Better voice quality

`voice/engineer.py` uses `pyttsx3` (offline, robotic). For real F1 radio quality:

**Option A — ElevenLabs** (best quality, paid):
```bash
pip install elevenlabs
```
```python
# In voice/engineer.py, replace the speak() method:
from elevenlabs import generate, play
def speak(self, text):
    audio = generate(text=text, voice="Daniel", model="eleven_monolingual_v1")
    play(audio)
```
Set `ELEVENLABS_API_KEY=...` in `.env`.

**Option B — Google Cloud TTS** (good quality, free tier available):
```bash
pip install google-cloud-texttospeech
```

#### Real CVE scanning

Replace the static `CVE_DB` in `engines/cyber_engine.py` with live NVD API calls:

```python
import httpx

def fetch_live_cves(keyword="f1 telemetry"):
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    r = httpx.get(url, params={"keywordSearch": keyword, "resultsPerPage": 5})
    return r.json()["vulnerabilities"]
```

#### Real CI/CD status

Replace `_cicd_status()` in `engines/devops_engine.py` with a GitHub Actions API call:

```python
import httpx, os

def _cicd_status(self):
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    repo  = os.getenv("GITHUB_REPO")
    url   = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
    r = httpx.get(url, headers={"Authorization": f"Bearer {token}"})
    runs = r.json()["workflow_runs"]
    return runs[0]["conclusion"] if runs else "unknown"
```

Set `GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO` in `.env`.

---

### 💡 Optional improvements

| Feature | Where | How |
|---|---|---|
| Add more QA tests | `engines/qa_engine.py` | Add functions to `TEST_REGISTRY` dict |
| Change race length | `app.py` | Set `total_laps` variable |
| Add new anomaly types | `engines/cyber_engine.py` | Add `if` blocks in `scan()` |
| Custom AI persona | `ai/brain.py` | Edit `SYSTEM_PROMPT` |
| Deploy to Streamlit Cloud | — | Push to GitHub, connect at share.streamlit.io |

---

## Project structure

```
f1_command_center/
├── app.py                        ← Streamlit entry point
├── engines/
│   ├── cyber_engine.py           ← CVE scanner + anomaly detection
│   ├── qa_engine.py              ← Strategy test suite + bug tracker
│   └── devops_engine.py          ← Infra health + CI/CD monitor
├── ai/
│   └── brain.py                  ← Claude cross-discipline reasoning
├── voice/
│   └── engineer.py               ← TTS radio voice system
├── data/
│   └── mock_telemetry.py         ← Simulated F1 telemetry feed
├── tests/
│   └── test_engines.py           ← Unit tests (pytest)
├── .github/workflows/ci.yml      ← GitHub Actions CI
├── .env.example                  ← Environment variable template
├── requirements.txt
└── README.md
```

---

## Running tests

```bash
pytest tests/ -v
```

---

## Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → select `app.py`
4. In **Secrets**, add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Deploy

---

## License

MIT
