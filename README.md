# training-calendar-dashboard
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_calendar import calendar
from datetime import datetime
import re

# 1. Page Configuration (Sleek UI Layout)
st.set_page_config(
    page_title="Executive Training Schedule Dashboard",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium cohesive color palette for courses
COLOR_PALETTE = {
    "Advanced Excel": "#36A2EB",      # Deep Electric Blue
    "Coding": "#FF6384",              # Vibrant Coral
    "Advanced Analytics": "#FF9F40",  # Amber Orange
    "DBMS-Projects": "#4BC0C0",       # Emerald Teal
    "Fallback": "#9966FF"             # Modern Purple
}

# 2. Advanced Custom Date Parser for "1st may", "15th may", etc.
def parse_custom_date(date_str, current_year=2026):
    if pd.isna(date_str):
        return None
    
    date_clean = str(date_str).lower().strip()
    
    # Extract only the numbers (e.g., "15th" -> "15")
    day_match = re.search(r'\d+', date_clean)
    day = int(day_match.group()) if day_match else 1
    
    # Identify month
    month = 5  # Default fallback to May
    if "april" in date_clean:
        month = 4
    elif "may" in date_clean:
        month = 5
    elif "june" in date_clean:
        month = 6
        
    return datetime(current_year, month, day)

# 3. Data Ingestion & Transformation Pipeline
@st.cache_data
def load_and_process_data(file_name):
    try:
        # Explicitly read from the primary data sheet
        df = pd.read_excel(file_name, sheet_name="Dataset")
        
        # Strip trailing/leading whitespace from string columns and column headers
        df.columns = df.columns.str.strip()
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].astype(str).str.strip()
            
        # Parse text dates to true standard datetime stamps
        df['Start_DateTime'] = df['Start date'].apply(parse_custom_date)
        df['End_DateTime'] = df['Closing date'].apply(parse_custom_date)
        
        return df
    except Exception as e:
        st.error(f"❌ Blueprint Ingestion Error: Ensure '{file_name}' is placed in your repository root folder.")
        st.stop()

# Load the file directly referencing its name verbatim
FILE_NAME = "Sample _data.xlsx"
df = load_and_process_data(FILE_NAME)

# 4. Interactive Sidebar Filters
st.sidebar.header("🔍 Filter Matrix Configuration")

all_universities = sorted(df['University'].unique())
selected_universities = st.sidebar.multiselect("University / Institution", all_universities, default=all_universities)

all_courses = sorted(df['Courses/ Name of the paper'].unique())
selected_courses = st.sidebar.multiselect("Module / Course Filter", all_courses, default=all_courses)

all_modes = sorted(df['Delivery mode'].unique())
selected_modes = st.sidebar.multiselect("Delivery Format", all_modes, default=all_modes)

# Apply runtime filters
filtered_df = df[
    (df['University'].isin(selected_universities)) &
    (df['Courses/ Name of the paper'].isin(selected_courses)) &
    (df['Delivery mode'].isin(selected_modes))
]

# 5. Header Section & High-Level KPIs
st.title("📅 Enterprise Training Management & Batch Calendar")
st.markdown("---")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.metric(label="Total Cohort Batches", value=int(filtered_df['No. of batches'].sum()))
with kpi_col2:
    st.metric(label="Total Active Enrollees", value=f"{int(filtered_df['No of students'].sum()):,}")
with kpi_col3:
    st.metric(label="Aggregated Delivery Volume", value=f"{int(filtered_df['Delivery hrs'].sum())} Hrs")
with kpi_col4:
    st.metric(label="Trainers Allocated", value=int(filtered_df['Trainers required'].sum()))

st.markdown("---")

# 6. Structuring Events for FullCalendar
calendar_events = []
for index, row in filtered_df.iterrows():
    course = row['Courses/ Name of the paper']
    bg_color = COLOR_PALETTE.get(course, COLOR_PALETTE["Fallback"])
    
    # Check for valid dates
    if pd.isna(row['Start_DateTime']) or pd.isna(row['End_DateTime']):
        continue

    event_entry = {
        "id": f"event_{index}",
        "title": f"[{row['Delivery mode']}] {row['University']} - {course}",
        "start": row['Start_DateTime'].strftime("%Y-%m-%d"),
        "end": (row['End_DateTime'] + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
        "backgroundColor": bg_color,
        "borderColor": bg_color,
        "textColor": "#FFFFFF",
        "extendedProps": {
            "university": row['University'],
            "program": row['Program'],
            "semester": row['Semester'],
            "trainer": row['Mapped Trainers'],
            "hours": row['Delivery hrs'],
            "mode": row['Delivery mode'],
            "students": row['No of students'],
            "style": row['Weekly/ Blocked']
        }
    }
    calendar_events.append(event_entry)

# Config options for FullCalendar wrapper
calendar_options = {
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,listMonth"
    },
    "initialView": "dayGridMonth",
    "navLinks": True,
    "selectable": True,
}

# 7. Render Layout Grid (Calendar View & Detailed Inspection Side-by-Side)
cal_layout, info_layout = st.columns([2.2, 1])

with cal_layout:
    st.subheader("Interactive Schedule Matrix Grid")
    calendar_state = calendar(
        events=calendar_events,
        options=calendar_options,
        custom_css="""
            .fc-event-title { font-weight: 500; font-size: 0.85rem; padding: 2px; }
            .fc-toolbar-title { font-size: 1.3rem !important; font-weight: bold; }
        """,
        key="operational_scheduler"
    )

with info_layout:
    st.subheader("Batch Metadata Inspector")
    
    if calendar_state and "eventClick" in calendar_state:
        click_data = calendar_state["eventClick"]["event"]
        props = click_data.get("extendedProps", {})
        
        st.markdown(f"### 📍 {props.get('university')}")
        st.success(f"**Course Title:** {click_data.get('title').split('] ')[-1]}")
        
        st.markdown(f"""
        * **🎓 Stream Archetype:** {props.get('program')} — {props.get('semester')}
        * **👨‍🏫 Assigned Faculty:** {props.get('trainer')}
        * **💻 Layout Strategy:** Mode: `{props.get('mode')}` ({props.get('style')})
        * **⏱️ Structural Duration:** {props.get('hours')} Hours Assigned
        * **👥 Headcount Load:** {props.get('students')} Confirmed Students
        """)
    else:
        st.info("💡 **Dashboard Guide:** Click directly on any colored strip inside the monthly calendar grid to view detailed batch information here.")

st.markdown("---")

# 8. Advanced Visual Business Intelligence Charts
st.subheader("📊 Operational Analytics Insights")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    fig_pie = px.pie(
        filtered_df, 
        values="No of students", 
        names="Courses/ Name of the paper",
        title="Student Registration Distribution by Topic Domain",
        hole=0.4,
        color="Courses/ Name of the paper",
        color_discrete_map=COLOR_PALETTE
    )
    fig_pie.update_layout(margin=dict(t=40, b=10, l=10, r=10))
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_col2:
    fig_bar = px.bar(
        filtered_df,
        x="University",
        y="Delivery hrs",
        color="Delivery mode",
        title="Total Required Delivery Hours per Institution Matrix",
        barmode="group",
        labels={"Delivery hrs": "Total Hours Specified"}
    )
    fig_bar.update_layout(margin=dict(t=40, b=10, l=10, r=10), xaxis_tickangle=-15)
    st.plotly_chart(fig_bar, use_container_width=True)
