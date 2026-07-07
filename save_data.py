import streamlit as st

def init_db():
    """Keeps app.py happy on initialization."""
    pass

def add_participant(participant_id):
    # Store ID safely in session memory
    st.session_state["pid_data"] = participant_id

def update_pretest(participant_id, pre_score, group):
    # Store pre-test results safely in session memory
    st.session_state["expertise_group_data"] = group
    st.session_state["pre_score_data"] = pre_score

def update_nonadaptive(participant_id, learning_time, practice_score, post_score):
    # Store System 1 results safely in session memory
    st.session_state["sys1_time_data"] = learning_time
    st.session_state["sys1_practice_data"] = practice_score
    st.session_state["sys1_post_data"] = post_score

def update_adaptive(participant_id, learning_time, practice_score, post_score):
    # Store System 2 results safely in session memory
    st.session_state["sys2_time_data"] = learning_time
    st.session_state["sys2_practice_data"] = practice_score
    st.session_state["sys2_post_data"] = post_score

def save_questionnaire(participant_id, questionnaire_answers):
    # Store final survey results safely in session memory
    st.session_state["survey_data"] = str(questionnaire_answers)
    
    # Optional: Display a copy of the results on the final screen so you never lose them
    st.session_state["data_ready_to_view"] = True