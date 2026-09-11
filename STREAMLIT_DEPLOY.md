# Streamlit Dashboard — IBM Cloud Deployment Guide
# PS-38: Improved Source of Drinking Water
# IBM SkillsBuild Internship

## Option A — Streamlit Community Cloud (FREE, recommended)

Deploy in 3 clicks — no IBM Cloud resource needed.

1. Push this project to a **public GitHub repository**.
2. Go to **[share.streamlit.io](https://share.streamlit.io)** → "New app".
3. Set:
   - Repository: `your-username/Drinking_Water_Analysis`
   - Branch: `main`
   - Main file path: `app.py`
4. Click **Deploy** — live URL in ~60 seconds.

Free limits: unlimited public apps, 1 GB memory, no time limit.


## Option B — IBM Cloud Code Engine (FREE tier, existing resource)

IBM Cloud Code Engine has a **free tier**:
- 100,000 vCPU-seconds / month
- 200,000 GB-seconds memory / month
- No new paid service required — use the existing Code Engine project.

### Prerequisites
- IBM Cloud CLI installed: https://cloud.ibm.com/docs/cli
- Code Engine plugin: `ibmcloud plugin install code-engine`
- Docker installed locally (for `ibmcloud ce buildrun`)
- IBM Cloud Container Registry (free 0.5 GB included with IBM Cloud account)

### Step 1 — Log in
```bash
ibmcloud login --sso
ibmcloud target -g Default -r us-south
ibmcloud ce project select --name <your-existing-ce-project>
```

### Step 2 — Push image to Container Registry
```bash
ibmcloud cr login
ibmcloud cr namespace-add ps38-water

docker build -t us.icr.io/ps38-water/drinking-water-app:latest .
docker push  us.icr.io/ps38-water/drinking-water-app:latest
```

### Step 3 — Create the application
```bash
ibmcloud ce application create \
  --name ps38-drinking-water \
  --image us.icr.io/ps38-water/drinking-water-app:latest \
  --cpu 0.25 \
  --memory 1G \
  --port 8501 \
  --min-scale 0 \
  --max-scale 1
```

### Step 4 — Get the URL
```bash
ibmcloud ce application get --name ps38-drinking-water --output url
```
Opens at: `https://ps38-drinking-water.<region>.codeengine.appdomain.cloud`

### To update after code changes
```bash
docker build -t us.icr.io/ps38-water/drinking-water-app:latest .
docker push  us.icr.io/ps38-water/drinking-water-app:latest
ibmcloud ce application update --name ps38-drinking-water
```

### Free-tier limits (Code Engine)
| Metric              | Free monthly allowance |
|---------------------|------------------------|
| vCPU-seconds        | 100,000                |
| Memory GB-seconds   | 200,000                |
| HTTP requests       | First 100,000 free     |

This dashboard uses ~0.25 vCPU and 1 GB for as long as the container is active.
With `--min-scale 0`, the container sleeps when not in use, minimising consumption.


## Running Locally

```bash
# Install dependencies
pip install streamlit plotly pandas numpy

# Launch dashboard
streamlit run app.py
```

Opens at: http://localhost:8501


## Project Files Used by app.py

| File                          | Required? |
|-------------------------------|-----------|
| `data/drinking_water_data.csv`| ✅ Yes — raw data |
| `.streamlit/config.toml`      | ✅ Yes — theme/server config |
| `app.py`                      | ✅ Yes — dashboard entry point |
| `results/*.png`               | ❌ Not used (charts rebuilt interactively with Plotly) |
| `validate_analysis.py`        | ❌ Not used by dashboard |
| `analysis_notebook.ipynb`     | ❌ Not used by dashboard |
