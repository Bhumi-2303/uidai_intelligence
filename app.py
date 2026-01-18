import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ---------------- CONFIGURATION & SETUP ---------------- #

st.set_page_config(
    page_title="UIDAI Analytics Hub",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional UI
def inject_custom_css(theme="☀️ Light"):
    # Theme Definitions
    if "Dark" in theme:
        colors = {
            "bg_color": "#0f172a",
            "text_color": "#e2e8f0",
            "card_bg": "#1e293b",
            "card_border": "#334155",
            "sidebar_bg": "#1e293b",
            "sidebar_text": "#f8fafc",
            "metric_label": "#94a3b8",
            "metric_value": "#f8fafc",
            "metric_delta_bg": "rgba(59, 130, 246, 0.2)",
            "header_shadow": "rgba(0,0,0,0.4)"
        }
    else:
        colors = {
            "bg_color": "#f4f6f9",
            "text_color": "#1e293b",
            "card_bg": "linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)",
            "card_border": "#e1e4e8",
            "sidebar_bg": "#f8fafc",
            "sidebar_text": "#334155",
            "metric_label": "#64748b",
            "metric_value": "#1e293b",
            "metric_delta_bg": "#eff6ff",
            "header_shadow": "rgba(37, 99, 235, 0.2)"
        }

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        /* General Font & Background */
        .stApp {{
            background-color: {colors["bg_color"]};
            font-family: 'Inter', sans-serif;
            color: {colors["text_color"]};
        }}
        
        /* Fix Widget Labels & Text Visibility - Comprehensive */
        label, .stRadio label, .stSelectbox label, .stNumberInput label, .stTextInput label, .stSidebar label {{
            color: {colors["text_color"]} !important;
        }}
        .stRadio div[role="radiogroup"] p {{
            color: {colors["text_color"]} !important;
        }}
        div[data-baseweb="select"] span {{
            color: {colors["text_color"]} !important;
        }}
        div[data-testid="stMarkdownContainer"] p {{
            color: {colors["text_color"]};
        }}
        
        /* Metric Cards */
        div[data-testid="stMetric"] {{
            background: {colors["card_bg"]};
            border: 1px solid {colors["card_border"]};
            padding: 24px;
            border-radius: 12px;
            border-left: 5px solid #3b82f6;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }}
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0, 0, 0, 0.1);
            border-color: #3b82f6;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {colors["metric_label"]};
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        div[data-testid="stMetricValue"] {{
            color: {colors["metric_value"]};
            font-weight: 800;
            font-size: 1.8rem;
        }}
        div[data-testid="stMetricDelta"] {{
            background-color: {colors["metric_delta_bg"]};
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            color: {colors["metric_value"]};
        }}
        
        /* Headers & Titles */
        h1, h2, h3, h4, h5, h6 {{
            color: {colors["text_color"]};
            font-family: 'Inter', sans-serif;
        }}
        h1 {{
            font-weight: 800;
            letter-spacing: -0.5px;
        }}
        .main-header {{
            background: linear-gradient(120deg, #2563eb, #1e40af);
            padding: 3rem 2rem;
            border-radius: 0 0 20px 20px;
            color: white;
            margin-bottom: 2rem;
            margin-top: -6rem;
            box-shadow: 0 4px 20px {colors["header_shadow"]};
        }}
        .main-header h1 {{
            color: white;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        /* Sidebar customization */
        section[data-testid="stSidebar"] {{
            background-color: {colors["sidebar_bg"]};
            color: {colors["sidebar_text"]};
            border-right: 1px solid {colors["card_border"]};
        }}
        section[data-testid="stSidebar"] .block-container {{
            padding-top: 3rem;
        }}
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] .stMarkdown,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label {{
            color: {colors["sidebar_text"]} !important;
        }}
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            background-color: {colors["card_bg"].replace("linear-gradient(135deg, ", "").replace(" 0%, ", "").replace(" 100%)", "").split(",")[0]};
            color: {colors["text_color"]};
            border-color: {colors["card_border"]};
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 20px;
            border-bottom: 1px solid {colors["card_border"]};
            padding-bottom: 10px;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 45px;
            background-color: transparent;
            border: none;
            color: {colors["metric_label"]};
            font-weight: 600;
            padding: 0 20px;
            transition: color 0.2s;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            color: #2563eb;
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: #2563eb;
            border-bottom: 3px solid #2563eb;
            background-color: transparent;
        }}
        
        /* Dataframes & Tables */
        .stDataFrame {{
            border: 1px solid {colors["card_border"]};
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        /* Alerts & Info */
        .stAlert {{
            border-radius: 8px;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        /* Custom Helper Classes */
        .caption-text {{
            color: {colors["metric_label"]};
            font-size: 0.9rem;
        }}
        </style>
    """, unsafe_allow_html=True)


# ---------------- DATA LOADING ---------------- #

@st.cache_data
def load_dashboard_data():
    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / "outputs" / "dashboard" / "dashboard_data.csv"
    try:
        return pd.read_csv(data_path)
    except FileNotFoundError:
        st.error(f"Data file not found at {data_path}. Please check the path.")
        return pd.DataFrame()

df = load_dashboard_data()

# ---------------- HEADER SECTION ---------------- #

# Title Area with Professional Gradient
st.markdown("""
    <div class="main-header">
        <h1>🇮🇳 UIDAI Analytics Hub</h1>
        <p style="font-size: 1.1rem; opacity: 0.9;">Comprehensive District-Level Intelligence & Performance Monitoring System</p>
    </div>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR NAVIGATION ---------------- #

with st.sidebar:
    st.markdown("### 🌗 Theme Settings")
    theme_selection = st.radio("Display Mode", ["☀️ Light", "🌙 Dark"], horizontal=True, label_visibility="collapsed")
    inject_custom_css(theme_selection)
    
    st.markdown("---")
    st.markdown("### 🎛️ Control Panel")
    
    # State Filter
    states = ["All"] + sorted(df["state"].unique().tolist())
    selected_state = st.selectbox("📍 Select State / Region", states)
    
    # Filter Logic
    if selected_state == "All":
        df_view = df.copy()
        st.info("Displaying data for **Pan-India**")
    else:
        df_view = df[df["state"] == selected_state]
        st.success(f"Focused on **{selected_state}**")
        
    st.markdown("---")
    st.markdown("### 📊 Dashboard Settings")
    chart_theme = st.selectbox("Chart Theme", ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"], index=1)
    
    st.markdown("---")
    st.caption(f"Last Updated: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    st.caption("v2.0.0 | Professional Edition")


# ---------------- MAIN CONTENT TABS ---------------- #

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Executive Overview",
    "🔎 Deep Dive Analysis",
    "🛡️ Risk & Compliance",
    "📝 Raw Data Explorer"
])

# =========================================================
# TAB 1: EXECUTIVE OVERVIEW
# =========================================================
with tab1:
    st.markdown("### Key Performance Indicators (KPIs)")
    
    # Top Level Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_recs = df_view[["age_0_5", "age_5_17", "age_18_greater"]].sum().sum()
    total_bio = df_view[["bio_age_5_17", "bio_age_17_"]].sum().sum()
    total_demo = df_view[["demo_age_5_17", "demo_age_17_"]].sum().sum()
    
    with kpi1:
        st.metric("Total Lives Covered", f"{total_recs:,.0f}", delta=f"{df_view['district'].nunique()} Districts")
    with kpi2:
        st.metric("Total Biometric Updates", f"{total_bio:,.0f}", delta_color="off")
    with kpi3:
        st.metric("Total Demographic Updates", f"{total_demo:,.0f}", delta_color="off")
    with kpi4:
        avg_saturation = (total_bio / total_recs * 100) if total_recs > 0 else 0
        st.metric("Avg Bio-Update Saturation", f"{avg_saturation:.1f}%")

    st.markdown("---")
    
    # Main Chart Area
    st.subheader("Regional Performance Analysis")
    
    col_chart_main, col_chart_side = st.columns([2, 1])
    
    with col_chart_main:
        metric_map = {
            "Total Enrollment": "total_enrollment",
            "Enrolment (Age 0–5)": "age_0_5",
            "Enrolment (Age 5–17)": "age_5_17",
            "Enrolment (Age 18+)": "age_18_greater",
            "Biometric Updates": "total_bio",
            "Demographic Updates": "total_demo"
        }
        
        # Helper columns
        df_view['total_enrollment'] = df_view['age_0_5'] + df_view['age_5_17'] + df_view['age_18_greater']
        df_view['total_bio'] = df_view['bio_age_5_17'] + df_view['bio_age_17_']
        df_view['total_demo'] = df_view['demo_age_5_17'] + df_view['demo_age_17_']
        
        metric_label = st.selectbox("Select Metric for Visualization", list(metric_map.keys()))
        metric_col = metric_map[metric_label]
        
        # Aggregated bar chart
        if selected_state == "All":
            # Show top 20 districts if all India
            data_to_plot = df_view.sort_values(metric_col, ascending=False).head(20)
            x_axis = "district"
            color_axis = "state"
            title_text = f"Top 20 Districts - {metric_label}"
        else:
            data_to_plot = df_view.sort_values(metric_col, ascending=False)
            x_axis = "district"
            color_axis = "district"   
            title_text = f"District-wise {metric_label} in {selected_state}"

        fig_main = px.bar(
            data_to_plot,
            x=x_axis,
            y=metric_col,
            color=color_axis,
            template=chart_theme,
            color_discrete_sequence=px.colors.qualitative.Prism,
            title=title_text
        )
        fig_main.update_layout(xaxis_tickangle=-45, showlegend=True, height=500)
        st.plotly_chart(fig_main, width="stretch")

    with col_chart_side:
        st.markdown(f"#### Distribution: {metric_label}")
        fig_pie = px.pie(
            df_view, 
            values=metric_col, 
            names='state' if selected_state == "All" else 'district',
            hole=0.4,
            template=chart_theme
        )
        if selected_state == "All":
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(showlegend=False)
        else:
            fig_pie.update_traces(textposition='inside', textinfo='percent')
            fig_pie.update_layout(showlegend=False)
            
        st.plotly_chart(fig_pie, width="stretch")
        
        st.info("💡 **Insight**: Use the sidebar to filter by State for granular district-level tracking.")

# =========================================================
# TAB 2: DEEP DIVE ANALYSIS
# =========================================================
with tab2:
    # Dynamic Color Logic for Tab 2
    if "Dark" in theme_selection:
        t2_bg = "#1e293b"
        t2_text = "#f8fafc"
        t2_subtext = "#94a3b8"
        t2_border = "#334155"
    else:
        t2_bg = "white"
        t2_text = "#1e293b"
        t2_subtext = "#64748b"
        t2_border = "#e2e8f0"

    # Header Section
    st.markdown(f"""
        <div style="background-color: {t2_bg}; padding: 1.5rem; border-radius: 12px; border: 1px solid {t2_border}; margin-bottom: 2rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <h3 style="margin-top:0; color: {t2_text}; font-family: 'Inter', sans-serif;">🔎 Advanced Data Exploration</h3>
            <p style="color: {t2_subtext}; margin-bottom: 0;">Perform multidimensional analysis to uncover hidden patterns, trends, and outliers in the UIDAI dataset.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_eda_control, col_eda_display = st.columns([1, 3], gap="large")
    
    with col_eda_control:
        st.markdown(f"#### ⚙️ Analysis Specs")
        with st.container():
            # Styled wrapper for controls
            st.markdown(f'<div style="background-color: {t2_bg}; padding: 15px; border-radius: 10px; border: 1px solid {t2_border};">', unsafe_allow_html=True)
            
            analysis_type = st.radio(
                "Select Methodology", 
                ["Univariate Analysis", "Bivariate Analysis", "Multivariate Analysis"],
                captions=["Single variable distribution", "Relationship between two variables", "Complex multi-variable interactions"]
            )
            
            st.markdown("---")
            
            all_numeric_cols = [c for c in df.columns if df[c].dtype in ['int64', 'float64']]
            # Remove IDs or non-metric columns if any
            
            if analysis_type == "Univariate Analysis":
                uni_var = st.selectbox("Target Variable", all_numeric_cols, index=2)
                st.info(f"Analyzing distribution of **{uni_var}**")
                
            elif analysis_type == "Bivariate Analysis":
                bi_x = st.selectbox("X-Axis (Independent)", all_numeric_cols, index=2)
                bi_y = st.selectbox("Y-Axis (Dependent)", all_numeric_cols, index=5)
                st.success(f"Correlating **{bi_y}** vs **{bi_x}**")
                
            else:
                multi_x = st.selectbox("X-Axis", all_numeric_cols, index=3)
                multi_y = st.selectbox("Y-Axis", all_numeric_cols, index=4)
                multi_size = st.selectbox("Bubble Size", all_numeric_cols, index=2)
                multi_color = st.selectbox("Color Segment", ["state"], disabled=True)
                
            st.markdown('</div>', unsafe_allow_html=True)

    with col_eda_display:
        if analysis_type == "Univariate Analysis":
            # Statistics Row
            stats = df_view[uni_var].describe()
            
            st.markdown(f"##### 📊 Statistical Snapshot: {uni_var}")
            s1, s2, s3, s4 = st.columns(4)
            with s1: st.metric("Mean", f"{stats['mean']:,.2f}")
            with s2: st.metric("Median", f"{stats['50%']:,.2f}")
            with s3: st.metric("Std Dev", f"{stats['std']:,.2f}")
            with s4: st.metric("Max", f"{stats['max']:,.0f}")
            
            st.markdown("")
            
            # Charts
            c1, c2 = st.columns(2, gap="medium")
            with c1:
                fig_hist = px.histogram(
                    df_view, x=uni_var, nbins=30, marginal="box", 
                    template=chart_theme, 
                    title=f"Histogram Distribution",
                    color_discrete_sequence=['#3b82f6']
                )
                fig_hist.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_hist, use_container_width=True)
            with c2:
                fig_box = px.box(
                    df_view, x="state" if selected_state=="All" else "district", y=uni_var, 
                    template=chart_theme, 
                    title=f"Box Plot Analysis",
                    color_discrete_sequence=['#ef4444']
                )
                fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_box, use_container_width=True)
                
        elif analysis_type == "Bivariate Analysis":
            # Stats for correlation
            corr_val = df_view[bi_x].corr(df_view[bi_y])
            
            col_stat, col_plot = st.columns([1, 4])
            
            with col_stat:
                st.metric("Correlation", f"{corr_val:.4f}")
                if abs(corr_val) > 0.7:
                    st.success("Strong Relationship")
                elif abs(corr_val) > 0.3:
                    st.warning("Moderate Relationship")
                else:
                    st.info("Weak Relationship")
                    
            with col_plot:
                fig_scat = px.scatter(
                    df_view, x=bi_x, y=bi_y, color="state", 
                    trendline="ols", hover_name="district",
                    template=chart_theme, 
                    title=f"Scatter Analysis: {bi_x} vs {bi_y}",
                    marginal_x="histogram", marginal_y="violin",
                    opacity=0.7
                )
                fig_scat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=500)
                st.plotly_chart(fig_scat, use_container_width=True)
            
        else:
            # Multivariate
            st.markdown("##### 🔬 Dimensionality Analysis")
            fig_bub = px.scatter(
                df_view, x=multi_x, y=multi_y, size=multi_size, color="state",
                hover_name="district", size_max=60, template=chart_theme,
                title=f"Multivariate View: {multi_x} vs {multi_y}",
                opacity=0.8
            )
            fig_bub.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=600)
            st.plotly_chart(fig_bub, use_container_width=True)

# =========================================================
# TAB 3: RISK & COMPLIANCE
# =========================================================
with tab3:
    st.markdown("### 🛡️ Risk Assessment & Action Plan")
    st.caption("Automated risk scoring based on enrollment gaps and update anomalies.")
    
    # ---------------- LOGIC FROM ORIGINAL APP ---------------- #
    def calculate_risk_score(row):
        """Calculate risk score based on enrollment and update metrics"""
        risk_score = 0
        risk_factors = []
        
        # Enrolment Risk
        total_enrolment = row['age_0_5'] + row['age_5_17'] + row['age_18_greater']
        # Note: Using global quantile thresholds for consistency
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

    # Calculate risk table
    df_risk = df_view.copy()
    if not df_risk.empty:
        df_risk[['risk_score', 'risk_factors']] = df_risk.apply(
            lambda row: pd.Series(calculate_risk_score(row)), axis=1
        )
        
        def get_risk_level(score):
            if score >= 70: return "Critical"
            elif score >= 50: return "High"
            elif score >= 30: return "Medium"
            else: return "Low"
            
        df_risk['risk_level'] = df_risk['risk_score'].apply(get_risk_level)
        
        # Risk Dashboard
        r_col1, r_col2 = st.columns([1, 2])
        
        with r_col1:
            st.subheader("Risk Distribution")
            risk_counts = df_risk['risk_level'].value_counts()
            
            # Custom donut chart for risk
            fig_risk = px.pie(
                names=risk_counts.index, 
                values=risk_counts.values, 
                hole=0.6,
                color=risk_counts.index,
                color_discrete_map={
                    "Critical": "#dc3545",
                    "High": "#ffc107",
                    "Medium": "#17a2b8",
                    "Low": "#28a745"
                },
                template=chart_theme
            )
            st.plotly_chart(fig_risk, width="stretch")
            
        with r_col2:
            st.subheader("⚠️ Critical Priority Districts")
            critical_districts = df_risk[df_risk['risk_level'] == 'Critical'].sort_values('risk_score', ascending=False)
            
            if not critical_districts.empty:
                st.dataframe(
                    critical_districts[['district', 'state', 'risk_score', 'risk_factors']],
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.success("No Critical Risk Districts found in this view. Great job!")

        # Recommendations Engine
        st.markdown("### 📋 Intelligent Recommendations")
        
        # Select district for specific recommendations
        selected_risk_district = st.selectbox("Select District for Action Plan", df_risk['district'].unique())
        
        if selected_risk_district:
            d_data = df_risk[df_risk['district'] == selected_risk_district].iloc[0]
            
            st.info(f"Analysis for **{d_data['district']}** (Risk Score: {d_data['risk_score']} - {d_data['risk_level']})")
            
            rec_cols = st.columns(3)
            
            # Action Cards
            with rec_cols[0]:
                st.markdown("**1. Biometric Status**")
                bio_cov = (d_data['bio_age_5_17'] + d_data['bio_age_17_']) / max(d_data['age_5_17'] + d_data['age_18_greater'], 1)
                st.progress(min(bio_cov, 1.0))
                if bio_cov < 0.5:
                    st.error("Action: Initiate Biometric Update Camps immediately.")
                else:
                    st.success("Status: Healthy Coverage.")
            
            with rec_cols[1]:
                st.markdown("**2. Child Enrollment (0-5)**")
                avg_0_5 = df['age_0_5'].mean()
                delta_0_5 = d_data['age_0_5'] - avg_0_5
                st.metric("0-5 Enrolled", f"{d_data['age_0_5']:,}", f"{delta_0_5:,.0f} from Mean")
                if d_data['age_0_5'] < df['age_0_5'].quantile(0.25):
                    st.warning("Action: Partner with local hospitals/Anganwadis.")
            
            with rec_cols[2]:
                st.markdown("**3. Factor Analysis**")
                if d_data['risk_factors']:
                    for f in d_data['risk_factors']:
                        st.write(f"• {f}")
                else:
                    st.write("• No specific risk factors identified.")

# =========================================================
# TAB 4: RAW DATA EXPLORER
# =========================================================
with tab4:
    st.markdown("### 📝 Master Data View")
    
    with st.expander("Filter Options", expanded=False):
        c1, c2 = st.columns(2)
        min_enrollment = c1.number_input("Min Enrollment", 0, 10000000, 0)
        search_district = c2.text_input("Search District Name")
        
    filtered_df = df_view[df_view['age_0_5'] + df_view['age_5_17'] + df_view['age_18_greater'] >= min_enrollment]
    if search_district:
        filtered_df = filtered_df[filtered_df['district'].str.contains(search_district, case=False)]
        
    st.dataframe(filtered_df, use_container_width=True, height=600)
    
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Filtered Data (CSV)",
        csv,
        "uidai_filtered_data.csv",
        "text/csv",
        key='download-csv'
    )
