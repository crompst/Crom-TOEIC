import streamlit as st
import pandas as pd
import random
import re
from google import genai
from gtts import gTTS
import tempfile

st.set_page_config(
    page_title="TOEIC AI Platform",
    layout="wide"
)

st.title("🎓 TOEIC AI Learning Platform 4.0")

# ----------------------
# API KEY
# ----------------------

def load_api_key():
    with open("Google_api.txt") as f:
        return f.read().strip()

client = genai.Client(api_key=load_api_key())

# ----------------------
# AUDIO
# ----------------------

def speak_word(word):

    tts = gTTS(word)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

    tts.save(tmp.name)

    return tmp.name

# ----------------------
# JSON PARSER
# ----------------------

def extract_json(text):

    import json

    match = re.search(r"\[.*\]", text, re.DOTALL)

    if match:
        return json.loads(match.group())

    return None

# ----------------------
# LOCAL VOCAB
# ----------------------

def local_vocab():

    return [
        {
        "word":"mandatory",
        "phonetic":"/ˈmændətɔːri/",
        "meaning_korean":"의무적인",
        "example":"Safety training is mandatory for all employees."
        },
        {
        "word":"facilitate",
        "phonetic":"/fəˈsɪlɪteɪt/",
        "meaning_korean":"촉진하다",
        "example":"This system will facilitate communication."
        },
        {
        "word":"acquisition",
        "phonetic":"/ˌækwɪˈzɪʃən/",
        "meaning_korean":"획득",
        "example":"The acquisition improved the company's growth."
        },
        {
        "word":"personnel",
        "phonetic":"/ˌpɜːrsəˈnel/",
        "meaning_korean":"직원",
        "example":"Personnel must attend the meeting."
        }
    ]

# ----------------------
# LOCAL RC
# ----------------------

def local_rc():

    return [
        {
        "question":"The manager requested that all expense reports be submitted _____ before the end of the fiscal quarter.",
        "choices":{
        "A":"immediately",
        "B":"immediate",
        "C":"immediacy",
        "D":"more immediate"
        },
        "answer":"A",
        "explanation_korean":"requested that + 주어 + 동사원형 구조에서는 동사 submit이 오며 부사 immediately가 정답입니다."
        }
    ]

# ----------------------
# SIDEBAR
# ----------------------

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Vocabulary Trainer",
        "RC Practice"
    ]
)

# ======================
# DASHBOARD
# ======================

if menu == "Dashboard":

    st.header("📊 Learning Dashboard")

    st.write("TOEIC AI 학습 플랫폼에 오신 것을 환영합니다.")

# ======================
# VOCABULARY
# ======================

if menu == "Vocabulary Trainer":

    st.header("📚 Vocabulary Trainer")

    if st.button("Generate Vocabulary"):

        try:

            prompt="""
Generate 10 TOEIC vocabulary words.

Return JSON:

[
{"word":"","phonetic":"","meaning_korean":"","example":""}
]
"""

            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )

            vocab = extract_json(response.text)

            st.session_state.vocab = vocab

        except:

            st.warning("API limit reached → local vocabulary 사용")

            st.session_state.vocab = local_vocab()

# FLASHCARD

    if "vocab" in st.session_state:

        st.subheader("Flashcards")

        for v in st.session_state.vocab:

            audio = speak_word(v["word"])

            st.markdown(f"""
### {v['word']} {v['phonetic']}
""")

            st.audio(audio)

            st.write("뜻:", v["meaning_korean"])

            st.write("Example:", v["example"])

# VOCAB TEST

        st.subheader("Vocabulary Test")

        word=random.choice(st.session_state.vocab)

        sentence=re.sub(
            word["word"],
            "_____",
            word["example"],
            flags=re.IGNORECASE
        )

        st.write(sentence)

        distractors=random.sample(
            [v["word"] for v in st.session_state.vocab if v["word"]!=word["word"]],
            3
        )

        options=distractors+[word["word"]]

        random.shuffle(options)

        user=st.radio("Choose answer",options)

        if st.button("Check Vocabulary"):

            if user==word["word"]:

                st.success("Correct!")

            else:

                st.error(f"Wrong! Correct answer: {word['word']}")

# ======================
# RC PRACTICE
# ======================

if menu=="RC Practice":

    st.header("📖 RC Practice")

    if st.button("Generate RC Questions"):

        try:

            prompt="""
Generate 5 TOEIC RC questions.

Explanation must be in Korean.

Return JSON:

[
{
"question":"",
"choices":{"A":"","B":"","C":"","D":""},
"answer":"",
"explanation_korean":""
}
]
"""

            response=client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )

            questions=extract_json(response.text)

            st.session_state.questions=questions

        except:

            st.warning("API limit reached → local RC 문제 사용")

            st.session_state.questions=local_rc()

    if "questions" in st.session_state:

        for i,q in enumerate(st.session_state.questions):

            st.write(q["question"])

            choices=q["choices"]

            options=[
                choices["A"],
                choices["B"],
                choices["C"],
                choices["D"]
            ]

            user=st.radio("Choose answer",options,key=i)

            correct=choices[q["answer"]]

            if st.button(f"Check {i}"):

                if user==correct:

                    st.success("Correct!")

                else:

                    st.error(f"Wrong! Correct answer: {correct}")

                st.write("해설:",q["explanation_korean"])