import gspread
import streamlit as st
import pandas as pd
def save_questionnaire(participant_id, questionnaire_answers):
    # 1. Connect using the credentials you saved in Streamlit Secrets
    creds = st.secrets["google_sheets"]
    gc = gspread.service_account_from_dict(creds)
    
    # 2. Open your specific sheet by the URL
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1n5JATvL2-k2nByf0fjkPFd3zRRMYJGfojcLFdaFYVt8/edit")
    worksheet = sh.sheet1 
    
    # 3. Compile your row data
    row = [
        participant_id,
        st.session_state.get("expertise_group_data", "N/A"),
        st.session_state.get("pre_score_data", 0),
        st.session_state.get("sys1_time_data", 0),
        st.session_state.get("sys1_post_data", 0),
        st.session_state.get("sys2_time_data", 0),
        st.session_state.get("sys2_post_data", 0),
        str(questionnaire_answers)
    ]
    
    # 4. Physically append the new row
    worksheet.append_row(row)
    st.session_state["data_ready_to_view"] = True