import gspread
import streamlit as st

def init_db():
    if "google_sheets" not in st.secrets:
        st.error("Google Sheets credentials not found in secrets!")

def add_participant(pid):
    # Initializes session state for this participant
    st.session_state["pid_data"] = pid

def update_pretest(pid, score, group):
    st.session_state["expertise_group_data"] = group
    st.session_state["pre_score_data"] = score

def update_nonadaptive(pid, learning_time, post_score):
    st.session_state["sys1_time_data"] = learning_time
    st.session_state["sys1_post_data"] = post_score

def update_adaptive(pid, learning_time, post_score):
    st.session_state["sys2_time_data"] = learning_time
    st.session_state["sys2_post_data"] = post_score

def save_questionnaire(participant_id, questionnaire_answers):
    # 1. Connect
    creds = st.secrets["google_sheets"]
    gc = gspread.service_account_from_dict(creds)
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1n5JATvL2-k2nByf0fjkPFd3zRRMYJGfojcLFdaFYVt8/edit")
    worksheet = sh.sheet1 

    # 2. Calculate Averages (Match these indices to your NEW questionnaire.py)
    likert_map = {"Strongly Disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly Agree": 5}
    scores = [likert_map.get(ans, 3) for ans in questionnaire_answers]
    
    usability = round((scores[0] + scores[3]) / 2, 2)
    effectiveness = round((scores[1] + scores[2] + scores[4]) / 3, 2)
    preference = round((scores[5] + scores[6]) / 2, 2)

    # 3. Compile row (Must match the 12 columns: A-L)
    row = [
        participant_id,
        st.session_state.get("expertise_group_data", "N/A"),
        st.session_state.get("pre_score_data", 0),
        st.session_state.get("sys1_post_data", 0),
        f"{(int(st.session_state.get('sys1_post_data', 0)) / 5) * 100:.1f}%",
        st.session_state.get("sys1_time_data", 0),
        st.session_state.get("sys2_post_data", 0),
        f"{(int(st.session_state.get('sys2_post_data', 0)) / 5) * 100:.1f}%",
        st.session_state.get("sys2_time_data", 0),
        usability,
        effectiveness,
        preference
    ]
    
    worksheet.append_row(row)
    st.session_state["data_ready_to_view"] = True