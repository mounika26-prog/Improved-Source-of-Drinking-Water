"""
Validation script — runs the full analysis logic from the notebook.
Saves all 11 charts to results/ and prints key statistics.
"""
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')   # non-interactive backend for script execution
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from matplotlib.patches import Patch
import warnings
warnings.filterwarnings('ignore')

os.makedirs('results', exist_ok=True)

sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams.update({
    'figure.dpi': 120, 'font.size': 11,
    'axes.titlesize': 13, 'axes.titleweight': 'bold',
    'axes.labelsize': 11, 'xtick.labelsize': 9, 'ytick.labelsize': 9,
})

# ── Load Data ────────────────────────────────────────────────────────────────
df = pd.read_csv('data/drinking_water_data.csv')
assert df.shape == (192, 14), f"Unexpected shape: {df.shape}"
print(f"✅  Loaded dataset: {df.shape[0]} rows × {df.shape[1]} cols")

df.rename(columns={
    'Improved_Water_Access_%'   : 'water_access',
    'Unimproved_Water_Access_%' : 'unimproved_water',
    'Clean_Cooking_Fuel_%'      : 'clean_fuel',
    'Solid_Fuel_%'              : 'solid_fuel',
    'Migration_Rate_%'          : 'migration_rate',
    'Literacy_Rate_%'           : 'literacy_rate',
    'Sanitation_Coverage_%'     : 'sanitation',
    'Avg_Income_INR'            : 'avg_income',
}, inplace=True)

df['Year'] = df['Year'].astype(int)
rural_df = df[df['Rural_Urban'] == 'Rural'].copy()
urban_df = df[df['Rural_Urban'] == 'Urban'].copy()

colors_ru = {'Rural': '#e67e22', 'Urban': '#2980b9'}

# ── Chart 1: National Trend ───────────────────────────────────────────────
national_trend = df.groupby(['Year', 'Rural_Urban'])['water_access'].mean().reset_index()
fig, ax = plt.subplots(figsize=(9, 5))
markers = {'Rural': 'o', 'Urban': 's'}
for label, group in national_trend.groupby('Rural_Urban'):
    ax.plot(group['Year'], group['water_access'],
            marker=markers[label], linewidth=2.5, markersize=9,
            color=colors_ru[label], label=label)
    for _, row in group.iterrows():
        ax.annotate(f"{row['water_access']:.1f}%",
                    xy=(row['Year'], row['water_access']),
                    xytext=(0, 10), textcoords='offset points',
                    ha='center', fontsize=9, color=colors_ru[label])
ax.set_title('National Average — Improved Drinking Water Access (2011–2021)')
ax.set_xlabel('Year'); ax.set_ylabel('Improved Water Access (%)')
ax.set_xticks([2011, 2016, 2021]); ax.set_ylim(40, 105)
ax.legend(title='Settlement Type', fontsize=10)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
plt.tight_layout()
plt.savefig('results/01_national_trend.png', bbox_inches='tight')
plt.close()
print("✅  Chart 1 saved")

# ── Chart 2: Rural vs Urban Distribution ────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sns.boxplot(data=df, x='Year', y='water_access', hue='Rural_Urban',
            palette=colors_ru, ax=axes[0], width=0.55)
axes[0].set_title('Water Access Distribution by Year & Settlement')
axes[0].set_xlabel('Year'); axes[0].set_ylabel('Improved Water Access (%)')
axes[0].yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
axes[0].legend(title='Type')
df_2021 = df[df['Year'] == 2021]
sns.violinplot(data=df_2021, x='Rural_Urban', y='water_access',
               palette=colors_ru, ax=axes[1], inner='box')
axes[1].set_title('Water Access Distribution in 2021 (Rural vs Urban)')
axes[1].set_xlabel('Settlement Type'); axes[1].set_ylabel('Improved Water Access (%)')
axes[1].yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
plt.tight_layout()
plt.savefig('results/02_rural_urban_distribution.png', bbox_inches='tight')
plt.close()
print("✅  Chart 2 saved")

# ── Chart 3: State Comparison 2021 ──────────────────────────────────────────
state_2021 = (
    df[df['Year'] == 2021]
    .groupby(['State', 'Rural_Urban'])['water_access']
    .mean().unstack().sort_values('Rural', ascending=False)
)
fig, ax = plt.subplots(figsize=(13, 7))
x = np.arange(len(state_2021)); width = 0.38
ax.bar(x - width/2, state_2021['Rural'], width, label='Rural',
       color='#e67e22', alpha=0.85, edgecolor='white')
ax.bar(x + width/2, state_2021['Urban'], width, label='Urban',
       color='#2980b9', alpha=0.85, edgecolor='white')
ax.set_title('State-Wise Improved Drinking Water Access — 2021')
ax.set_xlabel('State'); ax.set_ylabel('Improved Water Access (%)')
ax.set_xticks(x)
ax.set_xticklabels(state_2021.index, rotation=45, ha='right', fontsize=8)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
ax.set_ylim(50, 105); ax.legend(title='Settlement Type')
ax.axhline(90, color='green', linestyle='--', linewidth=1.2, alpha=0.6)
plt.tight_layout()
plt.savefig('results/03_state_comparison_2021.png', bbox_inches='tight')
plt.close()
print("✅  Chart 3 saved")

# ── Chart 4: Regional Trends ─────────────────────────────────────────────────
region_year = df.groupby(['Region', 'Year'])['water_access'].mean().reset_index()
region_palette = {
    'South': '#27ae60', 'West': '#2980b9', 'North': '#8e44ad',
    'East': '#e74c3c', 'Central': '#f39c12', 'Northeast': '#16a085'
}
fig, ax = plt.subplots(figsize=(10, 6))
for region, group in region_year.groupby('Region'):
    ax.plot(group['Year'], group['water_access'],
            marker='o', linewidth=2.2, markersize=8,
            color=region_palette.get(region, 'grey'), label=region)
ax.set_title('Regional Average — Improved Drinking Water Access (2011–2021)')
ax.set_xlabel('Year'); ax.set_ylabel('Improved Water Access (%)')
ax.set_xticks([2011, 2016, 2021])
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
ax.legend(title='Region', bbox_to_anchor=(1.01, 1), loc='upper left')
plt.tight_layout()
plt.savefig('results/04_regional_trends.png', bbox_inches='tight')
plt.close()
print("✅  Chart 4 saved")

# ── Chart 5: Top/Bottom States ───────────────────────────────────────────────
rural_2021 = (
    df[(df['Year'] == 2021) & (df['Rural_Urban'] == 'Rural')]
    .groupby('State')['water_access'].mean()
    .sort_values(ascending=False)
)
top5 = rural_2021.head(5); bottom5 = rural_2021.tail(5)
combined = pd.concat([top5, bottom5])
colors_tb = ['#27ae60'] * 5 + ['#e74c3c'] * 5
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(combined.index, combined.values, color=colors_tb,
               edgecolor='white', height=0.65)
for bar, val in zip(bars, combined.values):
    ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
            f'{val:.1f}%', va='center', fontsize=9)
ax.set_title('Top 5 vs Bottom 5 States — Rural Water Access (2021)')
ax.set_xlabel('Improved Water Access (%)')
ax.set_xlim(40, 105)
ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
ax.axvline(80, color='gray', linestyle='--', linewidth=1, alpha=0.6)
ax.legend(handles=[Patch(facecolor='#27ae60', label='Top 5'),
                   Patch(facecolor='#e74c3c', label='Bottom 5')])
plt.tight_layout()
plt.savefig('results/05_top_bottom_states.png', bbox_inches='tight')
plt.close()
print("✅  Chart 5 saved")

# ── Chart 6: Correlation Heatmap ─────────────────────────────────────────────
numeric_cols = ['water_access', 'clean_fuel', 'migration_rate',
                'literacy_rate', 'sanitation', 'avg_income']
corr_matrix = df[numeric_cols].corr().round(2)
labels = {
    'water_access': 'Water Access', 'clean_fuel': 'Clean Fuel',
    'migration_rate': 'Migration Rate', 'literacy_rate': 'Literacy Rate',
    'sanitation': 'Sanitation', 'avg_income': 'Avg Income'
}
corr_matrix.rename(index=labels, columns=labels, inplace=True)
fig, ax = plt.subplots(figsize=(8, 6))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f',
            cmap='RdYlGn', vmin=-1, vmax=1, center=0,
            square=True, linewidths=0.5, ax=ax, annot_kws={'size': 10})
ax.set_title('Correlation Matrix — Drinking Water & Socio-Economic Indicators')
plt.tight_layout()
plt.savefig('results/06_correlation_heatmap.png', bbox_inches='tight')
plt.close()
print("✅  Chart 6 saved")

# ── Chart 7: Scatter Socioeconomic ───────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
scatter_pairs = [
    ('literacy_rate', 'Literacy Rate (%)', '#8e44ad'),
    ('avg_income',    'Avg Income (INR)',  '#27ae60'),
    ('sanitation',    'Sanitation Coverage (%)', '#e67e22'),
]
for ax, (xcol, xlabel, color) in zip(axes, scatter_pairs):
    ax.scatter(df[xcol], df['water_access'], alpha=0.45, color=color, s=28, edgecolors='none')
    z = np.polyfit(df[xcol].dropna(), df.loc[df[xcol].notna(), 'water_access'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df[xcol].min(), df[xcol].max(), 200)
    ax.plot(x_line, p(x_line), color='black', linewidth=1.8, linestyle='--')
    r = df[[xcol, 'water_access']].corr().iloc[0, 1]
    ax.set_title(f'Water Access vs {xlabel}\nr = {r:.2f}', fontsize=10)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel('Improved Water Access (%)', fontsize=9)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
plt.suptitle('Scatter Analysis — Socio-Economic Drivers of Water Access',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('results/07_scatter_socioeconomic.png', bbox_inches='tight')
plt.close()
print("✅  Chart 7 saved")

# ── Chart 8: Clean Fuel & Water ──────────────────────────────────────────────
fuel_trend = df.groupby(['Year', 'Rural_Urban'])[['water_access', 'clean_fuel']].mean().reset_index()
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for label, group in fuel_trend.groupby('Rural_Urban'):
    axes[0].plot(group['Year'], group['clean_fuel'],
                 marker='o', linewidth=2.2, markersize=8,
                 color=colors_ru[label], label=label)
axes[0].set_title('Clean Cooking Fuel Access (2011–2021)')
axes[0].set_xlabel('Year'); axes[0].set_ylabel('Households with Clean Fuel (%)')
axes[0].set_xticks([2011, 2016, 2021])
axes[0].yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
axes[0].legend(title='Settlement')
for label in ['Rural', 'Urban']:
    subset = df[df['Rural_Urban'] == label]
    axes[1].scatter(subset['clean_fuel'], subset['water_access'],
                    alpha=0.5, color=colors_ru[label], s=30, label=label)
z = np.polyfit(df['clean_fuel'], df['water_access'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['clean_fuel'].min(), df['clean_fuel'].max(), 200)
axes[1].plot(x_line, p(x_line), 'k--', linewidth=1.8)
r = df[['clean_fuel', 'water_access']].corr().iloc[0, 1]
axes[1].set_title(f'Clean Fuel vs Improved Water Access (r = {r:.2f})')
axes[1].set_xlabel('Clean Cooking Fuel Access (%)')
axes[1].set_ylabel('Improved Water Access (%)')
axes[1].xaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
axes[1].yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
axes[1].legend(title='Settlement')
plt.tight_layout()
plt.savefig('results/08_clean_fuel_water.png', bbox_inches='tight')
plt.close()
print("✅  Chart 8 saved")

# ── Chart 9: Migration Analysis ───────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for label in ['Rural', 'Urban']:
    subset = df[df['Rural_Urban'] == label]
    axes[0].scatter(subset['migration_rate'], subset['water_access'],
                    alpha=0.5, color=colors_ru[label], s=30, label=label)
z = np.polyfit(df['migration_rate'], df['water_access'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['migration_rate'].min(), df['migration_rate'].max(), 200)
axes[0].plot(x_line, p(x_line), 'k--', linewidth=1.8)
r = df[['migration_rate', 'water_access']].corr().iloc[0, 1]
axes[0].set_title(f'Migration Rate vs Water Access (r = {r:.2f})')
axes[0].set_xlabel('Migration Rate (%)'); axes[0].set_ylabel('Improved Water Access (%)')
axes[0].yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
axes[0].legend(title='Settlement')
migration_region = (
    df[df['Year'] == 2021].groupby('Region')['migration_rate']
    .mean().sort_values(ascending=False)
)
region_colors = ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#8e44ad', '#16a085']
axes[1].bar(migration_region.index, migration_region.values,
            color=region_colors, edgecolor='white')
axes[1].set_title('Average Migration Rate by Region (2021)')
axes[1].set_xlabel('Region'); axes[1].set_ylabel('Migration Rate (%)')
axes[1].set_xticklabels(migration_region.index, rotation=30, ha='right')
for i, val in enumerate(migration_region.values):
    axes[1].text(i, val + 0.1, f'{val:.1f}%', ha='center', fontsize=9)
plt.tight_layout()
plt.savefig('results/09_migration_analysis.png', bbox_inches='tight')
plt.close()
print("✅  Chart 9 saved")

# ── Chart 10: Improvement by State ───────────────────────────────────────────
pivot = (
    df[df['Rural_Urban'] == 'Rural']
    .groupby(['State', 'Year'])['water_access']
    .mean().unstack('Year')
)
pivot['improvement'] = pivot[2021] - pivot[2011]
pivot = pivot.sort_values('improvement', ascending=False)
bar_colors_imp = ['#27ae60' if v >= 20 else '#3498db' if v >= 15 else '#f39c12'
                  for v in pivot['improvement']]
fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(pivot.index, pivot['improvement'], color=bar_colors_imp, edgecolor='white')
for bar, val in zip(bars, pivot['improvement']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            f'+{val:.1f}', ha='center', va='bottom', fontsize=8)
ax.set_title('Rural Water Access Improvement by State (2011 → 2021)')
ax.set_xlabel('State'); ax.set_ylabel('Percentage Point Improvement')
ax.set_xticklabels(pivot.index, rotation=45, ha='right', fontsize=8)
ax.legend(handles=[
    Patch(facecolor='#27ae60', label='≥ 20 pp (High improvement)'),
    Patch(facecolor='#3498db', label='15–20 pp (Moderate)'),
    Patch(facecolor='#f39c12', label='< 15 pp (Slow)'),
], loc='upper right', fontsize=9)
plt.tight_layout()
plt.savefig('results/10_improvement_by_state.png', bbox_inches='tight')
plt.close()
print("✅  Chart 10 saved")

# ── Chart 11: Fuel Pie Charts ─────────────────────────────────────────────────
fuel_2021 = (
    df[df['Year'] == 2021]
    .groupby('Rural_Urban')[['clean_fuel', 'solid_fuel']].mean()
)
fig, axes = plt.subplots(1, 2, figsize=(11, 5))
for ax, (label, row) in zip(axes, fuel_2021.iterrows()):
    wedges, texts, autotexts = ax.pie(
        [row['clean_fuel'], row['solid_fuel']],
        labels=['Clean Fuel (LPG/PNG)', 'Solid Fuel (Wood/Biomass)'],
        autopct='%1.1f%%', colors=['#27ae60', '#e74c3c'],
        startangle=90, pctdistance=0.82,
        wedgeprops=dict(edgecolor='white', linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(11); at.set_fontweight('bold')
    ax.set_title(f'{label} — Cooking Fuel Mix (2021)', fontsize=11)
plt.suptitle('Cooking Fuel Type Distribution — Rural vs Urban (2021)',
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('results/11_fuel_pie_charts.png', bbox_inches='tight')
plt.close()
print("✅  Chart 11 saved")

# ── Export CSVs ───────────────────────────────────────────────────────────────
state_summary = (
    df.groupby(['State', 'Region', 'Year', 'Rural_Urban'])
    [['water_access', 'clean_fuel', 'literacy_rate', 'sanitation', 'avg_income', 'migration_rate']]
    .mean().round(2).reset_index()
)
state_summary.to_csv('results/state_summary.csv', index=False)
improvement_table = pivot[['improvement']].rename(
    columns={'improvement': 'Rural_Improvement_pp (2011→2021)'})
improvement_table.to_csv('results/improvement_table.csv')
print("✅  CSVs exported")

# ── Print Key Stats ───────────────────────────────────────────────────────────
print('\n' + '=' * 60)
print('        KEY STATISTICS')
print('=' * 60)
nat_2011 = df[df['Year'] == 2011]['water_access'].mean()
nat_2021 = df[df['Year'] == 2021]['water_access'].mean()
print(f"National water access 2011: {nat_2011:.1f}%  →  2021: {nat_2021:.1f}%  (Δ +{nat_2021-nat_2011:.1f} pp)")
r_2021 = df[(df['Year']==2021)&(df['Rural_Urban']=='Rural')]['water_access'].mean()
u_2021 = df[(df['Year']==2021)&(df['Rural_Urban']=='Urban')]['water_access'].mean()
print(f"Rural 2021: {r_2021:.1f}%   Urban 2021: {u_2021:.1f}%   Gap: {u_2021-r_2021:.1f} pp")
print("Correlations with Water Access:")
for col, name in [('literacy_rate','Literacy'),('avg_income','Income'),
                   ('sanitation','Sanitation'),('clean_fuel','Clean Fuel')]:
    r = df[col].corr(df['water_access'])
    print(f"  {name:15s}: r = {r:.3f}")
print('=' * 60)
print('\n🎉  All validations passed! Project is ready.')
