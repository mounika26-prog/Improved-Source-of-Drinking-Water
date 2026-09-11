"""
app.py — Streamlit Dashboard
PS-38: Improved Source of Drinking Water
IBM SkillsBuild Internship | Data Analytics

Run locally:
    streamlit run app.py

Deploy to IBM Cloud Code Engine (free tier):
    See DEPLOYMENT.md for full instructions.
"""

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Drinking Water Analysis — PS-38",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colour palette (matches existing charts) ─────────────────────────────────
C_RURAL  = "#e67e22"
C_URBAN  = "#2980b9"
C_GREEN  = "#27ae60"
C_RED    = "#e74c3c"
C_PURPLE = "#8e44ad"
C_TEAL   = "#16a085"
C_GOLD   = "#f39c12"

REGION_COLORS = {
    "South":     "#27ae60",
    "West":      "#2980b9",
    "North":     "#8e44ad",
    "East":      "#e74c3c",
    "Central":   "#f39c12",
    "Northeast": "#16a085",
}

# ── Data loading (cached) ─────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and pre-process the raw CSV once; cache for the session."""
    path = os.path.join(os.path.dirname(__file__), "data", "drinking_water_data.csv")
    df = pd.read_csv(path)
    df.rename(columns={
        "Improved_Water_Access_%":   "water_access",
        "Unimproved_Water_Access_%": "unimproved_water",
        "Clean_Cooking_Fuel_%":      "clean_fuel",
        "Solid_Fuel_%":              "solid_fuel",
        "Migration_Rate_%":          "migration_rate",
        "Literacy_Rate_%":           "literacy_rate",
        "Sanitation_Coverage_%":     "sanitation",
        "Avg_Income_INR":            "avg_income",
    }, inplace=True)
    df["Year"] = df["Year"].astype(int)
    return df

df_raw = load_data()

# ── Sidebar — global filters ──────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/51/IBM_logo.svg", width=80)
    st.markdown("## 💧 PS-38 Dashboard")
    st.markdown("**IBM SkillsBuild Internship**  \nData Analytics · 2011–2021")
    st.divider()

    st.markdown("### 🔽 Global Filters")

    all_regions  = sorted(df_raw["Region"].unique())
    sel_regions  = st.multiselect("Region", all_regions, default=all_regions, key="f_region")

    all_states   = sorted(df_raw[df_raw["Region"].isin(sel_regions)]["State"].unique())
    sel_states   = st.multiselect("State", all_states, default=all_states, key="f_state")

    sel_years    = st.multiselect("Year", [2011, 2016, 2021], default=[2011, 2016, 2021], key="f_year")

    sel_ru       = st.multiselect(
        "Settlement Type", ["Rural", "Urban"], default=["Rural", "Urban"], key="f_ru"
    )

    st.divider()
    st.markdown(
        "**Coverage:** 20 states · 28 districts  \n"
        "**Source:** drinking_water_data.csv  \n"
        "**Charts:** Plotly (interactive)"
    )

# Apply global filters
df = df_raw[
    df_raw["Region"].isin(sel_regions) &
    df_raw["State"].isin(sel_states) &
    df_raw["Year"].isin(sel_years) &
    df_raw["Rural_Urban"].isin(sel_ru)
].copy()

if df.empty:
    st.warning("No data matches the current filters. Please broaden your selection.")
    st.stop()

# ── Navigation tabs ───────────────────────────────────────────────────────────
tabs = st.tabs([
    "🏠 Overview",
    "📈 National Trend",
    "🏙️ Rural vs Urban",
    "🗺️ State Comparison",
    "🌐 Regional Trends",
    "🏆 Top & Bottom States",
    "🔗 Correlation",
    "💰 Socioeconomic",
    "📊 Improvement",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 0 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("## 💧 PS-38: Improved Source of Drinking Water")
    st.markdown(
        "IBM SkillsBuild Internship · Data Analytics · "
        "**20 Indian States · 28 Districts · 2011 – 2016 – 2021**"
    )
    st.divider()

    # KPI row — always from full dataset (not filtered) for accurate national stats
    df_full = df_raw.copy()
    nat11 = df_full[df_full["Year"] == 2011]["water_access"].mean()
    nat21 = df_full[df_full["Year"] == 2021]["water_access"].mean()
    r21   = df_full[(df_full["Year"]==2021)&(df_full["Rural_Urban"]=="Rural")]["water_access"].mean()
    u21   = df_full[(df_full["Year"]==2021)&(df_full["Rural_Urban"]=="Urban")]["water_access"].mean()
    gap   = u21 - r21

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("National Access 2011", f"{nat11:.1f}%")
    k2.metric("National Access 2021", f"{nat21:.1f}%", delta=f"+{nat21-nat11:.1f} pp")
    k3.metric("Rural Access 2021",    f"{r21:.1f}%")
    k4.metric("Urban Access 2021",    f"{u21:.1f}%")
    k5.metric("Rural–Urban Gap 2021", f"{gap:.1f} pp")

    st.divider()

    # Mini national trend
    trend = df_full.groupby(["Year","Rural_Urban"])["water_access"].mean().reset_index()
    fig_ov = px.line(
        trend, x="Year", y="water_access", color="Rural_Urban",
        markers=True, title="National Average Improved Water Access (2011–2021)",
        color_discrete_map={"Rural": C_RURAL, "Urban": C_URBAN},
        labels={"water_access": "Water Access (%)", "Rural_Urban": "Settlement"},
    )
    fig_ov.update_traces(line_width=3, marker_size=10)
    fig_ov.update_layout(yaxis_ticksuffix="%", xaxis=dict(tickvals=[2011,2016,2021]))
    st.plotly_chart(fig_ov, use_container_width=True)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🔑 Key Findings")
        st.markdown(
            "- National avg access: **76.6% (2011) → 88.1% (2021)**  (+11.5 pp)\n"
            "- Urban access consistently **~95–98%** across all years\n"
            "- Rural access: **~58% (2011) → ~82% (2021)** — below 90% target\n"
            "- Fastest improving states: **Chhattisgarh (+23.6 pp), Odisha (+23.4 pp)**\n"
            "- Lowest rural access: **Jharkhand 61.2%, Bihar 61.1%** (2021)\n"
            "- Strongest correlation: Sanitation r=0.97, Clean Fuel r=0.95"
        )
    with c2:
        st.markdown("### 📁 Project Files")
        st.markdown(
            "| File | Description |\n"
            "|---|---|\n"
            "| `data/drinking_water_data.csv` | Raw dataset |\n"
            "| `analysis_notebook.ipynb` | Main EDA notebook |\n"
            "| `validate_analysis.py` | Analysis + chart generator |\n"
            "| `results/key_findings.md` | Findings summary |\n"
            "| `results/state_summary.csv` | State aggregates |\n"
            "| `results/improvement_table.csv` | Improvement ranking |\n"
            "| `app.py` | This dashboard |"
        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — NATIONAL TREND
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("## 📈 National Water Access Trend")
    st.caption("Average improved water access across all states, by year and settlement type.")

    trend_df = df.groupby(["Year", "Rural_Urban"])["water_access"].mean().reset_index()

    fig_t = px.line(
        trend_df, x="Year", y="water_access", color="Rural_Urban",
        markers=True,
        color_discrete_map={"Rural": C_RURAL, "Urban": C_URBAN},
        labels={"water_access": "Improved Water Access (%)", "Rural_Urban": "Settlement"},
        title="National Average — Improved Drinking Water Access",
    )
    fig_t.update_traces(line_width=3, marker_size=12)
    fig_t.add_hline(y=90, line_dash="dash", line_color="green",
                    annotation_text="90% national target", annotation_position="bottom right")
    fig_t.update_layout(
        yaxis=dict(range=[40, 105], ticksuffix="%"),
        xaxis=dict(tickvals=[2011, 2016, 2021]),
        legend_title="Settlement Type",
    )

    # Annotate data points
    for _, row in trend_df.iterrows():
        fig_t.add_annotation(
            x=row["Year"], y=row["water_access"],
            text=f"{row['water_access']:.1f}%",
            showarrow=False, yshift=16,
            font=dict(size=11, color=C_RURAL if row["Rural_Urban"]=="Rural" else C_URBAN),
        )

    st.plotly_chart(fig_t, use_container_width=True)

    # Year-on-year delta table
    st.markdown("#### Year-on-Year Change (pp)")
    pivot_t = trend_df.pivot(index="Year", columns="Rural_Urban", values="water_access").round(1)
    pivot_t.columns.name = None
    pivot_t.index.name = "Year"
    if "Rural" in pivot_t.columns and "Urban" in pivot_t.columns:
        pivot_t["Rural Δ (pp)"] = pivot_t["Rural"].diff().round(1)
        pivot_t["Urban Δ (pp)"] = pivot_t["Urban"].diff().round(1)
    st.dataframe(
        pivot_t.style.format("{:.1f}").highlight_max(axis=0, color="#d4edda"),
        use_container_width=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — RURAL vs URBAN
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("## 🏙️ Rural vs Urban Distribution")

    col_yr = st.selectbox("Select Year for Distribution View", [2011, 2016, 2021],
                          index=2, key="ru_year")

    c1, c2 = st.columns(2)

    # Box plot — all years
    with c1:
        fig_box = px.box(
            df, x="Year", y="water_access", color="Rural_Urban",
            color_discrete_map={"Rural": C_RURAL, "Urban": C_URBAN},
            title="Distribution by Year & Settlement (Boxplot)",
            labels={"water_access": "Water Access (%)", "Rural_Urban": "Settlement"},
            points="outliers",
        )
        fig_box.update_layout(yaxis_ticksuffix="%", xaxis=dict(type="category"))
        st.plotly_chart(fig_box, use_container_width=True)

    # Violin — selected year
    with c2:
        df_yr = df[df["Year"] == col_yr]
        fig_vio = px.violin(
            df_yr, x="Rural_Urban", y="water_access", color="Rural_Urban",
            box=True, points="all",
            color_discrete_map={"Rural": C_RURAL, "Urban": C_URBAN},
            title=f"Distribution in {col_yr} — Rural vs Urban",
            labels={"water_access": "Water Access (%)", "Rural_Urban": "Settlement"},
        )
        fig_vio.update_layout(yaxis_ticksuffix="%")
        st.plotly_chart(fig_vio, use_container_width=True)

    # Summary stats
    st.markdown("#### Summary Statistics by Settlement Type")
    stats = (
        df.groupby("Rural_Urban")["water_access"]
        .describe()[["mean","std","min","25%","50%","75%","max"]]
        .round(1)
    )
    stats.columns = ["Mean %", "Std Dev", "Min %", "25th %", "Median %", "75th %", "Max %"]
    st.dataframe(stats.style.format("{:.1f}"), use_container_width=True)

    # Gap analysis
    st.markdown("#### Rural–Urban Gap by Year")
    gap_df = (
        df.groupby(["Year","Rural_Urban"])["water_access"]
        .mean().unstack("Rural_Urban").round(1)
    )
    gap_df.columns.name = None
    if "Rural" in gap_df.columns and "Urban" in gap_df.columns:
        gap_df["Gap (Urban − Rural)"] = (gap_df["Urban"] - gap_df["Rural"]).round(1)
    fig_gap = px.bar(
        gap_df.reset_index(), x="Year", y="Gap (Urban − Rural)",
        title="Urban–Rural Water Access Gap (percentage points)",
        color_discrete_sequence=[C_PURPLE],
        text="Gap (Urban − Rural)",
    )
    fig_gap.update_traces(texttemplate="%{text:.1f} pp", textposition="outside")
    fig_gap.update_layout(yaxis_title="Gap (pp)", xaxis=dict(type="category"))
    st.plotly_chart(fig_gap, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — STATE COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("## 🗺️ State-Wise Comparison")

    yr_sc = st.selectbox("Year", [2011, 2016, 2021], index=2, key="sc_year")
    sc_df = (
        df[df["Year"] == yr_sc]
        .groupby(["State","Rural_Urban"])["water_access"]
        .mean().reset_index()
    )
    sc_wide = sc_df.pivot(index="State", columns="Rural_Urban", values="water_access").reset_index()
    sc_wide.columns.name = None

    # Sort by rural if available else urban
    sort_col = "Rural" if "Rural" in sc_wide.columns else sc_wide.columns[1]
    sc_wide = sc_wide.sort_values(sort_col, ascending=True)

    fig_sc = go.Figure()
    if "Rural" in sc_wide.columns:
        fig_sc.add_trace(go.Bar(
            y=sc_wide["State"], x=sc_wide["Rural"],
            name="Rural", orientation="h", marker_color=C_RURAL, opacity=0.85,
        ))
    if "Urban" in sc_wide.columns:
        fig_sc.add_trace(go.Bar(
            y=sc_wide["State"], x=sc_wide["Urban"],
            name="Urban", orientation="h", marker_color=C_URBAN, opacity=0.85,
        ))
    fig_sc.add_vline(x=90, line_dash="dash", line_color="green",
                     annotation_text="90% target")
    fig_sc.update_layout(
        title=f"State-Wise Water Access — {yr_sc}",
        barmode="group",
        xaxis=dict(title="Improved Water Access (%)", ticksuffix="%", range=[30, 105]),
        yaxis_title="State",
        height=600,
        legend_title="Settlement",
    )
    st.plotly_chart(fig_sc, use_container_width=True)

    # Raw data table
    with st.expander("📋 Show data table"):
        st.dataframe(sc_wide.set_index("State").round(1), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — REGIONAL TRENDS
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("## 🌐 Regional Trends")

    reg_df = df.groupby(["Region","Year"])["water_access"].mean().reset_index()

    fig_reg = px.line(
        reg_df, x="Year", y="water_access", color="Region",
        markers=True,
        color_discrete_map=REGION_COLORS,
        title="Regional Average — Improved Water Access (2011–2021)",
        labels={"water_access": "Water Access (%)", "Region": "Region"},
    )
    fig_reg.update_traces(line_width=2.5, marker_size=10)
    fig_reg.add_hline(y=90, line_dash="dot", line_color="gray",
                      annotation_text="90% target")
    fig_reg.update_layout(
        yaxis=dict(range=[40, 105], ticksuffix="%"),
        xaxis=dict(tickvals=[2011, 2016, 2021]),
        legend_title="Region",
    )
    for _, row in reg_df.iterrows():
        fig_reg.add_annotation(
            x=row["Year"], y=row["water_access"],
            text=f"{row['water_access']:.1f}",
            showarrow=False, yshift=12, font=dict(size=9),
        )
    st.plotly_chart(fig_reg, use_container_width=True)

    # Regional 2021 snapshot
    st.markdown("#### Regional Snapshot — 2021")
    reg21 = (
        df_raw[df_raw["Year"]==2021]
        .groupby(["Region","Rural_Urban"])["water_access"]
        .mean().reset_index()
    )
    fig_regbar = px.bar(
        reg21, x="Region", y="water_access", color="Rural_Urban",
        barmode="group",
        color_discrete_map={"Rural": C_RURAL, "Urban": C_URBAN},
        text_auto=".1f",
        title="Average Water Access by Region and Settlement Type (2021)",
        labels={"water_access": "Water Access (%)", "Rural_Urban": "Settlement"},
    )
    fig_regbar.update_layout(yaxis_ticksuffix="%", uniformtext_minsize=9)
    st.plotly_chart(fig_regbar, use_container_width=True)

    with st.expander("📋 Regional data table"):
        rpivot = reg_df.pivot(index="Region", columns="Year", values="water_access").round(1)
        rpivot.columns.name = None
        st.dataframe(rpivot, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — TOP & BOTTOM STATES
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("## 🏆 Top & Bottom States")

    tb_yr   = st.selectbox("Year", [2011, 2016, 2021], index=2, key="tb_year")
    tb_n    = st.slider("Number of states (top & bottom each)", 3, 10, 5, key="tb_n")
    tb_type = st.radio("Settlement type", ["Rural", "Urban", "Both (avg)"], horizontal=True, key="tb_type")

    if tb_type == "Both (avg)":
        rural_ranked = (
            df_raw[(df_raw["Year"]==tb_yr)]
            .groupby("State")["water_access"].mean()
            .sort_values(ascending=False)
        )
    else:
        rural_ranked = (
            df_raw[(df_raw["Year"]==tb_yr) & (df_raw["Rural_Urban"]==tb_type)]
            .groupby("State")["water_access"].mean()
            .sort_values(ascending=False)
        )

    top_n   = rural_ranked.head(tb_n)
    bot_n   = rural_ranked.tail(tb_n)
    combined = pd.concat([
        top_n.reset_index().assign(Group="Top"),
        bot_n.reset_index().assign(Group="Bottom"),
    ])
    combined.columns = ["State","water_access","Group"]

    fig_tb = px.bar(
        combined.sort_values("water_access"),
        y="State", x="water_access",
        color="Group",
        orientation="h",
        color_discrete_map={"Top": C_GREEN, "Bottom": C_RED},
        text="water_access",
        title=f"Top {tb_n} vs Bottom {tb_n} States — {tb_type} Water Access ({tb_yr})",
        labels={"water_access": "Water Access (%)", "State": "State"},
    )
    fig_tb.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_tb.add_vline(x=80, line_dash="dash", line_color="gray",
                     annotation_text="80% benchmark")
    fig_tb.update_layout(
        xaxis=dict(range=[30, 105], ticksuffix="%"),
        height=max(400, tb_n * 60),
        legend_title="Rank Group",
    )
    st.plotly_chart(fig_tb, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"#### 🥇 Top {tb_n}")
        st.dataframe(
            top_n.reset_index().rename(columns={"water_access": "Water Access (%)"})
            .assign(**{"Water Access (%)": lambda x: x["Water Access (%)"].round(1)})
            .set_index("State"),
            use_container_width=True,
        )
    with c2:
        st.markdown(f"#### 🔴 Bottom {tb_n}")
        st.dataframe(
            bot_n.reset_index().rename(columns={"water_access": "Water Access (%)"})
            .assign(**{"Water Access (%)": lambda x: x["Water Access (%)"].round(1)})
            .set_index("State"),
            use_container_width=True,
        )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — CORRELATION
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("## 🔗 Correlation Analysis")
    st.caption(
        "Pearson correlation between improved water access and socio-economic indicators. "
        "Values range from −1 (perfect negative) to +1 (perfect positive)."
    )

    num_cols = ["water_access","clean_fuel","migration_rate","literacy_rate","sanitation","avg_income"]
    labels   = {
        "water_access":   "Water Access",
        "clean_fuel":     "Clean Fuel",
        "migration_rate": "Migration Rate",
        "literacy_rate":  "Literacy Rate",
        "sanitation":     "Sanitation",
        "avg_income":     "Avg Income",
    }
    corr_df  = df[num_cols].rename(columns=labels).corr().round(2)

    # Lower-triangle mask
    mask = np.triu(np.ones(corr_df.shape, dtype=bool), k=1)
    corr_masked = corr_df.copy().astype(float)
    corr_masked[mask] = np.nan

    fig_hm = go.Figure(go.Heatmap(
        z=corr_masked.values,
        x=corr_masked.columns.tolist(),
        y=corr_masked.index.tolist(),
        colorscale="RdYlGn",
        zmin=-1, zmax=1,
        text=corr_masked.round(2).values,
        texttemplate="%{text}",
        colorbar=dict(title="r"),
        hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>r = %{z:.2f}<extra></extra>",
    ))
    fig_hm.update_layout(
        title="Correlation Heatmap — Drinking Water & Socio-Economic Indicators",
        height=460,
        xaxis=dict(side="bottom"),
    )
    st.plotly_chart(fig_hm, use_container_width=True)

    # Correlation bar for water_access only
    corr_water = (
        df[num_cols].corr()["water_access"]
        .drop("water_access")
        .rename(index=lambda c: labels.get(c, c))
        .reset_index()
    )
    corr_water.columns = ["Indicator", "Pearson r"]
    corr_water = corr_water.sort_values("Pearson r", ascending=True)
    corr_water["Color"] = corr_water["Pearson r"].apply(
        lambda v: C_GREEN if v >= 0.7 else (C_GOLD if v >= 0.3 else C_RED)
    )

    fig_cbar = go.Figure(go.Bar(
        y=corr_water["Indicator"],
        x=corr_water["Pearson r"],
        orientation="h",
        marker_color=corr_water["Color"],
        text=corr_water["Pearson r"].round(2),
        textposition="outside",
    ))
    fig_cbar.add_vline(x=0, line_color="black", line_width=1)
    fig_cbar.update_layout(
        title="Correlation with Water Access (Pearson r)",
        xaxis=dict(title="Pearson r", range=[-0.1, 1.1]),
        yaxis_title="Indicator",
        height=350,
    )
    st.plotly_chart(fig_cbar, use_container_width=True)

    st.markdown(
        "**Interpretation:**  \n"
        "- Sanitation (r≈0.97) and Clean Fuel (r≈0.95) are the **strongest co-indicators** — "
        "all three reflect the same underlying development gap.  \n"
        "- Literacy (r≈0.86) and Income (r≈0.82) confirm that socioeconomic upliftment drives water infrastructure.  \n"
        "- Migration (r≈0.35) has only a **moderate** correlation — "
        "high migration in eastern regions coexists with low water access."
    )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 — SOCIOECONOMIC
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown("## 💰 Socioeconomic Analysis")

    x_options = {
        "Literacy Rate (%)":        "literacy_rate",
        "Average Income (INR)":     "avg_income",
        "Sanitation Coverage (%)":  "sanitation",
        "Clean Cooking Fuel (%)":   "clean_fuel",
        "Migration Rate (%)":       "migration_rate",
    }
    col_left, col_right = st.columns([1, 3])
    with col_left:
        x_label = st.selectbox("X-axis indicator", list(x_options.keys()), key="se_x")
        color_by = st.selectbox("Colour by", ["Rural_Urban", "Region", "Year"], key="se_col")
        add_trendline = st.checkbox("Show trendline", value=True, key="se_trend")

    x_col  = x_options[x_label]
    r_val  = df[[x_col,"water_access"]].corr().iloc[0,1]

    with col_right:
        cmap = {"Rural_Urban": {"Rural": C_RURAL, "Urban": C_URBAN}}
        if color_by in cmap:
            fig_sc2 = px.scatter(
                df, x=x_col, y="water_access",
                color=color_by,
                color_discrete_map=cmap[color_by],
                trendline="ols" if add_trendline else None,
                opacity=0.65,
                title=f"Water Access vs {x_label}  (r = {r_val:.2f})",
                labels={"water_access": "Water Access (%)", x_col: x_label,
                        "Rural_Urban": "Settlement"},
                hover_data=["State","Year","Rural_Urban"],
            )
        else:
            fig_sc2 = px.scatter(
                df, x=x_col, y="water_access",
                color=color_by,
                color_discrete_map=REGION_COLORS if color_by=="Region" else None,
                trendline="ols" if add_trendline else None,
                opacity=0.65,
                title=f"Water Access vs {x_label}  (r = {r_val:.2f})",
                labels={"water_access": "Water Access (%)", x_col: x_label},
                hover_data=["State","Year","Rural_Urban"],
            )
        fig_sc2.update_layout(yaxis_ticksuffix="%")
        st.plotly_chart(fig_sc2, use_container_width=True)

    # Multi-panel: all five indicators
    st.markdown("#### All Socioeconomic Indicators vs Water Access")
    indicator_cols = list(x_options.values())
    indicator_names= list(x_options.keys())

    fig_multi = make_subplots(rows=1, cols=5,
                              subplot_titles=indicator_names,
                              shared_yaxes=True)
    colors_seq = [C_PURPLE, C_GREEN, C_GOLD, C_TEAL, C_RED]
    for i, (xcol, xname, col) in enumerate(zip(indicator_cols, indicator_names, colors_seq), 1):
        fig_multi.add_trace(
            go.Scatter(
                x=df[xcol], y=df["water_access"],
                mode="markers",
                marker=dict(color=col, opacity=0.5, size=5),
                name=xname,
                showlegend=False,
                hovertemplate=f"{xname}: %{{x:.1f}}<br>Water Access: %{{y:.1f}}%<extra></extra>",
            ),
            row=1, col=i,
        )
    fig_multi.update_layout(
        height=340,
        title_text="Scatter: Each Socioeconomic Indicator vs Water Access",
    )
    fig_multi.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig_multi, use_container_width=True)

    # Clean fuel as co-indicator
    st.markdown("#### Clean Cooking Fuel — A Co-Indicator of Water Access")
    fuel_trend = df.groupby(["Year","Rural_Urban"])[["water_access","clean_fuel"]].mean().reset_index()
    f1, f2 = st.columns(2)
    with f1:
        fig_ft = px.line(
            fuel_trend, x="Year", y="clean_fuel", color="Rural_Urban",
            markers=True,
            color_discrete_map={"Rural": C_RURAL, "Urban": C_URBAN},
            title="Clean Cooking Fuel Access (2011–2021)",
            labels={"clean_fuel": "Clean Fuel (%)", "Rural_Urban": "Settlement"},
        )
        fig_ft.update_traces(line_width=3, marker_size=10)
        fig_ft.update_layout(yaxis_ticksuffix="%", xaxis=dict(tickvals=[2011,2016,2021]))
        st.plotly_chart(fig_ft, use_container_width=True)
    with f2:
        r_fuel = df[["clean_fuel","water_access"]].corr().iloc[0,1]
        fig_fs = px.scatter(
            df, x="clean_fuel", y="water_access", color="Rural_Urban",
            color_discrete_map={"Rural": C_RURAL, "Urban": C_URBAN},
            trendline="ols",
            title=f"Clean Fuel vs Water Access  (r = {r_fuel:.2f})",
            labels={"clean_fuel": "Clean Fuel (%)", "water_access": "Water Access (%)",
                    "Rural_Urban": "Settlement"},
            opacity=0.6,
        )
        fig_fs.update_layout(yaxis_ticksuffix="%", xaxis_ticksuffix="%")
        st.plotly_chart(fig_fs, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 8 — IMPROVEMENT
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[8]:
    st.markdown("## 📊 Improvement by State (2011 → 2021)")
    st.caption("Rural water access improvement in percentage points over the decade.")

    imp_type = st.radio("Settlement type", ["Rural", "Urban", "Overall"], horizontal=True, key="imp_type")

    if imp_type == "Overall":
        pivot_imp = (
            df_raw.groupby(["State","Year"])["water_access"].mean()
            .unstack("Year")
        )
    else:
        pivot_imp = (
            df_raw[df_raw["Rural_Urban"] == imp_type]
            .groupby(["State","Year"])["water_access"].mean()
            .unstack("Year")
        )

    if 2011 in pivot_imp.columns and 2021 in pivot_imp.columns:
        pivot_imp["improvement"] = pivot_imp[2021] - pivot_imp[2011]
        pivot_imp = pivot_imp.sort_values("improvement", ascending=False).reset_index()
        pivot_imp["improvement"] = pivot_imp["improvement"].round(1)

        pivot_imp["color_group"] = pivot_imp["improvement"].apply(
            lambda v: "≥ 20 pp" if v >= 20 else ("15–20 pp" if v >= 15 else "< 15 pp")
        )
        cg_map = {"≥ 20 pp": C_GREEN, "15–20 pp": C_URBAN, "< 15 pp": C_GOLD}

        fig_imp = px.bar(
            pivot_imp, x="State", y="improvement",
            color="color_group",
            color_discrete_map=cg_map,
            text="improvement",
            title=f"{imp_type} Water Access Improvement by State (2011 → 2021)",
            labels={"improvement": "Improvement (pp)", "State": "State",
                    "color_group": "Improvement Band"},
        )
        fig_imp.update_traces(texttemplate="+%{text:.1f}", textposition="outside")
        fig_imp.update_layout(
            xaxis_tickangle=-40,
            yaxis_title="Percentage Point Improvement",
            legend_title="Improvement Band",
        )
        st.plotly_chart(fig_imp, use_container_width=True)

        # Absolute before/after
        st.markdown("#### Before (2011) and After (2021) Comparison")
        if 2011 in pivot_imp.columns and 2021 in pivot_imp.columns:
            ba_df = pivot_imp[["State", 2011, 2021, "improvement"]].copy()
            ba_df.columns = ["State", "2011 (%)", "2021 (%)", "Improvement (pp)"]
            ba_df = ba_df.sort_values("Improvement (pp)", ascending=False)

            fig_ba = go.Figure()
            fig_ba.add_trace(go.Bar(
                name="2011", y=ba_df["State"], x=ba_df["2011 (%)"],
                orientation="h", marker_color=C_RED, opacity=0.75,
            ))
            fig_ba.add_trace(go.Bar(
                name="2021", y=ba_df["State"], x=ba_df["2021 (%)"],
                orientation="h", marker_color=C_GREEN, opacity=0.75,
            ))
            fig_ba.update_layout(
                title=f"{imp_type} Water Access: 2011 vs 2021",
                barmode="group",
                xaxis=dict(title="Water Access (%)", ticksuffix="%", range=[0, 110]),
                yaxis_title="State",
                height=600,
                legend_title="Year",
            )
            st.plotly_chart(fig_ba, use_container_width=True)

        # Data table
        with st.expander("📋 Full improvement table"):
            st.dataframe(
                ba_df.set_index("State").style.format("{:.1f}")
                     .background_gradient(subset=["Improvement (pp)"], cmap="Greens"),
                use_container_width=True,
            )
    else:
        st.info("Select years 2011 and 2021 in the sidebar to see improvement data.")

    # Migration context
    st.markdown("#### Migration Context — High Migration vs Low Water Access")
    mig_df = (
        df_raw[df_raw["Year"]==2021]
        .groupby(["Region","Rural_Urban"])[["migration_rate","water_access"]]
        .mean().reset_index()
    )
    fig_mig = px.scatter(
        mig_df, x="migration_rate", y="water_access",
        color="Region", symbol="Rural_Urban",
        color_discrete_map=REGION_COLORS,
        size=[12]*len(mig_df),
        title="Migration Rate vs Water Access by Region (2021)",
        labels={"migration_rate": "Migration Rate (%)", "water_access": "Water Access (%)",
                "Rural_Urban": "Settlement"},
        hover_data=["Region","Rural_Urban"],
    )
    fig_mig.update_layout(yaxis_ticksuffix="%", xaxis_ticksuffix="%")
    st.plotly_chart(fig_mig, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:#888;font-size:12px;'>"
    "PS-38: Improved Source of Drinking Water · IBM SkillsBuild Internship · Data Analytics · "
    "Built with Streamlit & Plotly"
    "</div>",
    unsafe_allow_html=True,
)
