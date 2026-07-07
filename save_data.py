import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Columns exactly matching your Google Sheet screenshot
COLUMNS_LIST = [
    "Participant_ID", "Timestamp", "Expertise_Group", "Pre_Test_Score", 
    "Sys1_Learning_Time", "Sys1_Practice_Score", "Sys1_Post_Test_Score", 
    "Sys2_Learning_Time", "Sys2_Practice_Score", "Sys2_Post_Test_Score", 
    "Questionnaire_Answers"
]

def init_db():
    """Keeps app.py happy on initialization."""
    pass

def get_dataframe(conn):
    """Helper function to read the sheet safely."""
    try:
        df = conn.read(ttl=0)
        df = df.astype(object)
        # Ensure all columns exist
        for col in COLUMNS_LIST:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS_LIST)

# 1. Stage 3: Participant ID Screen
def add_participant(participant_id):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = get_dataframe(conn)
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if participant_id not in df["Participant_ID"].values:
        new_row = pd.DataFrame([{col: "" for col in COLUMNS_LIST}]).astype(object)
        new_row.at[0, "Participant_ID"] = participant_id
        new_row.at[0, "Timestamp"] = current_time
        df = pd.concat([df, new_row], ignore_index=True)
        conn.update(data=df)

# 2. Stage 4: Pre-Test Completion Screen
def update_pretest(participant_id, pre_score, group):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = get_dataframe(conn)
    
    if participant_id in df["Participant_ID"].values:
        idx = df[df["Participant_ID"] == participant_id].index[0]
        df.at[idx, "Pre_Test_Score"] = pre_score
        df.at[idx, "Expertise_Group"] = group
        df.at[idx, "Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.update(data=df)

# 3. Stage 7: System 1 (Non-Adaptive) Post-Test Screen
def update_nonadaptive(participant_id, learning_time, practice_score, post_score):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = get_dataframe(conn)
    
    if participant_id in df["Participant_ID"].values:
        idx = df[df["Participant_ID"] == participant_id].index[0]
        df.at[idx, "Sys1_Learning_Time"] = learning_time
        df.at[idx, "Sys1_Practice_Score"] = practice_score
        df.at[idx, "Sys1_Post_Test_Score"] = post_score
        df.at[idx, "Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.update(data=df)

# 4. Stage 10: System 2 (Adaptive) Post-Test Screen
def update_adaptive(participant_id, learning_time, practice_score, post_score):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = get_dataframe(conn)
    
    if participant_id in df["Participant_ID"].values:
        idx = df[df["Participant_ID"] == participant_id].index[0]
        df.at[idx, "Sys2_Learning_Time"] = learning_time
        df.at[idx, "Sys2_Practice_Score"] = practice_score
        df.at[idx, "Sys2_Post_Test_Score"] = post_score
        df.at[idx, "Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.update(data=df)

# 5. Stage 11: Final Survey Questionnaire Screen
def save_questionnaire(participant_id, questionnaire_answers):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = get_dataframe(conn)
    
    if participant_id in df["Participant_ID"].values:
        idx = df[df["Participant_ID"] == participant_id].index[0]
        df.at[idx, "Questionnaire_Answers"] = str(questionnaire_answers)
        df.at[idx, "Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.update(data=df)