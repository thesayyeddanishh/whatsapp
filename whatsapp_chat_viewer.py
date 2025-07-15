import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Page setup
st.set_page_config(layout="wide")
st.title("📱 WhatsApp Chat Viewer")
uploaded_file = st.file_uploader("Upload your WhatsApp chat (.txt)", type="txt")

# Chat line parsing
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
            # Multiline message continuation
            chat_data[-1]["message"] += "\n" + line
    return pd.DataFrame(chat_data)

# Chat bubble styling
def display_message(sender, message, is_user):
    bg_color = "#dcf8c6" if is_user else "#ffffff"
    align = "flex-end" if is_user else "flex-start"
    border_radius = "18px 18px 0px 18px" if is_user else "18px 18px 18px 0px"
    
    st.markdown(f"""
    <div style="display: flex; justify-content: {align}; margin-bottom: 10px;">
        <div style="
            background-color: {bg_color}; 
            padding: 10px 15px; 
            border-radius: {border_radius}; 
            max-width: 70%; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.2); 
            white-space: pre-wrap;
            color: black;
            font-size: 15px;
        ">
            {message}
        </div>
    </div>
    """, unsafe_allow_html=True)

# App logic
if uploaded_file:
    raw_lines = uploaded_file.read().decode("utf-8", errors="ignore").splitlines()
    chat_df = parse_chat(raw_lines)

    if chat_df.empty:
        st.warning("Couldn't parse any messages. Check the format or file.")
    else:
        senders = chat_df["sender"].unique().tolist()
        user_sender = st.sidebar.selectbox("Pick your sender (for right-aligned bubbles):", senders)
        selected_senders = st.sidebar.multiselect("Filter senders to show:", senders, default=senders)

        chat_df = chat_df[chat_df["sender"].isin(selected_senders)]

        st.markdown("---")
        for _, row in chat_df.iterrows():
            display_message(row["sender"], row["message"], row["sender"] == user_sender)
