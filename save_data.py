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

def update_nonadaptive(participant_id, learning_time, post_score, practice_score=None):
    # Store learning metrics cleanly
    st.session_state["sys1_time_data"] = learning_time
    st.session_state["sys1_post_data"] = post_score

def update_adaptive(participant_id, learning_time, post_score, practice_score=None):
    # Store learning metrics cleanly
    st.session_state["sys2_time_data"] = learning_time
    st.session_state["sys2_post_data"] = post_score

def save_questionnaire(participant_id, questionnaire_answers):
    # Store final survey results safely in session memory
    st.session_state["survey_data"] = str(questionnaire_answers)
    
    # Flags the system that everything is packed and ready
    st.session_state["data_ready_to_view"] = True