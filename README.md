# 💧 Problem Statement 38 — Improved Source of Drinking Water

> **IBM SkillsBuild Internship Project**  
> Domain: Data Analytics | Tools: Python, Pandas, NumPy, Matplotlib, Seaborn

---

## 📌 Problem Statement

**PS-38: Improved Source of Drinking Water**

Access to safe and clean drinking water is a fundamental human right. Despite significant policy interventions under schemes like *Jal Jeevan Mission* and *NRDWP*, millions of Indians — especially in rural areas — still lack access to improved water sources. This project analyzes:

- Trends in improved drinking water access across Rural and Urban areas
- Regional and state-level disparities
- Relationship between clean cooking fuel access and water access
- Migration patterns and their correlation with infrastructure
- Impact of literacy and income on water access
- Progress from 2011 → 2016 → 2021

---

## 📁 Project Structure

```
Drinking_Water_Analysis/
│
├── data/
│   └── drinking_water_data.csv       # Main dataset (states, districts, years)
│
├── results/
│   └── key_findings.md               # Summary of findings and insights
│
├── analysis_notebook.ipynb           # Main Jupyter Notebook (EDA + Visualizations)
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation (this file)
```

---

## 📊 Dataset Description

The dataset (`data/drinking_water_data.csv`) contains district-level data for 20 major Indian states across 3 census/survey years: **2011, 2016, 2021**.

| Column | Description |
|---|---|
| `State` | Indian state name |
| `District` | District name |
| `Year` | Survey year (2011 / 2016 / 2021) |
| `Rural_Urban` | Settlement type (Rural / Urban) |
| `Population` | Population count |
| `Improved_Water_Access_%` | % population with improved water access |
| `Unimproved_Water_Access_%` | % population without improved water access |
| `Clean_Cooking_Fuel_%` | % households using clean cooking fuel (LPG/PNG) |
| `Solid_Fuel_%` | % households using solid/biomass fuel |
| `Migration_Rate_%` | Net migration rate (%) |
| `Literacy_Rate_%` | Literacy rate (%) |
| `Sanitation_Coverage_%` | % households with improved sanitation |
| `Avg_Income_INR` | Average household income (INR/year) |
| `Region` | Geographic region (North/South/East/West/Central/Northeast) |

---

## 🔍 Key Analysis Areas

1. **National Trend Analysis** — How has water access improved from 2011 to 2021?
2. **Rural vs Urban Disparity** — Quantifying the access gap
3. **Regional Comparison** — Which regions lead / lag?
4. **State-Level Ranking** — Best and worst performing states
5. **Correlation Analysis** — Water access vs literacy, income, sanitation
6. **Cooking Fuel & Water Access** — Are they co-dependent indicators?
7. **Migration Analysis** — Do higher migration rates correlate with better water access?

---

## 🚀 How to Run

### 1. Clone / Download the project
```bash
git clone <repo-url>
cd Drinking_Water_Analysis
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Jupyter Notebook
```bash
jupyter notebook analysis_notebook.ipynb
```

### 4. Run All Cells
- Click **Kernel → Restart & Run All**
- All charts and outputs will be generated inline

---

## 📈 Summary of Key Findings

| Insight | Value |
|---|---|
| National average water access improvement (2011–2021) | **+11.5 percentage points** |
| Urban vs Rural water access gap (2021) | **~16%** |
| Highest access state (Urban) | **Kerala / Goa / Delhi** |
| Lowest access state (Rural) | **Bihar / Jharkhand / Odisha** |
| Correlation: Water Access ↔ Literacy | **r ≈ +0.98** |
| Correlation: Water Access ↔ Income | **r ≈ +0.89** |
| States showing fastest improvement | **Bihar, Jharkhand, Odisha** |

*(Full findings in `results/key_findings.md`)*

---

## 🛠 Technologies Used

| Tool | Purpose |
|---|---|
| **Python 3.x** | Core programming language |
| **Pandas** | Data loading, cleaning, manipulation |
| **NumPy** | Numerical computations |
| **Matplotlib** | Base plotting |
| **Seaborn** | Statistical visualizations |
| **Jupyter Notebook** | Interactive analysis environment |

---

## 👤 Author

**IBM SkillsBuild Internship Submission**  
Problem Statement 38 — Improved Source of Drinking Water  
Domain: Data Analytics
