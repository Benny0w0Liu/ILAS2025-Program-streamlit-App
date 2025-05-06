import streamlit as st
import pandas as pd
import re

st.set_page_config(
    page_title="Speech Information - ILAS2025",
    page_icon="data/favicon.ico",  # Path to your icon file
    layout="wide"
)

# --- Helper: Create URL-safe anchor from TITLE ---
def slugify(title):
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', str(title).lower()).strip('-')
    return slug
def make_clickable(link):
    return f'<a href="{link}">{link[1::]}</a>'
# --- Load Data ---
df = pd.read_csv("data/srp-full.csv")

# Define columns
summary_columns = ["WEEKDAY", "START_STR", "END_STR", "SESSION", "FULL_NAME", "TYPE", "ROOM"]
detail_columns = summary_columns + ["TITLE", "ABSTRACT"]

# Weekday sort order
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekdays_in_data = df['WEEKDAY'].dropna().unique()
weekdays_sorted = [day for day in weekday_order if day in weekdays_in_data]

# Sidebar Navigation
page = st.sidebar.radio("Select Page", [
    "Filter by Weekday & Time", 
    "Filter by Session",
    "Filter by Name"
])
st.title("ILAS2025 Speech Information")

# --- Filtering Logic ---
if page == "Filter by Weekday & Time":    
    selected_weekday = st.sidebar.selectbox("Select Weekday", weekdays_sorted)
    weekday_df = df[df['WEEKDAY'] == selected_weekday]
    show_all_times = st.sidebar.checkbox("Show all times for this weekday", value=True)

    if show_all_times:
        filtered_df = weekday_df
    else:
        times = weekday_df['START_STR'].dropna().unique()
        selected_time = st.sidebar.selectbox("Select Start Time", sorted(times))
        filtered_df = weekday_df[weekday_df['START_STR'] == selected_time]

elif page == "Filter by Session":
    sessions = df['SESSION'].dropna().unique()
    selected_session = st.sidebar.selectbox("Select Session", sorted(sessions))
    filtered_df = df[df['SESSION'] == selected_session]

elif page == "Filter by Name":
    name_query = st.sidebar.text_input("Enter part of a name", "").strip()
    if name_query:
        filtered_df = df[df['FULL_NAME'].str.contains(name_query, case=False, na=False)]
    else:
        st.info("Please enter a name to search.")
        filtered_df = pd.DataFrame(columns=df.columns)

# --- Sort and Generate Anchors ---
filtered_df = filtered_df.sort_values("START_STR").reset_index(drop=True)

# Generate anchor slugs from titles
slugs = {}
anchor_links = []

for title in filtered_df["TITLE"]:
    base_slug = slugify(title)
    slug = base_slug
    count = 1
    while slug in slugs:
        slug = f"{base_slug}-{count}"
        count += 1
    slugs[slug] = True
    anchor_links.append(slug)

filtered_df["ANCHOR"] = anchor_links
show_table = st.checkbox("Show Schedule Overview Table", value=True)

# --- Display Table ---
if not filtered_df.empty:
    if show_table:

        st.subheader("Schedule Overview")
        st.markdown("<div id='schedule-overview'></div>", unsafe_allow_html=True)

        summary_table = filtered_df[summary_columns + ["ANCHOR"]].copy()
        summary_table["ANCHOR"] = summary_table["ANCHOR"].apply(lambda x: f"#{x}")
        summary_table['ANCHOR'] = summary_table['ANCHOR'].apply(make_clickable)
        summary_table = summary_table.rename(columns={
            "WEEKDAY": "Day",
            "START_STR": "Start Time",
            "END_STR": "End Time",
            "SESSION": "Session",
            "FULL_NAME": "Presenter",
            "TYPE": "Type",
            "ROOM": "Room",
            "Link": "Details"
        })

        st.write(summary_table.to_html(escape=False), unsafe_allow_html=True)
        st.markdown("---")
    st.subheader("Detailed Information")

    for _, row in filtered_df.iterrows():
        st.markdown(f"<div id='{row['ANCHOR']}'></div>", unsafe_allow_html=True)
        st.markdown(f"### {row['TITLE']}")
        st.write(f"**Session:** {row['SESSION']}, **Type:** {row['TYPE']}, **Time:** {row['START_STR']}–{row['END_STR']}, **Room:** {row['ROOM']}")
        st.write(f"**Presenter:** {row['FULL_NAME']}")
        st.markdown("**Abstract:**")
        st.markdown(row['ABSTRACT'], unsafe_allow_html=True)
        st.markdown("[🔝](#schedule-overview)")
        st.markdown("---")
else:
    if page != "Filter by Name" or name_query:
        st.warning("No results found.")
