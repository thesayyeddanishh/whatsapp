import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Page setup
st.set_page_config(layout="wide")
st.title("📱 WhatsApp Chat Viewer")

uploaded_file = st.file_uploader("Upload your WhatsApp chat (.txt)", type="txt")

# Parsing function
def parse_chat(lines):
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2})\s?(am|pm)? - (.*?): (.*)'
    chat_data = []

    for line in lines:
        line = line.strip()
        match = re.match(pattern, line, flags=re.IGNORECASE)
        if match:
            date, time, ampm, sender, message = match.groups()
            time_str = f"{time} {ampm}" if ampm else time
            try:
                timestamp = datetime.strptime(f"{date} {time_str}", "%d/%m/%y %I:%M %p")
            except:
                try:
                    timestamp = datetime.strptime(f"{date} {time_str}", "%d/%m/%y %H:%M")
                except:
                    continue
            chat_data.append({
                "timestamp": timestamp,
                "sender": sender.strip(),
                "message": message.strip()
            })
        elif chat_data:
            chat_data[-1]["message"] += "\n" + line

    return pd.DataFrame(chat_data)

# Chat bubble styling
def display_message(sender, message, timestamp, is_user):
    bg_color = "#dcf8c6" if is_user else "#ffffff"
    align = "flex-end" if is_user else "flex-start"
    border_radius = "1px 1px 1px 1px" if is_user else "12px 12px 12px 0px"
    time_str = timestamp.strftime("%I:%M %p").lstrip("0")

    st.markdown(f"""
    <div style="display: flex; justify-content: {align}; margin: 1px 0;">
        <div style="
            background-color: {bg_color}; 
            padding: 6px 1px 4px 1px; 
            border-radius: {border_radius}; 
            max-width: 60%; 
            box-shadow: 0 1px 1px rgba(0,0,0,0.1); 
            white-space: pre-wrap;
            color: #111;
            font-size: 13px;
            line-height: 1.25;
        ">
            <div style="margin: 0;">{message}</div>
            <div style="
                font-size: 10px; 
                color: #888; 
                text-align: right;
                margin-top: 2px;
            ">{time_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main app
if uploaded_file:
    raw_lines = uploaded_file.read().decode("utf-8", errors="ignore").splitlines()
    chat_df = parse_chat(raw_lines)

    if chat_df.empty:
        st.warning("Couldn't parse any messages. Check the format.")
    else:
        chat_df['date'] = chat_df['timestamp'].dt.date

        # Sidebar filters
        senders = chat_df["sender"].unique().tolist()
        user_sender = st.sidebar.selectbox("🔘 Choose your name:", senders)
        selected_senders = st.sidebar.multiselect("👥 Show messages from:", senders, default=senders)

        # Date range
        min_date, max_date = chat_df["date"].min(), chat_df["date"].max()
        date_range = st.sidebar.date_input("📅 Date Range", (min_date, max_date))
        if isinstance(date_range, tuple):
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range

        # Search keyword
        search_query = st.sidebar.text_input("🔍 Search keyword")

        # Filter data
        filtered_df = chat_df[
            (chat_df["sender"].isin(selected_senders)) &
            (chat_df["date"] >= start_date) &
            (chat_df["date"] <= end_date)
        ]
        if search_query:
            filtered_df = filtered_df[filtered_df["message"].str.contains(search_query, case=False)]

        st.markdown("---")
        for _, row in filtered_df.iterrows():
            display_message(row["sender"], row["message"], row["timestamp"], row["sender"] == user_sender)
