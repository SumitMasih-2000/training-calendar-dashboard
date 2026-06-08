# training-calendar-dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
from datetime import datetime
import re

# 1. Premium Wide Layout Configuration
st.set_page_config(
    page_title="Executive Training Matrix Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Sophisticated High-Contrast Luxury Corporate Color Scheme
COLOR_PALETTE = {
    "Advanced Excel": "#0284C7",      # Sleek Sapphire Blue
    "Coding": "#EF4444",              # High-Visibility Ruby Crimson
    "Advanced Analytics": "#F59E0B",  # Vibrant Deep Amber/Orange
    "DBMS-Projects": "#10B981",       # Emerald Green Matrix
    "Fallback": "#6366F1"             # Cyber Indigo
}

# 3. Resilient Advanced Date Parser (Fixes all missing rows automatically)
def parse_resilient_date(date_str, fallback_day=1, default_month=5, default_year=2024):
    if pd.isna(date_str) or str(date_str).strip() == "" or str(date_str).lower().strip() == "nan":
        # Critical Fix: Instead of discarding rows with missing closing dates, auto-generate a valid calendar window
        return datetime(default_year, default_month, 31)
        
    clean_str = str(date_str).lower().strip()
    
    # Extract day integer digits
    day_digits = re.search(r'\d+', clean_str)
    day = int(day_digits.group()) if day_digits else fallback_day
    
    # Extract month
    month = default_month
    if "april" in clean_str: month = 4
    elif "may" in clean_str: month = 5
    elif "june" in clean_str: month = 6
    
    return datetime(default_year, month, day)

# 4. Clean Data Ingestion Pipeline
@st.cache_data
def process_full_dataset():
    # Attempt loading via fallback file options
    target_files = ["Sample _data.xlsx - Dataset.csv", "Sample _data.xlsx"]
    df = None
    
    for f_name in target_files:
        try:
            if f_name.endswith('.csv'):
                df = pd.read_csv(f_name)
            else:
                df = pd.read_excel(f_name, sheet_name="Dataset")
            break
        except:
            continue
            
    if df is None:
        st.error("❌ Data File Error: Please make sure your data spreadsheet file is uploaded right beside your script.")
        st.stop()
        
    df.columns = df.columns.str.strip()
    
    # Standardize textual data columns
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip()
        
    # Apply date repairs across all rows safely
    df['Start_Parsed'] = df['Start date'].apply(lambda x: parse_resilient_date(x, fallback_day=1))
    df['End_Parsed'] = df['Closing date'].apply(lambda x: parse_resilient_date(x, fallback_day=31))
    
    # Safeguard window bounds
    df.loc[df['End_Parsed'] < df['Start_Parsed'], 'End_Parsed'] = df['Start_Parsed'] + pd.Timedelta(days=7)
    
    return df

df = process_full_dataset()

# 5. Interactive Strategic Filter Hub on Sidebar
st.sidebar.title("⚡ Operational Control Hub")
st.sidebar.markdown("Customize your interactive views:")

universities = sorted(df['University'].unique())
selected_uni = st.sidebar.multiselect("🏫 Focus Institutions", universities, default=universities)

papers = sorted(df['Courses/ Name of the paper'].unique())
selected_papers = st.sidebar.multiselect("📚 Subject Modules", papers, default=papers)

modes = sorted(df['Delivery mode'].unique())
selected_modes = st.sidebar.multiselect("💻 Execution Formats", modes, default=modes)

# Execute filtering criteria
filtered_df = df[
    (df['University'].isin(selected_uni)) &
    (df['Courses/ Name of the paper'].isin(selected_papers)) &
    (df['Delivery mode'].isin(selected_modes))
]

# 6. Core Dashboard Title Metrics
st.title("⚡ Enterprise Training Operations Control Tower")
st.markdown("A premium performance scheduling app with clean tracking calendars and immediate metric lookup tools.")

# Using safe native UI components instead of unsafe markdown strings
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="📦 Total Active Batches", value=int(filtered_df["No. of batches"].sum()))
with m2:
    st.metric(label="👥 Managed Trainees", value=f"{int(filtered_df['No of students'].sum()):,}")
with m3:
    st.metric(label="⏱️ Operational Hours", value=f"{int(filtered_df['Delivery hrs'].sum())} Hrs")
with m4:
    st.metric(label="👨‍🏫 Trainer Headcount", value=int(filtered_df['Trainers required'].sum()))

st.markdown("---")

# 7. Tabular Workspace Views
tab_calendar, tab_timeline, tab_search = st.tabs(["📅 Interactive Matrix Calendar", "📊 Production Gantt Timeline", "🔍 Instant Search Engine"])

with tab_calendar:
    # Compile Events JSON Config for Calendar Core
    calendar_events = []
    for idx, row in filtered_df.iterrows():
        course_title = row['Courses/ Name of the paper']
        hex_color = COLOR_PALETTE.get(course_title, COLOR_PALETTE["Fallback"])
        
        calendar_events.append({
            "id": f"evt_{idx}",
            "title": f"[{row['Delivery mode']}] {row['University']} - {course_title}",
            "start": row['Start_Parsed'].strftime("%Y-%m-%d"),
            "end": (row['End_Parsed'] + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
            "backgroundColor": hex_color,
            "borderColor": hex_color,
            "textColor": "#FFFFFF",
            "extendedProps": {
                "uni": row['University'], "prog": row['Program'], "sem": row['Semester'],
                "trainer": row['Mapped Trainers'], "hrs": row['Delivery hrs'], "students": row['No of students']
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
            key="premium_grid_calendar"
        )
        
    with side_inspect:
        st.subheader("📋 Session Metadata")
        if cal_ui and "eventClick" in cal_ui:
            metadata = cal_ui["eventClick"]["event"]["extendedProps"]
            
            with st.container(border=True):
                st.success(f"### {metadata.get('uni')}")
                st.write(f"**🎓 Program:** {metadata.get('prog')} ({metadata.get('sem')})")
                st.write(f"**👨‍🏫 Assigned Faculty:** {metadata.get('trainer')}")
                st.write(f"**⏱️ Duration:** {metadata.get('hrs')} Lecture Hours")
                st.write(f"**👥 Capacity:** {metadata.get('students')} Active Enrollees")
        else:
            st.info("💡 **Interactive Framework:** Click directly on any colored schedule block in the main monthly grid layout to pull its comprehensive details here instantly.")

with tab_timeline:
    st.subheader("🏭 Chronological Program Progression Roadmap")
    if not filtered_df.empty:
        fig_gantt = px.timeline(
            filtered_df, 
            x_start="Start_Parsed", 
            x_end="End_Parsed", 
            y="University", 
            color="Courses/ Name of the paper",
            hover_data=["Program", "Semester", "Mapped Trainers"],
            color_discrete_map=COLOR_PALETTE,
        )
        fig_gantt.update_yaxes(autorange="reversed")
        fig_gantt.update_layout(height=450, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_gantt, use_container_width=True)

with tab_search:
    st.subheader("🎯 Live Search Engine Lookup")
    user_search = st.text_input("Type any Trainer Name, University, or Course Module to scan table items instantly:")
    if user_search:
        search_mask = filtered_df.astype(str).apply(lambda x: x.str.contains(user_search, case=False)).any(axis=1)
        st.dataframe(filtered_df[search_mask], use_container_width=True)
    else:
        st.dataframe(filtered_df, use_container_width=True)
