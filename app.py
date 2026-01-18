import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="UIDAI District Dashboard",
    layout="wide"
)


# ---------------- DATA LOADING ---------------- #

@st.cache_data
def load_dashboard_data():
    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / "outputs" / "dashboard" / "dashboard_data.csv"
    return pd.read_csv(data_path)


df = load_dashboard_data()


# ---------------- SIDEBAR ---------------- #

st.sidebar.title("Filters")

states = ["All"] + sorted(df["state"].unique().tolist())
selected_state = st.sidebar.selectbox("Select State", states)

if selected_state == "All":
    df_view = df.copy()
else:
    df_view = df[df["state"] == selected_state]


# ---------------- HEADER ---------------- #

st.title("UIDAI District-Level Dashboard")
st.caption("Official district-wise UIDAI statistics (post normalization)")


# ---------------- SUMMARY METRICS ---------------- #

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total States",
    df["state"].nunique()
)

col2.metric(
    "Total Official Districts",
    df["district"].nunique()
)

col3.metric(
    "Total UIDAI Records",
    int(
        df[
            [
                "age_0_5",
                "age_5_17",
                "age_18_greater",
                "bio_age_5_17",
                "bio_age_17_",
                "demo_age_17_",
            ]
        ].sum().sum()
    )
)

st.divider()


# ---------------- METRIC SELECTION ---------------- #

st.subheader("District-wise UIDAI Metrics")

metric_map = {
    "Enrolment (Age 0–5)": "age_0_5",
    "Enrolment (Age 5–17)": "age_5_17",
    "Enrolment (Age 18+)": "age_18_greater",
    "Biometric Updates (Age 5–17)": "bio_age_5_17",
    "Biometric Updates (Age 18+)": "bio_age_17_",
    "Demographic Updates (Age 18+)": "demo_age_17_",
}

metric_label = st.selectbox(
    "Select Metric",
    list(metric_map.keys())
)

metric_col = metric_map[metric_label]


# ---------------- BAR CHART ---------------- #

fig = px.bar(
    df_view,
    x="district",
    y=metric_col,
    color="state",
    title=f"{metric_label} by District",
)

fig.update_layout(
    xaxis_tickangle=-45,
    height=520,
    legend_title_text="State"
)

st.plotly_chart(fig, use_container_width=True)


# ---------------- DATA TABLE ---------------- #

st.subheader("District-Level Aggregated Data")

st.dataframe(
    df_view.sort_values(["state", "district"]),
    use_container_width=True
)

st.header("📊 Exploratory Data Analysis (EDA)")
st.subheader("1️⃣ Univariate Analysis")

st.write("Analyze the distribution of individual variables across all districts")

uni_metric_map = {
    "Enrolment (Age 0–5)": "age_0_5",
    "Enrolment (Age 5–17)": "age_5_17",
    "Enrolment (Age 18+)": "age_18_greater",
    "Biometric Updates (Age 5–17)": "bio_age_5_17",
    "Biometric Updates (Age 18+)": "bio_age_17_",
    "Demographic Updates (Age 5–17)": "demo_age_5_17",
    "Demographic Updates (Age 18+)": "demo_age_17_",
}

uni_metric_label = st.selectbox(
    "Select variable for univariate analysis",
    list(uni_metric_map.keys()),
    key="uni"
)

uni_col = uni_metric_map[uni_metric_label]

col_uni_1, col_uni_2 = st.columns(2)

# Histogram
with col_uni_1:
    fig_uni_hist = px.histogram(
        df,
        x=uni_col,
        nbins=50,
        title=f"Distribution: {uni_metric_label}",
        marginal="box"
    )
    st.plotly_chart(fig_uni_hist, use_container_width=True)

# Box plot by state
with col_uni_2:
    fig_uni_box = px.box(
        df,
        y=uni_col,
        x="state",
        title=f"Box Plot by State: {uni_metric_label}",
        points="outliers"
    )
    fig_uni_box.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig_uni_box, use_container_width=True)

# Summary statistics
with st.expander("📈 Summary Statistics"):
    stats = df[uni_col].describe()
    st.write(stats)
    
    col_stat_1, col_stat_2, col_stat_3 = st.columns(3)
    col_stat_1.metric("Mean", f"{df[uni_col].mean():.2f}")
    col_stat_2.metric("Median", f"{df[uni_col].median():.2f}")
    col_stat_3.metric("Std Dev", f"{df[uni_col].std():.2f}")

st.subheader("2️⃣ Bivariate Analysis")

st.write("Analyze relationships between different variable pairs")

# Define metric pairs for bivariate analysis
bivariate_pairs = {
    "Enrolment vs Biometric": ("age_18_greater", "bio_age_17_"),
    "Enrolment vs Demographic": ("age_18_greater", "demo_age_17_"),
    "Biometric vs Demographic": ("bio_age_17_", "demo_age_17_"),
    "Age 0-5 vs Age 5-17": ("age_0_5", "age_5_17"),
    "Age 5-17 vs Age 18+": ("age_5_17", "age_18_greater"),
    "Biometric Age Groups": ("bio_age_5_17", "bio_age_17_"),
    "Demographic Age Groups": ("demo_age_5_17", "demo_age_17_"),
    "Enrolment (0-5) vs Biometric (5-17)": ("age_0_5", "bio_age_5_17"),
    "Enrolment (5-17) vs Biometric (5-17)": ("age_5_17", "bio_age_5_17"),
}

bivariate_pair = st.selectbox(
    "Select variable pair",
    list(bivariate_pairs.keys()),
    key="bi_pair"
)

x_metric, y_metric = bivariate_pairs[bivariate_pair]

col_bi_1, col_bi_2 = st.columns(2)

# Scatter plot with state coloring
with col_bi_1:
    fig_bi_scatter = px.scatter(
        df,
        x=x_metric,
        y=y_metric,
        color="state",
        title=f"Scatter: {bivariate_pair}",
        opacity=0.7,
        trendline="ols",
        hover_name="district"
    )
    st.plotly_chart(fig_bi_scatter, use_container_width=True)

# 2D Density heatmap
with col_bi_2:
    fig_bi_density = px.density_contour(
        df,
        x=x_metric,
        y=y_metric,
        title=f"Density Distribution: {bivariate_pair}",
    )
    st.plotly_chart(fig_bi_density, use_container_width=True)

# Correlation analysis
with st.expander("📊 Correlation & Statistical Details"):
    correlation = df[x_metric].corr(df[y_metric])
    st.metric("Pearson Correlation", f"{correlation:.4f}")
    
    col_corr_1, col_corr_2 = st.columns(2)
    with col_corr_1:
        st.write(f"**{x_metric}**")
        st.write(df[x_metric].describe())
    with col_corr_2:
        st.write(f"**{y_metric}**")
        st.write(df[y_metric].describe())

st.subheader("3️⃣ Multivariate Analysis")

st.write("Analyze relationships between multiple variables simultaneously")

multivar_options = {
    "Enrolment Types": {
        "x": "age_0_5",
        "y": "age_5_17",
        "size": "age_18_greater",
    },
    "Biometric & Demographic Updates": {
        "x": "age_18_greater",
        "y": "bio_age_17_",
        "size": "demo_age_17_",
    },
    "All Age Groups": {
        "x": "age_5_17",
        "y": "bio_age_5_17",
        "size": "demo_age_5_17",
    },
    "Enrolment vs Biometric vs Demographic": {
        "x": "age_18_greater",
        "y": "bio_age_17_",
        "size": "demo_age_17_",
    },
}

multivar_choice = st.selectbox(
    "Select multivariate relationship",
    list(multivar_options.keys()),
    key="multi"
)

mv_config = multivar_options[multivar_choice]

fig_multi = px.scatter(
    df,
    x=mv_config["x"],
    y=mv_config["y"],
    size=mv_config["size"],
    color="state",
    hover_name="district",
    title=multivar_choice,
    size_max=40,
    opacity=0.7
)

fig_multi.update_layout(height=550)
st.plotly_chart(fig_multi, use_container_width=True)

# Correlation heatmap for all metrics
with st.expander("🔥 Correlation Matrix (All Metrics)"):
    correlation_cols = [
        "age_0_5",
        "age_5_17",
        "age_18_greater",
        "bio_age_5_17",
        "bio_age_17_",
        "demo_age_5_17",
        "demo_age_17_",
    ]
    
    corr_matrix = df[correlation_cols].corr()
    
    fig_corr = px.imshow(
        corr_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        title="Correlation Heatmap",
        labels=dict(x="", y=""),
        aspect="auto"
    )
    fig_corr.update_layout(height=600)
    st.plotly_chart(fig_corr, use_container_width=True)


# ============================================ #
#        RISK ANALYSIS & RECOMMENDATIONS      #
# ============================================ #

st.divider()
st.header("⚠️ Risk Analysis & Recommendations")

def calculate_risk_score(row):
    """Calculate risk score based on enrollment and update metrics"""
    risk_score = 0
    risk_factors = []
    
    # Enrolment Risk
    total_enrolment = row['age_0_5'] + row['age_5_17'] + row['age_18_greater']
    if total_enrolment < df['age_0_5'].quantile(0.25) + df['age_5_17'].quantile(0.25) + df['age_18_greater'].quantile(0.25):
        risk_score += 25
        risk_factors.append("Low enrollment numbers")
    
    # Biometric Update Coverage Risk
    bio_coverage = (row['bio_age_5_17'] + row['bio_age_17_']) / max(row['age_5_17'] + row['age_18_greater'], 1)
    if bio_coverage < 0.3:
        risk_score += 30
        risk_factors.append("Low biometric update coverage")
    elif bio_coverage < 0.5:
        risk_score += 15
        risk_factors.append("Moderate biometric update coverage")
    
    # Demographic Update Coverage Risk
    demo_coverage = (row['demo_age_5_17'] + row['demo_age_17_']) / max(row['age_5_17'] + row['age_18_greater'], 1)
    if demo_coverage < 0.3:
        risk_score += 30
        risk_factors.append("Low demographic update coverage")
    elif demo_coverage < 0.5:
        risk_score += 15
        risk_factors.append("Moderate demographic update coverage")
    
    # Age 0-5 Enrollment Gap
    if row['age_0_5'] < df['age_0_5'].quantile(0.25):
        risk_score += 20
        risk_factors.append("Low age 0-5 enrollment")
    
    return risk_score, risk_factors

# Calculate risk scores
df_risk = df.copy()
df_risk[['risk_score', 'risk_factors']] = df_risk.apply(
    lambda row: pd.Series(calculate_risk_score(row)), axis=1
)

def get_risk_level(score):
    """Categorize risk level"""
    if score >= 70:
        return "🔴 Critical"
    elif score >= 50:
        return "🟠 High"
    elif score >= 30:
        return "🟡 Medium"
    else:
        return "🟢 Low"

df_risk['risk_level'] = df_risk['risk_score'].apply(get_risk_level)

# Filter by state
risk_df_view = df_risk[df_risk['state'] == selected_state] if selected_state != "All" else df_risk

# Risk Overview Metrics
st.subheader("Risk Summary")
col_risk_1, col_risk_2, col_risk_3, col_risk_4 = st.columns(4)

critical_count = (df_risk['risk_score'] >= 70).sum()
high_count = ((df_risk['risk_score'] >= 50) & (df_risk['risk_score'] < 70)).sum()
medium_count = ((df_risk['risk_score'] >= 30) & (df_risk['risk_score'] < 50)).sum()
low_count = (df_risk['risk_score'] < 30).sum()

col_risk_1.metric("🔴 Critical", critical_count)
col_risk_2.metric("🟠 High", high_count)
col_risk_3.metric("🟡 Medium", medium_count)
col_risk_4.metric("🟢 Low", low_count)

# Risk Distribution Chart
fig_risk_dist = px.bar(
    df_risk,
    x='risk_level',
    title="Risk Level Distribution Across Districts",
    labels={'risk_level': 'Risk Level', 'count': 'Number of Districts'},
    color='risk_level',
    color_discrete_map={
        '🔴 Critical': '#EF553B',
        '🟠 High': '#FF9900',
        '🟡 Medium': '#FFD700',
        '🟢 Low': '#00CC96'
    }
)
st.plotly_chart(fig_risk_dist, use_container_width=True)

# High-Risk Districts Table
st.subheader("⚠️ High-Risk Districts Requiring Attention")

high_risk_df = df_risk[df_risk['risk_score'] >= 50].sort_values('risk_score', ascending=False)

if len(high_risk_df) > 0:
    risk_display = high_risk_df[['state', 'district', 'risk_score', 'risk_level']].head(20)
    st.dataframe(risk_display, use_container_width=True)
else:
    st.success("✅ No high-risk districts identified!")

# Detailed Risk Analysis by District
st.subheader("🔍 Detailed Risk Analysis")

selected_district = st.selectbox(
    "Select a district for detailed risk assessment",
    risk_df_view.sort_values('district')['district'].unique(),
    key="risk_district"
)

district_risk = risk_df_view[risk_df_view['district'] == selected_district].iloc[0]

# Risk Profile
col_profile_1, col_profile_2, col_profile_3, col_profile_4 = st.columns(4)

col_profile_1.metric(
    "Risk Score",
    int(district_risk['risk_score']),
    delta=f"Status: {district_risk['risk_level']}"
)

total_enrolment = district_risk['age_0_5'] + district_risk['age_5_17'] + district_risk['age_18_greater']
col_profile_2.metric(
    "Total Enrollment",
    int(total_enrolment)
)

# Calculate coverage percentages correctly
bio_enrolment = district_risk['age_5_17'] + district_risk['age_18_greater']
bio_updates = district_risk['bio_age_5_17'] + district_risk['bio_age_17_']
bio_cov = (bio_updates / max(bio_enrolment, 1)) * 100 if bio_enrolment > 0 else 0

demo_enrolment = district_risk['age_5_17'] + district_risk['age_18_greater']
demo_updates = district_risk['demo_age_5_17'] + district_risk['demo_age_17_']
demo_cov = (demo_updates / max(demo_enrolment, 1)) * 100 if demo_enrolment > 0 else 0

enrol_0_to_5 = district_risk['age_0_5']
enrol_5_to_17 = district_risk['age_5_17']
enrol_18_plus = district_risk['age_18_greater']

col_profile_3.metric(
    "Biometric Coverage %",
    f"{bio_cov:.1f}%",
    f"{int(bio_updates):,} / {int(bio_enrolment):,}"
)

col_profile_4.metric(
    "Demographic Coverage %",
    f"{demo_cov:.1f}%",
    f"{int(demo_updates):,} / {int(demo_enrolment):,}"
)

# Enrollment Breakdown
with st.expander("📊 Enrollment Breakdown by Age Group"):
    col_enrol_1, col_enrol_2, col_enrol_3 = st.columns(3)
    col_enrol_1.metric("Age 0-5", f"{int(enrol_0_to_5):,}")
    col_enrol_2.metric("Age 5-17", f"{int(enrol_5_to_17):,}")
    col_enrol_3.metric("Age 18+", f"{int(enrol_18_plus):,}")
    
    # Pie chart
    enrollment_breakdown = pd.DataFrame({
        'Age Group': ['0-5', '5-17', '18+'],
        'Count': [enrol_0_to_5, enrol_5_to_17, enrol_18_plus]
    })
    
    fig_enrol_pie = px.pie(
        enrollment_breakdown,
        names='Age Group',
        values='Count',
        title='Enrollment Distribution by Age Group'
    )
    st.plotly_chart(fig_enrol_pie, width='stretch')

# Risk Factors
with st.expander("📋 Risk Factors Identified"):
    if district_risk['risk_factors']:
        for i, factor in enumerate(district_risk['risk_factors'], 1):
            st.write(f"{i}. {factor}")
    else:
        st.success("No major risk factors identified")

# Recommended Actions
st.subheader("✅ Recommended Actions")

recommendations = []

# Use the bio_cov and demo_cov calculated earlier (already in percentage form)
bio_cov_ratio = bio_cov / 100  # Convert to ratio for comparison
demo_cov_ratio = demo_cov / 100

if district_risk['risk_score'] >= 70:
    recommendations.append({
        'priority': '🔴 Critical',
        'action': 'Immediate intervention required',
        'details': 'Schedule urgent review and allocate resources for comprehensive enrollment and update drive'
    })

if bio_cov_ratio < 0.3:
    recommendations.append({
        'priority': '🟠 High',
        'action': 'Biometric Update Campaign',
        'details': f'Launch targeted biometric update camps. Current coverage is {bio_cov:.1f}%. Target: 70%+'
    })

if demo_cov_ratio < 0.3:
    recommendations.append({
        'priority': '🟠 High',
        'action': 'Demographic Update Drive',
        'details': f'Mobilize field teams for demographic data collection. Current coverage is {demo_cov:.1f}%. Target: 70%+'
    })

if district_risk['age_0_5'] < df['age_0_5'].quantile(0.25):
    recommendations.append({
        'priority': '🟡 Medium',
        'action': 'Newborn Enrollment Focus',
        'details': 'Enhance enrollment at birth registration centers. Coordinate with health departments'
    })

total_enrolment = district_risk['age_0_5'] + district_risk['age_5_17'] + district_risk['age_18_greater']
if total_enrolment < df[['age_0_5', 'age_5_17', 'age_18_greater']].sum(axis=1).quantile(0.25):
    recommendations.append({
        'priority': '🟡 Medium',
        'action': 'General Enrollment Drive',
        'details': 'Conduct community awareness and enrollment camps targeting underrepresented areas'
    })

if len(recommendations) == 0:
    recommendations.append({
        'priority': '🟢 Low',
        'action': 'Maintain Current Operations',
        'details': 'District is performing well. Continue regular monitoring and maintenance activities'
    })

for rec in recommendations:
    with st.container():
        st.markdown(f"### {rec['priority']} - {rec['action']}")
        st.write(rec['details'])

# Comparison with State Average
st.subheader("📊 Comparison with State Average")

if selected_state != "All":
    # Get the selected district's state
    district_state = district_risk['state']
    
    # Calculate state average for the district's state
    state_data = df_risk[df_risk['state'] == district_state]
    state_avg_enrolment = state_data[['age_0_5', 'age_5_17', 'age_18_greater']].sum(axis=1).mean()
    state_avg_bio = (state_data['bio_age_5_17'].mean() + state_data['bio_age_17_'].mean())
    state_avg_demo = (state_data['demo_age_5_17'].mean() + state_data['demo_age_17_'].mean())
    
    district_total_enrolment = district_risk['age_0_5'] + district_risk['age_5_17'] + district_risk['age_18_greater']
    district_bio = district_risk['bio_age_5_17'] + district_risk['bio_age_17_']
    district_demo = district_risk['demo_age_5_17'] + district_risk['demo_age_17_']
    
    col_comp_1, col_comp_2, col_comp_3 = st.columns(3)
    
    enrolment_diff = district_total_enrolment - state_avg_enrolment
    bio_diff = district_bio - state_avg_bio
    demo_diff = district_demo - state_avg_demo
    
    col_comp_1.metric(
        "Total Enrollment",
        f"{int(district_total_enrolment):,}",
        f"{enrolment_diff:+.0f} vs state avg",
        delta_color="inverse"
    )
    
    col_comp_2.metric(
        "Biometric Updates",
        f"{int(district_bio):,}",
        f"{bio_diff:+.0f} vs state avg",
        delta_color="inverse"
    )
    
    col_comp_3.metric(
        "Demographic Updates",
        f"{int(district_demo):,}",
        f"{demo_diff:+.0f} vs state avg",
        delta_color="inverse"
    )
    
    # Performance vs State Visualization
    with st.expander("📈 Detailed State Comparison"):
        col_perf_1, col_perf_2 = st.columns(2)
        
        with col_perf_1:
            # Enrollment breakdown comparison
            comparison_data = pd.DataFrame({
                'Age Group': ['0-5', '5-17', '18+'],
                'District': [
                    district_risk['age_0_5'],
                    district_risk['age_5_17'],
                    district_risk['age_18_greater']
                ],
                'State Avg': [
                    state_data['age_0_5'].mean(),
                    state_data['age_5_17'].mean(),
                    state_data['age_18_greater'].mean()
                ]
            })
            
            fig_comp = px.bar(
                comparison_data,
                x='Age Group',
                y=['District', 'State Avg'],
                title=f"{district_state}: {selected_district} vs State Average (Enrollment)",
                barmode='group'
            )
            st.plotly_chart(fig_comp, use_container_width=True)
        
        with col_perf_2:
            # Updates comparison
            update_comparison = pd.DataFrame({
                'Type': ['Biometric', 'Demographic'],
                'District': [district_bio, district_demo],
                'State Avg': [state_avg_bio, state_avg_demo]
            })
            
            fig_updates = px.bar(
                update_comparison,
                x='Type',
                y=['District', 'State Avg'],
                title=f"{district_state}: {selected_district} vs State Average (Updates)",
                barmode='group'
            )
            st.plotly_chart(fig_updates, use_container_width=True)
else:
    st.info("ℹ️ Select a specific state from the sidebar to see comparison with state average")
