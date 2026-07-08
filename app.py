import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
from google import genai
from google.genai import types
from google.genai.errors import ServerError, APIError

# --- IMPORTING YOUR STRUCTURAL MODULES ---
from questions import pre_test, post_test_nonadaptive, post_test_adaptive
from lessons import lessons
# tasks module is no longer required as practice tasks are removed
from questionnaire import questionnaire, likert_scale
from save_data import (
    init_db,
    add_participant,
    update_pretest,
    update_nonadaptive,
    update_adaptive,
    save_questionnaire
)

# --- PAGE CONFIG & CUSTOM STYLES ---
st.set_page_config(
    page_title="AI Assistance Research",
    page_icon="🤖",
    layout="wide"
)

# Initialize data configuration hooks
init_db()

try:
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# --- GEMINI CLIENT CONNECT ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("Gemini API Key missing! Check .streamlit/secrets.toml")

# --- INITIALIZE MULTI-STAGE STATE EXPERIMENT ---
if "page" not in st.session_state:
    st.session_state.page = "welcome"
if "participant_id" not in st.session_state:
    st.session_state.participant_id = ""
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "lesson_index" not in st.session_state:
    st.session_state.lesson_index = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = 0.0
if "questionnaire_answers" not in st.session_state:
    st.session_state.questionnaire_answers = []

# ==========================================
# STAGE 1: WELCOME SCREEN
# ==========================================
if st.session_state.page == "welcome":
    st.title("🤖 AI Assistance Research")
    st.write("### Welcome to the Research Study!")
    st.write("Thank you for participating in this experimental comparison of adaptive and non-adaptive AI assistance based on user expertise.")
    if st.button("Start Study ➜", type="primary"):
        st.session_state.page = "consent"
        st.rerun()

# ==========================================
# STAGE 2: CONSENT FORM
# ==========================================
elif st.session_state.page == "consent":
    st.markdown("<h2>📋 Informed Consent Form</h2>", unsafe_allow_html=True)
    st.write("Your responses are anonymous and will only be utilized for statistical academic analysis.")
    agree = st.checkbox("I understand the guidelines and voluntarily agree to participate in this study.")
    if st.button("Next ➜"):
        if agree:
            st.session_state.page = "participant_id"
            st.rerun()
        else:
            st.warning("You must agree to the consent form to proceed.")

# ==========================================
# STAGE 3: PARTICIPANT ID
# ==========================================
elif st.session_state.page == "participant_id":
    st.markdown("<h2>🔑 Participant Identification</h2>", unsafe_allow_html=True)
    pid = st.text_input("Enter a unique Participant ID:")
    if st.button("Submit Profile ➜") and pid:
        st.session_state.participant_id = pid
        add_participant(pid)
        st.session_state.page = "pre_test"
        st.session_state.question_index = 0
        st.session_state.score = 0
        st.rerun()

# ==========================================
# STAGE 4: PRE-TEST
# ==========================================
elif st.session_state.page == "pre_test":
    st.markdown("<h2>📝 Phase 1: Pre-Test Assessment</h2>", unsafe_allow_html=True)
    current = st.session_state.question_index
    total_qs = len(pre_test)
    
    st.markdown(f"<div class='question-number'>Question {current + 1} of {total_qs}</div>", unsafe_allow_html=True)
    q_item = pre_test[current]
    st.markdown(f"### {q_item['question']}")
    
    selected_ans = st.radio("Select your answer:", q_item['options'], index=None, key=f"pre_{current}")
    
    if st.button("Next Question ➜" if current < total_qs - 1 else "Submit Pre-Test Evaluation"):
        if selected_ans is not None:
            if selected_ans == q_item['answer']:
                st.session_state.score += 1
            
            if current < total_qs - 1:
                st.session_state.question_index += 1
                st.rerun()
            else:
                pre_score = st.session_state.score
                group = "Expert" if pre_score >= 3 else "Novice"
                st.session_state.expertise = group
                
                update_pretest(st.session_state.participant_id, pre_score, group)
                
                st.session_state.page = "show_group"
                st.rerun()
        else:
            st.warning("Please choose an option before continuing.")

# ==========================================
# STAGE 5: GROUP CLASSIFICATION CARD
# ==========================================
elif st.session_state.page == "show_group":
    st.markdown("<h2>📊 Knowledge Profile Results</h2>", unsafe_allow_html=True)
    group = st.session_state.expertise
    score = st.session_state.score
    
    if group == "Expert":
        st.success(f"Based on your score of **{score}/5**, you have been classified as an **EXPERT**.")
    else:
        st.info(f"Based on your score of **{score}/5**, you have been classified as a **NOVICE**.")
        
    if st.button("Proceed to System 1 ➜"):
        st.session_state.page = "non_adaptive_learning"
        st.session_state.lesson_index = 0
        st.session_state.chat_history = []
        st.session_state.start_time = time.time()
        st.rerun()

# ==========================================
# STAGE 6: SYSTEM 1 - NON-ADAPTIVE AI
# ==========================================
elif st.session_state.page == "non_adaptive_learning":
    idx = st.session_state.lesson_index
    total_lessons = len(lessons)
    lesson_data = lessons[idx]
    
    st.markdown(f"<h2>📘 System 1: Standard AI — Lesson {idx + 1}/{total_lessons} ({lesson_data['title']})</h2>", unsafe_allow_html=True)
    st.caption("Standard Core Engine Profile: Delivers exact database reference outlines uniformly.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown(lesson_data["content"])
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='example-box'>", unsafe_allow_html=True)
        st.markdown(lesson_data["example"])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
            st.write("#### Technical Reference Chat Interface")
            
            # 1. DISPLAY existing history
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
            
            # 2. CAPTURE new user input
            if user_input := st.chat_input("Ask standard core a question...", key="chat_s1"):
                # Append user message immediately
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # Use a placeholder to show the user's message immediately
                with st.chat_message("user"):
                    st.write(user_input)
                
                # 3. GENERATE AI response
                with st.chat_message("assistant"):
                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            response = client.models.generate_content(
                                model='gemini-1.5-flash',
                                contents=[m["content"] for m in st.session_state.chat_history],
                                config=types.GenerateContentConfig(
                                    system_instruction="You are a static, rigid textbook reference system. Provide cold, formal, encyclopedic summaries only."
                                )
                            )
                            st.write(response.text)
                            st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                            break 
                        except (ServerError, APIError):
                            if attempt < max_retries - 1:
                                time.sleep(1)
                                continue
                            else:
                                st.error("⚠️ AI server is busy. Please try again.")
                # We do NOT use st.rerun() here because st.chat_message 
                # and st.write handle the UI update automatically.
    st.markdown("<hr>", unsafe_allow_html=True)
    
    button_label = "Next Lesson ➜" if idx < total_lessons - 1 else "Proceed to System 1 Post-Test ➜"
    if st.button(button_label, type="primary"):
        if idx < total_lessons - 1:
            st.session_state.lesson_index += 1
            st.session_state.chat_history = []
            st.rerun()
        else:
            elapsed = round(time.time() - st.session_state.start_time, 2)
            st.session_state.sys1_elapsed = elapsed
            st.session_state.page = "post_test_non_adaptive"
            st.session_state.question_index = 0
            st.session_state.score = 0
            st.rerun()

# ==========================================
# STAGE 7: POST-TEST - NON-ADAPTIVE AI
# ==========================================
elif st.session_state.page == "post_test_non_adaptive":
    st.markdown("<h2>📋 Phase 2: Post-Test (System 1)</h2>", unsafe_allow_html=True)
    current = st.session_state.question_index
    total_qs = len(post_test_nonadaptive)
    
    st.markdown(f"<div class='question-number'>Question {current + 1} of {total_qs}</div>", unsafe_allow_html=True)
    q_item = post_test_nonadaptive[current]
    st.markdown(f"### {q_item['question']}")
    
    selected_ans = st.radio("Select your answer:", q_item['options'], index=None, key=f"post_s1_{current}")
    
    if st.button("Next Question ➜" if current < total_qs - 1 else "Complete System 1 Evaluation"):
        if selected_ans is not None:
            if selected_ans == q_item['answer']:
                st.session_state.score += 1
                
            if current < total_qs - 1:
                st.session_state.question_index += 1
                st.rerun()
            else:
                update_nonadaptive(
                    st.session_state.participant_id,
                    learning_time=st.session_state.sys1_elapsed,
                    post_score=st.session_state.score
                )
                st.session_state.page = "transition_to_sys2"
                st.rerun()
        else:
            st.warning("Please choose an answer.")

# ==========================================
# STAGE 8: TRANSITION SCREEN
# ==========================================
elif st.session_state.page == "transition_to_sys2":
    st.markdown("<h2>🟢 Transitioning to System 2</h2>", unsafe_allow_html=True)
    st.write("You have successfully completed the Evaluation block for **System 1 (Non-Adaptive AI)**.")
    st.write("Next, you will experience **System 2 (Adaptive AI Framework)**, which realigns dynamically based on your profile tracking parameters.")
    
    if st.button("Begin System 2 ➜", type="primary"):
        st.session_state.page = "adaptive_learning"
        st.session_state.lesson_index = 0
        st.session_state.chat_history = []
        st.session_state.start_time = time.time()
        st.rerun()

# ==========================================
# STAGE 9: SYSTEM 2 - ADAPTIVE AI
# ==========================================
# ==========================================
# STAGE 9: SYSTEM 2 - ADAPTIVE AI
# ==========================================
elif st.session_state.page == "adaptive_learning":
    idx = st.session_state.lesson_index
    total_lessons = len(lessons)
    lesson_data = lessons[idx]
    group = st.session_state.expertise
    
    st.markdown(f"<h2>🟢 System 2: Adaptive AI — Lesson {idx + 1}/{total_lessons} ({lesson_data['title']})</h2>", unsafe_allow_html=True)
    st.success(f"Dynamic Persona Tracker: System adapted to **{group.upper()}** profile mode rules.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Lesson Content stays here, clean and separate from chat
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown(lesson_data["content"])
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='example-box'>", unsafe_allow_html=True)
        st.markdown(lesson_data["example"])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.write(f"#### Adaptive Helper Interfacing ({group})")
        
        # 1. DISPLAY history (Loop happens here)
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        # 2. CAPTURE new input
        if user_input := st.chat_input("Ask adaptive coach a question...", key="chat_s2"):
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.rerun() # Refresh to trigger the generation block below

        # 3. GENERATE response (Triggered only by new user input)
        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
            
            # Set system prompt
            if group == "Novice":
                sys_prompt = "You are an adaptive tutor for a Novice. Use clear step-by-step breakdowns and simple real-world structural analogies."
            else:
                sys_prompt = "You are an advanced researcher helper. Skip basic details. Provide rich mathematical definitions and concise quantitative methodologies."
                
            with st.chat_message("assistant"):
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        response = client.models.generate_content(
                            model='gemini-1.5-flash',
                            contents=[m["content"] for m in st.session_state.chat_history],
                            config=types.GenerateContentConfig(system_instruction=sys_prompt)
                        )
                        st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                        st.rerun() # Refresh to display the new assistant message
                        break
                    except (ServerError, APIError):
                        if attempt < max_retries - 1:
                            time.sleep(1)
                            continue
                        else:
                            st.error("⚠️ AI server is busy. Please try your question again.")

    st.markdown("<hr>", unsafe_allow_html=True)
    
    button_label = "Next Lesson ➜" if idx < total_lessons - 1 else "Proceed to System 2 Post-Test ➜"
    if st.button(button_label, type="primary"):
        if idx < total_lessons - 1:
            st.session_state.lesson_index += 1
            st.session_state.chat_history = []
            st.rerun()
        else:
            elapsed = round(time.time() - st.session_state.start_time, 2)
            st.session_state.sys2_elapsed = elapsed
            st.session_state.page = "post_test_adaptive"
            st.session_state.question_index = 0
            st.session_state.score = 0
            st.rerun()

# ==========================================
# STAGE 10: POST-TEST - ADAPTIVE AI
# ==========================================
elif st.session_state.page == "post_test_adaptive":
    st.markdown("<h2>📋 Phase 4: Post-Test (System 2)</h2>", unsafe_allow_html=True)
    current = st.session_state.question_index
    total_qs = len(post_test_adaptive)
    
    st.markdown(f"<div class='question-number'>Question {current + 1} of {total_qs}</div>", unsafe_allow_html=True)
    q_item = post_test_adaptive[current]
    st.markdown(f"### {q_item['question']}")
    
    selected_ans = st.radio("Select your answer:", q_item['options'], index=None, key=f"post_s2_{current}")
    
    if st.button("Next Question ➜" if current < total_qs - 1 else "Complete System 2 Evaluation"):
        if selected_ans is not None:
            if selected_ans == q_item['answer']:
                st.session_state.score += 1
                
            if current < total_qs - 1:
                st.session_state.question_index += 1
                st.rerun()
            else:
                update_adaptive(
                    st.session_state.participant_id,
                    learning_time=st.session_state.sys2_elapsed,
                    post_score=st.session_state.score
                )
                st.session_state.page = "questionnaire"
                st.session_state.question_index = 0
                st.session_state.questionnaire_answers = []
                st.rerun()
        else:
            st.warning("Please choose an answer.")

# ==========================================
# STAGE 11: EXPERIENCE EVALUATION QUESTIONNAIRE
# ==========================================
elif st.session_state.page == "questionnaire":
    st.markdown("<h2>📊 User Experience Feedback Questionnaire</h2>", unsafe_allow_html=True)
    current = st.session_state.question_index
    total_items = len(questionnaire)
    
    st.markdown(f"<div class='question-number'>Statement {current + 1} of {total_items}</div>", unsafe_allow_html=True)
    item = questionnaire[current]
    st.markdown(f"### {item['question']}")
    
    response = st.radio("Your Assessment:", likert_scale, index=None, key=f"likert_{current}")
    
    if st.button("Submit Survey Entry" if current == total_items - 1 else "Next Statement ➜"):
        if response is not None:
            st.session_state.questionnaire_answers.append(response)
            
            if current < total_items - 1:
                st.session_state.question_index += 1
                st.rerun()
            else:
                save_questionnaire(
                    st.session_state.participant_id,
                    st.session_state.questionnaire_answers
                )
                st.session_state.page = "finish"
                st.rerun()
        else:
            st.warning("Please select a tracking response rating index scale marker.")

# ==========================================
# STAGE 12: EXPERIMENT FINISH & DATA CARD
# ==========================================
elif st.session_state.page == "finish":
    st.balloons()
    st.title("🎉 Study Completed!")
    st.success("Thank you for participating in this research experiment.")
    
    # 1. Calculate Accuracy Metrics Safely
    pre_score = int(st.session_state.get("pre_score_data", 0))
    sys1_score = int(st.session_state.get("sys1_post_data", 0))
    sys2_score = int(st.session_state.get("sys2_post_data", 0))
    total_questions = 5 
    
    # 2. Process Questionnaire Data
    answers = st.session_state.get("questionnaire_answers", [])
    
    # Map Likert scale text choices perfectly to numbers 1-5
    likert_map = {
        "Strongly Disagree": 1,
        "Disagree": 2,
        "Neutral": 3,
        "Agree": 4,
        "Strongly Agree": 5
    }
    
    # Convert text responses to numbers
    scores = [likert_map.get(ans, 3) for ans in answers] # defaults to 3 if a question is blank
    
    # Calculate explicit research dimension averages based on your 7 items
    if len(scores) >= 7:
        # Usability & Engagement: Avg of Q1 ("easy to use") and Q4 ("felt engaged")
        usability_score = round((scores[0] + scores[3]) / 2, 2)
        
        # Perceived Effectiveness: Avg of Q2 ("helped understand"), Q3 ("feedback helped"), and Q5 ("improved understanding")
        effectiveness_score = round((scores[1] + scores[2] + scores[4]) / 3, 2)
        
        # Adaptive Preference: Avg of Q6 ("Adaptive was more helpful") and Q7 ("prefer Adaptive for future")
        adaptive_preference = round((scores[5] + scores[6]) / 2, 2)
    else:
        usability_score = effectiveness_score = adaptive_preference = "N/A"

    st.write("### 📋 Logged Participant Session Data:")
    summary_df = pd.DataFrame([{
        "Participant_ID": st.session_state.get("pid_data", st.session_state.participant_id),
        "Expertise_Group": st.session_state.get("expertise_group_data", ""),
        "Pre_Test_Score": f"{pre_score}/{total_questions}",
        "Sys1_Post_Score": f"{sys1_score}/{total_questions}",
        "Sys1_Accuracy": f"{(sys1_score / total_questions) * 100:.1f}%",
        "Sys1_Learning_Time": st.session_state.get("sys1_time_data", ""),
        "Sys2_Post_Score": f"{sys2_score}/{total_questions}",
        "Sys2_Accuracy": f"{(sys2_score / total_questions) * 100:.1f}%",
        "Sys2_Learning_Time": st.session_state.get("sys2_time_data", ""),
        "Usability_Engagement_Avg": usability_score,
        "Learning_Effectiveness_Avg": effectiveness_score,
        "Adaptive_Preference_Avg": adaptive_preference
    }])
    st.dataframe(summary_df)
    st.info("You can hover over the table above and click the download icon to save it as a CSV anytime!")