# training-calendar-dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
from datetime import datetime
import re
import io

# 1. Premium Wide Page Layout Configuration
st.set_page_config(
    page_title="Global Training Operations Command Center",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Executive Blue Theme Color Palette Map
# Designed using high-contrast shades of Professional Blue to keep a cohesive corporate aesthetic
BLUE_PALETTE = {
    "Advanced Excel": "#1E3A8A",      # Deep Navy Blue
    "Coding": "#3B82F6",              # Electric Royal Blue
    "Advanced Analytics": "#06B6D4",  # High-Contrast Cyan Blue
    "DBMS-Projects": "#60A5FA",       # Light Sky Blue
    "Fallback": "#2563EB"             # Classic Blue Accent
}

# 3. Resilient Advanced Date Parser (Ensures NO rows are dropped due to blank cells)
def parse_resilient_date(date_str, fallback_day=1, default_month=5, default_year=2024):
    if pd.isna(date_str) or str(date_str).strip() == "" or str(date_str).lower().strip() == "nan":
        # Critical Fallback: If closing date is missing, auto-extend to end of month so it stays visible
        return datetime(default_year, default_month, 31)
        
    clean_str = str(date_str).lower().strip()
    
    # Extract only numbers from strings like "1st", "15th", "26th"
    day_digits = re.search(r'\d+', clean_str)
    day = int(day_digits.group()) if day_digits else fallback_day
    
    # Map months to numbers safely
    month = default_month
    if "april" in clean_str: month = 4
    elif "may" in clean_str: month = 5
    elif "june" in clean_str: month = 6
    
    return datetime(default_year, month, day)

# 4. Master Data Ingestion Pipeline (Reads directly from Excel)
@st.cache_data
def process_master_dataset():
    # Looks for both raw Excel or pre-extracted formats to maximize uptime compatibility
    target_files = ["Sample _data.xlsx", "Sample _data.xlsx - Dataset.csv"]
    df = None
    
    for f_name in target_files:
        try:
            if f_name.endswith('.csv'):
                df = pd.read_csv(f_name)
            else:
                # Target the exact data sheet named 'Dataset' in your uploaded file
                df = pd.read_excel(f_name, sheet_name="Dataset")
            break
        except:
            continue
            
    if df is None:
        st.error("❌ Data Engine Failure: Ensure your 'Sample _data.xlsx' spreadsheet is saved right beside your script file.")
        st.stop()
        
    # Standardize column headers and text values by stripping spaces
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].fillna("Not Assigned").astype(str).str.strip()
        
    # Clean and parse metrics securely
    df['No of students'] = pd.to_numeric(df['No of students'], errors='coerce').fillna(0).astype(int)
    df['Delivery hrs'] = pd.to_numeric(df['Delivery hrs'], errors='coerce').fillna(0).astype(int)
    df['No. of batches'] = pd.to_numeric(df['No. of batches'], errors='coerce').fillna(0).astype(int)
    df['Trainers required'] = pd.to_numeric(df['Trainers required'], errors='coerce').fillna(0).astype(int)

    # Convert inconsistent string dates to standardized timestamps
    df['Start_Parsed'] = df['Start date'].apply(lambda x: parse_resilient_date(x, fallback_day=1))
    df['End_Parsed'] = df['Closing date'].apply(lambda x: parse_resilient_date(x, fallback_day=31))
    
    # Boundary guard: prevent end dates from falling chronologically before start dates
    df.loc[df['End_Parsed'] < df['Start_Parsed'], 'End_Parsed'] = df['Start_Parsed'] + pd.Timedelta(days=7)
    
    return df

df = process_master_dataset()

# 5. Advanced Sidebar Filter Matrix Configuration
st.sidebar.title("💠 Operations Matrix Filters")
st.sidebar.markdown("Refine your dashboard data views globally:")

universities = sorted(df['University'].unique())
selected_uni = st.sidebar.multiselect("🏫 Focus Institutions", universities, default=universities)

papers = sorted(df['Courses/ Name of the paper'].unique())
selected_papers = st.sidebar.multiselect("📚 Course Modules", papers, default=papers)

modes = sorted(df['Delivery mode'].unique())
selected_modes = st.sidebar.multiselect("💻 Modality Format", modes, default=modes)

# Execute global structural query filter across all views
filtered_df = df[
    (df['University'].isin(selected_uni)) &
    (df['Courses/ Name of the paper'].isin(selected_papers)) &
    (df['Delivery mode'].isin(selected_modes))
]

# 6. Main Dashboard Architecture Header & Enterprise KPIs
st.title("💠 Blue-Theme Enterprise Training Management Hub")
st.markdown("A premium, resilient executive scheduler offering automated date repairs, trainer booking conflict validation, and export tooling.")

# KPIs structured natively for optimal dashboard presentation
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="📦 Active Cohort Batches", value=int(filtered_df["No. of batches"].sum()))
with m2:
    st.metric(label="👥 Registered Trainees", value=f"{int(filtered_df['No of students'].sum()):,}")
with m3:
    st.metric(label="⏱️ Total Delivery Volume", value=f"{int(filtered_df['Delivery hrs'].sum())} Hrs")
with m4:
    st.metric(label="👨‍🏫 Allocated Trainer Spots", value=int(filtered_df['Trainers required'].sum()))

st.markdown("---")

# 7. Advanced Tabular Workspace (Core App Components)
tab_calendar, tab_analytics, tab_conflicts, tab_export = st.tabs([
    "📅 Blue Calendar Grid Matrix", 
    "📊 Advanced Visual Analytics", 
    "⚠️ Trainer Conflict Checker", 
    "📥 Data Export Toolkit"
])

with tab_calendar:
    # Build events JSON configuration dynamically
    calendar_events = []
    for idx, row in filtered_df.iterrows():
        course_title = row['Courses/ Name of the paper']
        hex_blue = BLUE_PALETTE.get(course_title, BLUE_PALETTE["Fallback"])
        
        calendar_events.append({
            "id": f"evt_{idx}",
            "title": f"[{row['Delivery mode']}] {row['University']} - {course_title}",
            "start": row['Start_Parsed'].strftime("%Y-%m-%d"),
            "end": (row['End_Parsed'] + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            "backgroundColor": hex_blue,
            "borderColor": hex_blue,
            "textColor": "#FFFFFF",
            "extendedProps": {
                "uni": row['University'], "prog": row['Program'], "sem": row['Semester'],
                "trainer": row['Mapped Trainers'], "hrs": row['Delivery hrs'], "students": row['No of students'],
                "style": row['Weekly/ Blocked']
            }
        })

    cal_col, side_inspect = st.columns([2.3, 1])
    with cal_col:
        cal_ui = calendar(
            events=calendar_events,
            options={
                "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridWeek,listMonth"},
                "initialView": "dayGridMonth",
                "navLinks": True,
                "selectable": True,
                "height": 650
            },
            key="blue_theme_scheduler"
        )
        
    with side_inspect:
        st.subheader("📋 Session Metadata Profile")
        if cal_ui and "eventClick" in cal_ui:
            metadata = cal_ui["eventClick"]["event"]["extendedProps"]
            
            with st.container(border=True):
                st.markdown(f"### 📍 {metadata.get('uni')}")
                st.write(f"**📚 Course Module:** {cal_ui['eventClick']['event']['title'].split('] ')[-1]}")
                st.divider()
                st.write(f"**🎓 Program Path:** {metadata.get('prog')} — {metadata.get('sem')}")
                st.write(f"**👨‍🏫 Assigned Faculty:** {metadata.get('trainer')}")
                st.write(f"**💻 Modality Setup:** {metadata.get('mode')} ({metadata.get('style')})")
                st.write(f"**⏱️ Allocation Length:** {metadata.get('hrs')} Lecture Hours")
                st.write(f"**👥 Group Capacity:** {metadata.get('students')} Confirmed Enrollees")
        else:
            st.info("💡 **Interactive Framework Hint:** Click any blue schedule block inside the calendar grid to populate its granular cohort profile immediately here.")

with tab_analytics:
    st.subheader("📊 Operational Intelligence Dashboard Panels")
    if not filtered_df.empty:
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Blue themed Pie/Donut Chart showing Student Volume Distribution
            fig_pie = px.pie(
                filtered_df, 
                values="No of students", 
                names="Courses/ Name of the paper",
                title="Trainee Volume Distribution across Topic Columns",
                hole=0.4,
                color="Courses/ Name of the paper",
                color_discrete_map=BLUE_PALETTE
            )
            fig_pie.update_layout(margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with chart_col2:
            # Blue themed Stacked Bar Chart for University Delivery Breakdown
            fig_bar = px.bar(
                filtered_df,
                x="University",
                y="Delivery hrs",
                color="Courses/ Name of the paper",
                title="Operational Hours Imposed per Institution Matched",
                color_discrete_map=BLUE_PALETTE,
                labels={"Delivery hrs": "Allocated Work Hours"}
            )
            fig_bar.update_layout(margin=dict(t=40, b=10, l=10, r=10), xaxis_tickangle=-20)
            st.plotly_chart(fig_bar, use_container_width=True)
            
        # Linear Timeline Gantt view embedded at bottom of analytics for clean visibility
        st.markdown("<br><b>🏭 Operational Resource Allocation Roadmap View</b>", unsafe_with_html=True)
        fig_gantt = px.timeline(
            filtered_df, 
            x_start="Start_Parsed", 
            x_end="End_Parsed", 
            y="University", 
            color="Courses/ Name of the paper",
            color_discrete_map=BLUE_PALETTE,
            hover_data=["Program", "Mapped Trainers"]
        )
        fig_gantt.update_yaxes(autorange="reversed")
        fig_gantt.update_layout(height=350, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_gantt, use_container_width=True)
    else:
        st.warning("No data points meet your current filter configuration inputs.")

with tab_conflicts:
    st.subheader("⚠️ Automated Trainer Schedule Overlap Detector")
    st.markdown("This tool cross-references dates to flags instances where a single trainer is booked for multiple parallel batches simultaneously.")
    
    conflicts_found = False
    trainers_list = filtered_df['Mapped Trainers'].unique()
    
    for trainer in trainers_list:
        if trainer == "Not Assigned" or "," in trainer or "and" in trainer.lower():
            continue  # Skip unassigned slots or shared team delivery entries
            
        trainer_df = filtered_df[filtered_df['Mapped Trainers'] == trainer].sort_values(by='Start_Parsed')
        if len(trainer_df) > 1:
            for i in range(len(trainer_df) - 1):
                current_row = trainer_df.iloc[i]
                next_row = trainer_df.iloc[i+1]
                
                # Check for calendar
