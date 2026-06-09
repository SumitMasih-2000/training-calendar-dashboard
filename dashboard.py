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
BLUE_PALETTE = {
    "Advanced Excel": "#1E3A8A",      # Deep Navy Blue
    "Coding": "#3B82F6",              # Electric Royal Blue
    "Advanced Analytics": "#06B6D4",  # High-Contrast Cyan Blue
    "DBMS-Projects": "#60A5FA",       # Light Sky Blue
    "Fallback": "#2563EB"             # Classic Blue Accent
}

# 3. Resilient Advanced Date Parser
def parse_resilient_date(date_str, fallback_day=1, default_month=5, default_year=2024):
    if pd.isna(date_str) or str(date_str).strip() == "" or str(date_str).lower().strip() == "nan":
        return datetime(default_year, default_month, 31)
        
    clean_str = str(date_str).lower().strip()
    day_digits = re.search(r'\d+', clean_str)
    day = int(day_digits.group()) if day_digits else fallback_day
    
    month = default_month
    if "april" in clean_str: month = 4
    elif "may" in clean_str: month = 5
    elif "june" in clean_str: month = 6
    
    return datetime(default_year, month, day)

# 4. Master Data Ingestion Pipeline
@st.cache_data
def process_master_dataset():
    target_files = ["Sample _data.xlsx", "Sample _data.xlsx - Dataset.csv"]
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
        st.error("❌ Data Engine Failure: Ensure your 'Sample _data.xlsx' spreadsheet is saved right beside your script file.")
        st.stop()
        
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].fillna("Not Assigned").astype(str).str.strip()
        
    df['No of students'] = pd.to_numeric(df['No of students'], errors='coerce').fillna(0).astype(int)
    df['Delivery hrs'] = pd.to_numeric(df['Delivery hrs'], errors='coerce').fillna(0).astype(int)
    df['No. of batches'] = pd.to_numeric(df['No. of batches'], errors='coerce').fillna(0).astype(int)
    df['Trainers required'] = pd.to_numeric(df['Trainers required'], errors='coerce').fillna(0).astype(int)

    df['Start_Parsed'] = df['Start date'].apply(lambda x: parse_resilient_date(x, fallback_day=1))
    df['End_Parsed'] = df['Closing date'].apply(lambda x: parse_resilient_date(x, fallback_day=31))
    
    df.loc[df['End_Parsed'] < df['Start_Parsed'], 'End_Parsed'] = df['Start_Parsed'] + pd.Timedelta(days=7)
    
    return df

df = process_master_dataset()

# 5. Advanced Sidebar Filter Matrix Configuration
st.sidebar.title("💠 Operations Matrix Filters")
st.sidebar.markdown("Refine your dashboard data views globally:")

# CHANGE: Converted University filter into an easy-to-operate drop-down list
universities_options = ["All Universities"] + sorted(list(df['University'].unique()))
selected_uni = st.sidebar.selectbox("🏫 Focus Institution", universities_options, index=0)

papers = sorted(df['Courses/ Name of the paper'].unique())
selected_papers = st.sidebar.multiselect("📚 Course Modules", papers, default=papers)

modes = sorted(df['Delivery mode'].unique())
selected_modes = st.sidebar.multiselect("💻 Modality Format", modes, default=modes)

# Execute global structural query filter with the dropdown choice accounted for
if selected_uni == "All Universities":
    uni_mask = df['University'].isin(df['University'].unique())
else:
    uni_mask = df['University'] == selected_uni

filtered_df = df[
    uni_mask &
    (df['Courses/ Name of the paper'].isin(selected_papers)) &
    (df['Delivery mode'].isin(selected_modes))
]

# 6. Main Dashboard Architecture Header & Enterprise KPIs
st.title("💠 Blue-Theme Enterprise Training Management Hub")
st.markdown("A premium, resilient executive scheduler offering automated date repairs, trainer booking conflict validation, and export tooling.")

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

# 7. Advanced Tabular Workspace
tab_calendar, tab_analytics, tab_conflicts, tab_export = st.tabs([
    "📅 Blue Calendar Grid Matrix", 
    "📊 Advanced Visual Analytics", 
    "⚠️ Trainer Conflict Checker", 
    "📥 Data Export Toolkit"
])

with tab_calendar:
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
                "style": row['Weekly/ Blocked'], "mode": row['Delivery mode'] # Fixed missing item
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
    st.markdown("This tool cross-references dates to flag instances where a single trainer is booked for multiple parallel batches simultaneously.")
    
    conflicts_found = False
    trainers_list = filtered_df['Mapped Trainers'].unique()
    
    for trainer in trainers_list:
        if trainer == "Not Assigned" or "," in trainer or "and" in trainer.lower():
            continue  
            
        trainer_df = filtered_df[filtered_df['Mapped Trainers'] == trainer].sort_values(by='Start_Parsed')
        if len(trainer_df) > 1:
            for i in range(len(trainer_df) - 1):
                current_row = trainer_df.iloc[i]
                next_row = trainer_df.iloc[i+1]
                
                # Check for calendar overlap overlaps
                if current_row['End_Parsed'] >= next_row['Start_Parsed']:
                    conflicts_found = True
                    st.error(f"⚠️ **Schedule Overlap Detected for {trainer}:**")
                    st.write(f"- **Batch 1:** {current_row['University']} - {current_row['Courses/ Name of the paper']} ({current_row['Start_Parsed'].strftime('%d %b')} to {current_row['End_Parsed'].strftime('%d %b')})")
                    st.write(f"- **Batch 2:** {next_row['University']} - {next_row['Courses/ Name of the paper']} ({next_row['Start_Parsed'].strftime('%d %b')} to {next_row['End_Parsed'].strftime('%d %b')})")
                    st.divider()
                    
    if not conflicts_found:
        st.success("✅ Clean Slate: No trainer scheduling overlaps found with current selection settings.")

with tab_export:
    st.subheader("📥 Data Export Toolkit")
    st.markdown("Download your currently filtered dataset as a standard CSV archive file.")
    
    if not filtered_df.empty:
        csv_buffer = io.StringIO()
        # Drop parsed structural columns for clean export file
        export_df = filtered_df.drop(columns=['Start_Parsed', 'End_Parsed'], errors='ignore')
        export_df.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode('utf-8')
        
        st.download_button(
            label="📥 Download Filtered Data Matrix as CSV",
            data=csv_bytes,
            file_name=f"training_schedule_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No data available to generate export file.")
