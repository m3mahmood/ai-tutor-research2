import os
import pandas as pd
from datetime import datetime

# File paths for your research data
PARTICIPANTS_FILE = "participants.xlsx"
INTERACTION_LOG_FILE = "experimental_results.xlsx"

def init_db():
    """
    Initializes the Excel database structure if it does not exist.
    Creates a master tracking spreadsheet with strict string dtypes.
    """
    if not os.path.exists(PARTICIPANTS_FILE):
        columns = [
            "Participant_ID", "Timestamp", "Expertise_Group", "Pre_Test_Score",
            "Sys1_Learning_Time", "Sys1_Practice_Score", "Sys1_Post_Test_Score",
            "Sys2_Learning_Time", "Sys2_Practice_Score", "Sys2_Post_Test_Score",
            "Questionnaire_Answers"
        ]
        df = pd.DataFrame(columns=columns)
        df.to_excel(PARTICIPANTS_FILE, index=False)

def add_participant(participant_id):
    """Initializes a new row for a participant when they enter their ID."""
    init_db()  # Safety check
    
    # Force read to see tracking fields as objects/strings
    df = pd.read_excel(PARTICIPANTS_FILE)
    
    # Check if participant already exists to prevent duplicate rows
    if str(participant_id) in df["Participant_ID"].astype(str).values:
        return
        
    # Use empty strings "" for text fields instead of None to force string dtype
    new_row = {
        "Participant_ID": str(participant_id),
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Expertise_Group": "",  # Force string/object type immediately
        "Pre_Test_Score": None,
        "Sys1_Learning_Time": None,
        "Sys1_Practice_Score": None,
        "Sys1_Post_Test_Score": None,
        "Sys2_Learning_Time": None,
        "Sys2_Practice_Score": None,
        "Sys2_Post_Test_Score": None,
        "Questionnaire_Answers": ""  # Force string/object type immediately
    }
    
    df_new = pd.DataFrame([new_row])
    df_combined = pd.concat([df, df_new], ignore_index=True)
    df_combined.to_excel(PARTICIPANTS_FILE, index=False)

def update_pretest(participant_id, score, group):
    """Updates the pre-test results and initial classification."""
    df = pd.read_excel(PARTICIPANTS_FILE, dtype={"Participant_ID": str, "Expertise_Group": str})
    
    # Force text columns to string format to override any auto float64 conversion
    df["Participant_ID"] = df["Participant_ID"].astype(str)
    df["Expertise_Group"] = df["Expertise_Group"].astype(str)
    
    # Convert incoming participant_id to string to guarantee a clean match
    pid_str = str(participant_id)
    
    # Update row cleanly
    df.loc[df["Participant_ID"] == pid_str, "Pre_Test_Score"] = score
    df.loc[df["Participant_ID"] == pid_str, "Expertise_Group"] = str(group)
    
    df.to_excel(PARTICIPANTS_FILE, index=False)

def update_nonadaptive(participant_id, learning_time, practice_score, post_score):
    """Updates tracking metrics for System 1 (Non-Adaptive)."""
    df = pd.read_excel(PARTICIPANTS_FILE, dtype={"Participant_ID": str})
    pid_str = str(participant_id)
    
    df.loc[df["Participant_ID"] == pid_str, "Sys1_Learning_Time"] = learning_time
    df.loc[df["Participant_ID"] == pid_str, "Sys1_Practice_Score"] = practice_score
    df.loc[df["Participant_ID"] == pid_str, "Sys1_Post_Test_Score"] = post_score
    df.to_excel(PARTICIPANTS_FILE, index=False)

def update_adaptive(participant_id, learning_time, practice_score, post_score):
    """Updates tracking metrics for System 2 (Adaptive)."""
    df = pd.read_excel(PARTICIPANTS_FILE, dtype={"Participant_ID": str})
    pid_str = str(participant_id)
    
    df.loc[df["Participant_ID"] == pid_str, "Sys2_Learning_Time"] = learning_time
    df.loc[df["Participant_ID"] == pid_str, "Sys2_Practice_Score"] = practice_score
    df.loc[df["Participant_ID"] == pid_str, "Sys2_Post_Test_Score"] = post_score
    df.to_excel(PARTICIPANTS_FILE, index=False)

def save_questionnaire(participant_id, answers):
    """Saves the survey answers array as a string representation inside the row."""
    df = pd.read_excel(PARTICIPANTS_FILE, dtype={"Participant_ID": str, "Questionnaire_Answers": str})
    df["Questionnaire_Answers"] = df["Questionnaire_Answers"].astype(str)
    pid_str = str(participant_id)
    
    df.loc[df["Participant_ID"] == pid_str, "Questionnaire_Answers"] = str(answers)
    df.to_excel(PARTICIPANTS_FILE, index=False)

def log_interaction(step, user_profile, user_message, ai_response):
    """
    Logs raw conversational interaction details into a separate ledger 
    for deep linguistic or context analysis.
    """
    new_data = {
        "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Experimental_Phase": [step],        
        "User_Expertise_Profile": [user_profile],  
        "User_Input": [user_message],
        "AI_Response": [ai_response]
    }
    
    df_new = pd.DataFrame(new_data)
    
    if not os.path.exists(INTERACTION_LOG_FILE):
        df_new.to_excel(INTERACTION_LOG_FILE, index=False)
    else:
        df_existing = pd.read_excel(INTERACTION_LOG_FILE)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_excel(INTERACTION_LOG_FILE, index=False)