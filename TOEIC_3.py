import streamlit as st
import pandas as pd
import random
import json
import re
from google import genai

st.set_page_config(page_title="TOEIC AI Platform 6.0", layout="wide")

st.title("🎓 TOEIC AI Learning Platform 6.0")

# -------------------------
# API
# -------------------------

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# -------------------------
# LOAD WORD DB
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
# VOCABULARY QUIZ
# ===================================================

if menu == "Vocabulary":

    st.header("Vocabulary Practice")

    word = random.choice(words["word"].tolist())

    meaning = words[words["word"] == word]["meaning"].values[0]

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
        model="gemini-1.5-flash",
        contents=prompt
    )

    match = re.search(r"\{.*\}", response.text, re.DOTALL)
    data = json.loads(match.group())

    sentence = data["sentence"]
    choices = data["choices"]
    answer = data["answer"]

    st.write(sentence)

    user = st.radio("Choose answer", choices)

    if st.button("Check Answer"):

        if user == answer:

            st.success("Correct!")

            new = pd.DataFrame({"type":["vocab"],"correct":[1]})
            new.to_csv("progress.csv",mode="a",header=False,index=False)

        else:

            st.error(f"Wrong! Correct answer: {answer}")

            new = pd.DataFrame({"type":["vocab"],"correct":[0]})
            new.to_csv("progress.csv",mode="a",header=False,index=False)

# ===================================================
# PART7 READING
# ===================================================

if menu == "Part7 Reading":

    st.header("TOEIC Part7 Reading")

    prompt = """
Generate a TOEIC Part7 reading passage with 2 questions.

Return JSON:

{
"passage":"",
"questions":[
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

    st.write("### Passage")
    st.write(data["passage"])

    for i,q in enumerate(data["questions"]):

        st.write(q["question"])

        user = st.radio(
            f"Question {i+1}",
            q["choices"],
            key=i
        )

        if st.button(f"Check {i}"):

            if user == q["answer"]:

                st.success("Correct")

                new = pd.DataFrame({"type":["reading"],"correct":[1]})
                new.to_csv("progress.csv",mode="a",header=False,index=False)

            else:

                st.error(f"Correct answer: {q['answer']}")

                new = pd.DataFrame({"type":["reading"],"correct":[0]})
                new.to_csv("progress.csv",mode="a",header=False,index=False)

# ===================================================
# STATISTICS
# ===================================================

if menu == "Statistics":

    st.header("Learning Statistics")

    if len(progress) > 0:

        accuracy = progress["correct"].mean()*100

        st.metric("Accuracy", f"{accuracy:.1f}%")

        predicted_score = int(accuracy * 9.9)

        st.metric("Predicted TOEIC Score", predicted_score)

        st.bar_chart(progress["correct"])import streamlit as st
import pandas as pd
import random
import json
import re
from google import genai

st.set_page_config(page_title="TOEIC AI Platform 6.0", layout="wide")

st.title("🎓 TOEIC AI Learning Platform 6.0")

# -------------------------
# API
# -------------------------

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

# -------------------------
# LOAD WORD DB
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
# VOCABULARY QUIZ
# ===================================================

if menu == "Vocabulary":

    st.header("Vocabulary Practice")

    word = random.choice(words["word"].tolist())

    meaning = words[words["word"] == word]["meaning"].values[0]

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
        model="gemini-1.5-flash",
        contents=prompt
    )

    match = re.search(r"\{.*\}", response.text, re.DOTALL)
    data = json.loads(match.group())

    sentence = data["sentence"]
    choices = data["choices"]
    answer = data["answer"]

    st.write(sentence)

    user = st.radio("Choose answer", choices)

    if st.button("Check Answer"):

        if user == answer:

            st.success("Correct!")

            new = pd.DataFrame({"type":["vocab"],"correct":[1]})
            new.to_csv("progress.csv",mode="a",header=False,index=False)

        else:

            st.error(f"Wrong! Correct answer: {answer}")

            new = pd.DataFrame({"type":["vocab"],"correct":[0]})
            new.to_csv("progress.csv",mode="a",header=False,index=False)

# ===================================================
# PART7 READING
# ===================================================

if menu == "Part7 Reading":

    st.header("TOEIC Part7 Reading")

    prompt = """
Generate a TOEIC Part7 reading passage with 2 questions.

Return JSON:

{
"passage":"",
"questions":[
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

    st.write("### Passage")
    st.write(data["passage"])

    for i,q in enumerate(data["questions"]):

        st.write(q["question"])

        user = st.radio(
            f"Question {i+1}",
            q["choices"],
            key=i
        )

        if st.button(f"Check {i}"):

            if user == q["answer"]:

                st.success("Correct")

                new = pd.DataFrame({"type":["reading"],"correct":[1]})
                new.to_csv("progress.csv",mode="a",header=False,index=False)

            else:

                st.error(f"Correct answer: {q['answer']}")

                new = pd.DataFrame({"type":["reading"],"correct":[0]})
                new.to_csv("progress.csv",mode="a",header=False,index=False)

# ===================================================
# STATISTICS
# ===================================================

if menu == "Statistics":

    st.header("Learning Statistics")

    if len(progress) > 0:

        accuracy = progress["correct"].mean()*100

        st.metric("Accuracy", f"{accuracy:.1f}%")

        predicted_score = int(accuracy * 9.9)

        st.metric("Predicted TOEIC Score", predicted_score)

        st.bar_chart(progress["correct"])