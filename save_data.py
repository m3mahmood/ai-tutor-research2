import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

def get_sheet_connection():
    return st.connection("gsheets", type=GSheetsConnection)

def save_participant_data(participant_id, expertise_group=None, pre_score=None, 
                          sys1_time=None, sys1_practice=None, sys1_post=None, 
                          sys2_time=None, sys2_practice=None, sys2_post=None, 
                          survey_answers=None):
    conn = get_sheet_connection()
    
    # Exact columns from your screenshot
    columns_list = [
        "Participant_ID", "Timestamp", "Expertise_Group", "Pre_Test_Score", 
        "Sys1_Learning_Time", "Sys1_Practice_Score", "Sys1_Post_Test_Score", 
        "Sys2_Learning_Time", "Sys2_Practice_Score", "Sys2_Post_Test_Score", 
        "Questionnaire_Answers"
    ]
    
    # 1. Read existing spreadsheet data
    try:
        df = conn.read(ttl=0)
        df = df.astype(object)
    except Exception:
        df = pd.DataFrame(columns=columns_list)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. Update if participant already exists
    if participant_id in df["Participant_ID"].values:
        idx = df[df["Participant_ID"] == participant_id].index[0]
        
        df.at[idx, "Timestamp"] = current_time
        if expertise_group is not None: df.at[idx, "Expertise_Group"] = expertise_group
        if pre_score is not None: df.at[idx, "Pre_Test_Score"] = pre_score
        if sys1_time is not None: df.at[idx, "Sys1_Learning_Time"] = sys1_time
        if sys1_practice is not None: df.at[idx, "Sys1_Practice_Score"] = sys1_practice
        if sys1_post is not None: df.at[idx, "Sys1_Post_Test_Score"] = sys1_post
        if sys2_time is not None: df.at[idx, "Sys2_Learning_Time"] = sys2_time
        if sys2_practice is not None: df.at[idx, "Sys2_Practice_Score"] = sys2_practice
        if sys2_post is not None: df.at[idx, "Sys2_Post_Test_Score"] = sys2_post
        if survey_answers is not None: df.at[idx, "Questionnaire_Answers"] = str(survey_answers)
    else:
        # 3. Create a brand new row if it's a new participant
        new_row = pd.DataFrame([{
            "Participant_ID": participant_id,
            "Timestamp": current_time,
            "Expertise_Group": expertise_group if expertise_group is not None else "",
            "Pre_Test_Score": pre_score if pre_score is not None else "",
            "Sys1_Learning_Time": sys1_time if sys1_time is not None else "",
            "Sys1_Practice_Score": sys1_practice if sys1_practice is not None else "",
            "Sys1_Post_Test_Score": sys1_post if sys1_post is not None else "",
            "Sys2_Learning_Time": sys2_time if sys2_time is not None else "",
            "Sys2_Practice_Score": sys2_practice if sys2_practice is not None else "",
            "Sys2_Post_Test_Score": sys2_post if sys2_post is not None else "",
            "Questionnaire_Answers": str(survey_answers) if survey_answers is not None else ""
        }]).astype(object)
        df = pd.concat([df, new_row], ignore_index=True)
    
    # 4. Push data straight to your Google Sheet
    conn.update(data=df)