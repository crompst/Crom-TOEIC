import streamlit as st
import pandas as pd
import random
import json
import re
from google import genai

# -----------------------------
# PAGE SETTING
# -----------------------------

st.set_page_config(
    page_title="TOEIC AI Learning Platform",
    layout="wide"
)

st.title("🎓 TOEIC AI Learning Platform 6.2")

# -----------------------------
# LOAD API KEY
# -----------------------------

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# -----------------------------
# LOAD WORD DATA
# -----------------------------

words = pd.read_csv("toeic_words.csv")

# -----------------------------
# SESSION STATE
# -----------------------------

if "vocab_question" not in st.session_state:
    st.session_state.vocab_question = None

if "reading_question" not in st.session_state:
    st.session_state.reading_question = None

# -----------------------------
# GEMINI SAFE CALL
# -----------------------------

def ask_gemini(prompt):

    try:

        if not prompt:
            return None

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt]
        )

        return response.text

    except Exception as e:

        st.error("Gemini API Error")
        st.write(e)

        return None


# -----------------------------
# SIDEBAR MENU
# -----------------------------

menu = st.sidebar.radio(
    "Menu",
    [
        "Vocabulary Practice",
        "Part7 Reading",
    ]
)

# =====================================================
# VOCABULARY PRACTICE
# =====================================================

if menu == "Vocabulary Practice":

    st.header("Vocabulary Practice")

    if st.button("Generate Vocabulary Question"):

        word = random.choice(words["word"].tolist())

        prompt = f"""
Create a TOEIC sentence using the word '{word}'.

Leave the word blank like _____

Return JSON:

{{
"sentence":"",
"choices":["","","",""],
"answer":""
}}
"""

        result = ask_gemini(prompt)

        if result:

            try:

                match = re.search(r"\{.*\}", result, re.DOTALL)

                data = json.loads(match.group())

                st.session_state.vocab_question = data

            except:

                st.error("JSON parsing failed")


    if st.session_state.vocab_question:

        q = st.session_state.vocab_question

        st.write(q["sentence"])

        user_answer = st.radio(
            "Choose the correct word",
            q["choices"]
        )

        if st.button("Check Answer"):

            if user_answer == q["answer"]:

                st.success("Correct!")

            else:

                st.error(f"Correct answer: {q['answer']}")

# =====================================================
# PART7 READING
# =====================================================

if menu == "Part7 Reading":

    st.header("TOEIC Part7 Reading")

    if st.button("Generate Reading Passage"):

        prompt = """
Create a TOEIC Part7 style reading passage.

Return JSON:

{
"passage":"",
"questions":[
{
"question":"",
"choices":["","","",""],
"answer":""
},
{
"question":"",
"choices":["","","",""],
"answer":""
}
]
}
"""

        result = ask_gemini(prompt)

        if result:

            try:

                match = re.search(r"\{.*\}", result, re.DOTALL)

                data = json.loads(match.group())

                st.session_state.reading_question = data

            except:

                st.error("JSON parsing failed")


    if st.session_state.reading_question:

        data = st.session_state.reading_question

        st.subheader("Passage")

        st.write(data["passage"])

        for i, q in enumerate(data["questions"]):

            st.write(q["question"])

            user_answer = st.radio(
                f"Question {i+1}",
                q["choices"],
                key=f"reading{i}"
            )

            if st.button(f"Check Answer {i}"):

                if user_answer == q["answer"]:

                    st.success("Correct!")

                else:

                    st.error(f"Correct answer: {q['answer']}")