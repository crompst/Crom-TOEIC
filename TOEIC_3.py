import flet as ft
import sqlite3
import time
import threading

# --- DB 설정 및 초기화 ---
def init_db():
    conn = sqlite3.connect("toeic_study.db", check_same_thread=False)
    cursor = conn.cursor()
    # 문제 테이블 (카테고리 추가)
    cursor.execute('''CREATE TABLE IF NOT EXISTS quiz 
                      (id INTEGER PRIMARY KEY, question TEXT, answer TEXT, 
                       opt1 TEXT, opt2 TEXT, opt3 TEXT, exp TEXT, category TEXT)''')
    # 오답 기록 테이블
    cursor.execute('''CREATE TABLE IF NOT EXISTS wrong_notes 
                      (quiz_id INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # 샘플 데이터 삽입 (비어있을 때만)
    cursor.execute("SELECT count(*) FROM quiz")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("The CEO _______ the merger next week.", "will announce", "announce", "announced", "will announce", "미래 부사구 next week 확인", "시제"),
            ("Please review the document _______.", "carefully", "carefully", "careful", "carefulness", "동사 수식은 부사", "품사"),
            ("The team is _______ for the upcoming project.", "preparing", "prepare", "prepared", "preparing", "be동사 뒤 현재진행", "동사형태")
        ]
        cursor.executemany("INSERT INTO quiz (question, answer, opt1, opt2, opt3, exp, category) VALUES (?,?,?,?,?,?,?)", sample_data)
        conn.commit()
    return conn

def main(page: ft.Page):
    conn = init_db()
    cursor = conn.cursor()
    
    page.title = "TOEIC 700 Master (iPad Optimized)"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    
    # --- 상태 변수 ---
    state = {"quiz_idx": 0, "timer_seconds": 60, "timer_running": False}

    # --- 공통 기능: 다크모드 ---
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        theme_icon.icon = ft.icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.icons.DARK_MODE
        page.update()

    theme_icon = ft.IconButton(ft.icons.DARK_MODE, on_click=toggle_theme)

    # --- 1. 퀴즈 섹션 (오답 저장 로직 포함) ---
    def load_quiz():
        cursor.execute("SELECT * FROM quiz")
        return cursor.fetchall()

    quizzes = load_quiz()

    def check_answer(e):
        q = quizzes[state["quiz_idx"]]
        if quiz_options.value == q[2]:
            result_text.value = f"✅ 정답! \n해설: {q[6]}"
            result_text.color = "green"
        else:
            result_text.value = f"❌ 오답! 정답은 {q[2]}입니다. \n해설: {q[6]}"
            result_text.color = "red"
            # 오답 노터에 저장
            cursor.execute("INSERT INTO wrong_notes (quiz_id) VALUES (?)", (q[0],))
            conn.commit()
        page.update()

    def next_quiz(e):
        state["quiz_idx"] = (state["quiz_idx"] + 1) % len(quizzes)
        update_quiz_ui()

    def update_quiz_ui():
        q = quizzes[state["quiz_idx"]]
        quiz_q_text.value = f"[{q[7]}] {q[1]}"
        quiz_options.options = [ft.dropdown.Option(q[3]), ft.dropdown.Option(q[4]), ft.dropdown.Option(q[5])]
        quiz_options.value = None
        result_text.value = ""
        page.update()

    quiz_q_text = ft.Text("", size=22, weight="bold")
    quiz_options = ft.RadioGroup(content=ft.Column([]))
    result_text = ft.Text("", size=16)

    quiz_view = ft.Column([
        ft.Row([ft.Text("Part 5 문법 훈련", size=28, weight="bold"), theme_icon], alignment="spaceBetween"),
        ft.Divider(),
        quiz_q_text,
        quiz_options,
        ft.Row([
            ft.ElevatedButton("정답 확인", on_click=check_answer, icon=ft.icons.CHECK),
            ft.TextButton("다음 문제", on_click=next_quiz)
        ]),
        result_text
    ], visible=True)
    update_quiz_ui()

    # --- 2. 오답 노트 섹션 ---
    def load_wrong_notes(e):
        cursor.execute("""SELECT q.question, q.answer FROM wrong_notes w 
                          JOIN quiz q ON w.quiz_id = q.id 
                          ORDER BY w.timestamp DESC LIMIT 5""")
        notes = cursor.fetchall()
        wrong_list.controls = [ft.ListTile(title=ft.Text(n[0]), subtitle=ft.Text(f"정답: {n[1]}")) for n in notes]
        page.update()

    wrong_list = ft.Column([])
    wrong_view = ft.Column([
        ft.Text("나의 오답 노트", size=28, weight="bold"),
        ft.Text("최근 틀린 문제 5개를 보여줍니다.", size=14, color="grey"),
        ft.ElevatedButton("오답 불러오기", on_click=load_wrong_notes),
        wrong_list
    ], visible=False)

    # --- 3. 독해 타이머 섹션 ---
    timer_text = ft.Text("01:00", size=50, weight="bold", font_family="Courier")
    
    def run_timer():
        while state["timer_running"] and state["timer_seconds"] > 0:
            time.sleep(1)
            state["timer_seconds"] -= 1
            timer_text.value = f"{state['timer_seconds'] // 60:02d}:{state['timer_seconds'] % 60:02d}"
            page.update()
        state["timer_running"] = False

    def start_timer(e):
        if not state["timer_running"]:
            state["timer_running"] = True
            threading.Thread(target=run_timer, daemon=True).start()

    def reset_timer(e):
        state["timer_running"] = False
        state["timer_seconds"] = 60
        timer_text.value = "01:00"
        page.update()

    timer_view = ft.Column([
        ft.Text("Part 7 시간 관리", size=28, weight="bold"),
        ft.Container(timer_text, alignment=ft.alignment.center, padding=30),
        ft.Row([
            ft.FloatingActionButton(icon=ft.icons.PLAY_ARROW, on_click=start_timer),
            ft.FloatingActionButton(icon=ft.icons.REPLAY, on_click=reset_timer),
        ], alignment="center")
    ], visible=False)

    # --- 네비게이션 로직 ---
    def on_nav_change(e):
        idx = e.control.selected_index
        quiz_view.visible = (idx == 0)
        wrong_view.visible = (idx == 1)
        timer_view.visible = (idx == 2)
        page.update()

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(icon=ft.icons.SCHOOL, label="학습"),
            ft.NavigationDestination(icon=ft.icons.EDIT_NOTE, label="오답노트"),
            ft.NavigationDestination(icon=ft.icons.TIMER, label="타이머"),
        ],
        on_change=on_nav_change
    )

    page.add(quiz_view, wrong_view, timer_view)

# 아이패드 접속을 위해 포트 개방 및 웹 모드 실행
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
