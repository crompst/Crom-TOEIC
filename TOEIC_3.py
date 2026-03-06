import streamlit as st
import pandas as pd
import random
import json
import re
from google import genai

st.set_page_config(page_title="TOEIC AI Platform", layout="wide")

st.title("🎓 TOEIC AI Learning Platform 6.1")

# -------------------------
# API
# -------------------------
def load_api_key():
    with open("Google_api.txt") as f:
        return f.read().strip()

client = genai.Client(api_key=load_api_key())

# -------------------------
# LOAD WORD DATABASE
# -------------------------

words = pd.read_csv("toeic_words.csv")

# -------------------------
# LOAD PROGRESS
# -------------------------

try:
    progress = pd.read_csv("progress.csv")
except:
    progress = pd.DataFrame(columns=["type","correct"])

# -------------------------
# SIDEBAR
# -------------------------

menu = st.sidebar.radio(
    "Menu",
    [
        "Vocabulary",
        "Part7 Reading",
        "Statistics"
    ]
)

# ===================================================
# VOCABULARY
# ===================================================

if menu == "Vocabulary":

    st.header("Vocabulary Practice")

    if "vocab_question" not in st.session_state:
        st.session_state.vocab_question = None

    if st.button("Generate Vocabulary Question"):

        word = random.choice(words["word"].tolist())

        prompt = f"""
Create a TOEIC sentence using the word '{word}'.

Leave the word blank: _____

Return JSON:

{{
"sentence":"",
"choices":["","","",""],
"answer":""
}}
"""

        response = client.models.generate_content(
            model="gemini-1.5-flash-latest",
            contents=prompt
        )

        match = re.search(r"\{.*\}", response.text, re.DOTALL)

        data = json.loads(match.group())

        st.session_state.vocab_question = data

    # -------------------------

    if st.session_state.vocab_question:

        q = st.session_state.vocab_question

        st.write(q["sentence"])

        user = st.radio(
            "Choose answer",
            q["choices"]
        )

        if st.button("Check Answer"):

            if user == q["answer"]:

                st.success("Correct!")

                new = pd.DataFrame(
                    {"type":["vocab"],"correct":[1]}
                )

            else:

                st.error(f"Correct answer: {q['answer']}")

                new = pd.DataFrame(
                    {"type":["vocab"],"correct":[0]}
                )

            new.to_csv(
                "progress.csv",
                mode="a",
                header=False,
                index=False
            )

# ===================================================
# PART7
# ===================================================

if menu == "Part7 Reading":

    st.header("TOEIC Part7 Practice")

    if "reading_question" not in st.session_state:
        st.session_state.reading_question = None

    if st.button("Generate Reading Passage"):

        prompt = """
Generate a TOEIC Part7 passage with 2 questions.

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

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        match = re.search(r"\{.*\}", response.text, re.DOTALL)

        data = json.loads(match.group())

        st.session_state.reading_question = data

    # -------------------------

    if st.session_state.reading_question:

        data = st.session_state.reading_question

        st.subheader("Passage")

        st.write(data["passage"])

        for i,q in enumerate(data["questions"]):

            st.write(q["question"])

            user = st.radio(
                f"Question {i+1}",
                q["choices"],
                key=f"q{i}"
            )

            if st.button(f"Check {i}"):

                if user == q["answer"]:

                    st.success("Correct")

                    new = pd.DataFrame(
                        {"type":["reading"],"correct":[1]}
                    )

                else:

                    st.error(f"Correct answer: {q['answer']}")

                    new = pd.DataFrame(
                        {"type":["reading"],"correct":[0]}
                    )

                new.to_csv(
                    "progress.csv",
                    mode="a",
                    header=False,
                    index=False
                )

# ===================================================
# STATISTICS
# ===================================================

if menu == "Statistics":

    st.header("Learning Statistics")

    if len(progress) > 0:

        accuracy = progress["correct"].mean()*100

        st.metric(
            "Accuracy",
            f"{accuracy:.1f}%"
        )

        predicted_score = int(accuracy * 9.9)

        st.metric(
            "Predicted TOEIC Score",
            predicted_score
        )

        st.bar_chart(progress["correct"])

    else:

        st.write("No learning data yet.")