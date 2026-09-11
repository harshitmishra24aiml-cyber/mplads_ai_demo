# MPLADS AI Risk Monitor — SIH PS 26102

A deployment-ready prototype for detecting anomalies, inefficiencies, and potential risk patterns in MPLADS project implementation. It combines rule-based checks with Isolation Forest and presents explainable risk scores through a browser dashboard.

> **Demo disclaimer:** The included dataset is synthetic and used only for demonstration. A risk alert is not proof of fraud; it requires human verification.

## Features

- CSV upload and schema validation
- Rule-based anomaly checks
- Isolation Forest anomaly detection
- Explainable risk score and reasons
- Summary cards and risk-level filtering
- Render deployment configuration

## Required CSV columns

```text
project_id,work_name,category,district,sanctioned_amount,expenditure,progress_percent,days_elapsed,planned_days,vendor_id,latitude,longitude
```

## Run locally

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000`.

## Deploy on Render

1. Push this folder to a GitHub repository.
2. In Render, select **New → Web Service**.
3. Connect the GitHub repository.
4. Use these settings:

- **Runtime:** Python
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Plan:** Free

The included `render.yaml` can also be used for Blueprint deployment.

## Jury demo flow

1. Open the live URL.
2. Click **Run Analysis**.
3. Show the total, high, medium, and low-risk cards.
4. Filter high-risk projects.
5. Open a flagged project and explain its reasons.
6. Explain that the system prioritizes projects for human verification.
