import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import math
import random
import time
import pandas as pd

st.set_page_config(
    page_title="Flood Swarm Simulation System",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded" # Автоматически открывает сайдбар на смартфонах!
)

st.markdown("""
    <style>
    /* 1. Фон приложения */
    .stApp { background-color: #0a0e14 !important; }

    /* 2. Полное скрытие всех системных плашек и подвалов */
    footer, [data-testid="stFooter"], div[class*="stAppFooter"], 
    div[class*="viewerBadge"], [data-testid="stStatusWidget"],
    header [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    /* 3. Гарантируем показ кнопки открытия боковой панели (стрелочки >) */
    [data-testid="collapsedControl"], [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        color: #00ffcc !important;
        background-color: #121820 !important;
        border: 1px solid #00ffcc !important;
        border-radius: 6px !important;
        z-index: 999999 !important;
    }

    /* Стилизация цифр в метриках */
    div[data-testid="stMetricValue"] { color: #00ffcc; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)

# 2. Класс агента (сохранен 1 в 1)
class Agent:
    def __init__(self, agent_id, x, y):
        self.id = agent_id
        self.x = x
        self.y = y
        self.threshold = random.randint(25, 75)
        self.state = "PATROL"
        self.vx = random.choice([-2, -1, 1, 2])
        self.vy = random.choice([-2, -1, 1, 2])

    def update(self, mode, connection_ok, risk_center_x, risk_center_y, risk_radius, current_stimulus):
        dist_to_risk = math.hypot(self.x - risk_center_x, self.y - risk_center_y)
        if dist_to_risk <= risk_radius:
            local_stimulus = current_stimulus * (1 - dist_to_risk / risk_radius)
        else:
            local_stimulus = 0

        if mode == "Decentralized" or connection_ok:
            if local_stimulus >= self.threshold + 20:
                self.state = "ALERT"
            elif local_stimulus >= self.threshold:
                self.state = "RESPOND"
            elif local_stimulus >= 15:
                self.state = "CHECK"
            else:
                self.state = "PATROL"
        else:
            self.state = "NO_SIGNAL"

        if self.state in ["RESPOND", "ALERT"]:
            angle = math.atan2(risk_center_y - self.y, risk_center_x - self.x)
            self.x += math.cos(angle) * 2.5
            self.y += math.sin(angle) * 2.5
        elif self.state == "CHECK":
            angle = math.atan2(risk_center_y - self.y, risk_center_x - self.x)
            self.x += math.cos(angle) * 1.2
            self.y += math.sin(angle) * 1.2
        elif self.state == "PATROL":
            self.x += self.vx
            self.y += self.vy
            if self.x < 10 or self.x > 570:
                self.vx *= -1
            if self.y < 10 or self.y > 370:
                self.vy *= -1

# 3. Инициализация состояния (Session State)
if "agents" not in st.session_state:
    st.session_state.agents = [Agent(i, random.randint(50, 540), random.randint(50, 340)) for i in range(20)]
if "time_history" not in st.session_state:
    st.session_state.time_history = []
    st.session_state.active_history = []
    st.session_state.log_data = []
    st.session_state.start_time = time.time()
    st.session_state.is_running = False

# Заголовок
st.title("🌊 FLOOD SWARM SYSTEM // NORTHERN KAZAKHSTAN")

# 4. Боковая панель (Controls)
st.sidebar.header("⚙️ Панель управления")

mode = st.sidebar.radio("MODE:", ["Decentralized", "Centralized"])
conn_status = st.sidebar.checkbox("CONNECTION STATUS [ONLINE]", value=True)

st.sidebar.subheader("Параметры среды")
w_val = st.sidebar.slider("Water (W):", 0, 100, 50)
r_val = st.sidebar.slider("Rate (R):", 0, 100, 40)
i_val = st.sidebar.slider("Ice Jam (I):", 0, 100, 60)

# Расчет стимула
stimulus = 0.33 * w_val + 0.33 * r_val + 0.34 * i_val

# Кнопки управления
col_btn1, col_btn2, col_btn3 = st.sidebar.columns(3)
if col_btn1.button("▶ START"):
    st.session_state.is_running = True
    st.session_state.start_time = time.time()
if col_btn2.button("⏸ PAUSE"):
    st.session_state.is_running = False
if col_btn3.button("↺ RESET"):
    st.session_state.is_running = False
    st.session_state.agents = [Agent(i, random.randint(50, 540), random.randint(50, 340)) for i in range(20)]
    st.session_state.time_history = []
    st.session_state.active_history = []
    st.session_state.log_data = []

# 5. Отрисовка шапки с метриками
m1, m2, m3, m4 = st.columns(4)
m1.metric("STIMULUS S", f"{stimulus:.1f}")
m2.metric("РЕЖИМ", mode)
m3.metric("СВЯЗЬ", "ONLINE" if conn_status else "OFFLINE")

# Обновление состояния агентов, если симуляция запущенна
risk_x, risk_y, risk_radius = 290, 190, 120
active_count = 0

if st.session_state.is_running:
    for agent in st.session_state.agents:
        agent.update(mode, conn_status, risk_x, risk_y, risk_radius, stimulus)
    
    elapsed = time.time() - st.session_state.start_time
    st.session_state.time_history.append(elapsed)
    
    # Считаем активных агентов
    active_count = sum(1 for a in st.session_state.agents if a.state in ["RESPOND", "ALERT"])
    st.session_state.active_history.append(active_count)
    
    st.session_state.log_data.append([
        round(elapsed, 2), mode, "ONLINE" if conn_status else "OFFLINE", round(stimulus, 1), active_count
    ])
else:
    active_count = sum(1 for a in st.session_state.agents if a.state in ["RESPOND", "ALERT"])

m4.metric("ACTIVE AGENTS", f"{active_count} / 20")

# 6. Визуализация Карты (Matplotlib Canvas)
col_left, col_right = st.columns([1.2, 1])

with col_left:
    fig_map, ax_map = plt.subplots(figsize=(6, 4), facecolor="#121820")
    ax_map.set_facecolor("#0d1117")
    
    # 1. Река
    x_river = np.linspace(0, 600, 200)
    y_river = 200 + 15 * np.sin(x_river / 60.0)
    river_w = 2 + (w_val / 100.0) * 8
    ax_map.plot(x_river, y_river, color="#0066ff", linewidth=river_w, alpha=0.8)

    # 2. Стрелки течения
    if r_val > 5:
        for xb in range(0, 600, 60):
            yb = 200 + 15 * np.sin(xb / 60.0)
            ax_map.text(xb, yb, ">>", color="#00ffff", fontsize=6 + (r_val/100)*4, fontweight="bold", ha="center", va="center")

    # 3. Ледяной затор (Ice Jam)
    if i_val > 10:
        num_ice = int(1 + (i_val / 100.0) * 8)
        random.seed(42)
        for _ in range(num_ice):
            ix = risk_x + random.randint(-40, 40)
            iy = (200 + 15 * math.sin(ix / 60.0)) + random.randint(-5, 5)
            ax_map.scatter(ix, iy, marker="D", color="#e0ffff", edgecolors="#00e5ff", s=30)

    # 4. Деревни
    ax_map.add_patch(plt.Rectangle((40, 40), 70, 40, color="#121820", ec="#00ffcc"))
    ax_map.text(75, 60, "VILLAGE A", color="#00ffcc", fontsize=7, fontweight="bold", ha="center", va="center")
    
    ax_map.add_patch(plt.Rectangle((470, 300), 80, 40, color="#121820", ec="#00ffcc"))
    ax_map.text(510, 320, "VILLAGE B", color="#00ffcc", fontsize=7, fontweight="bold", ha="center", va="center")

    # 5. Зона риска
    risk_circle = plt.Circle((risk_x, risk_y), risk_radius, color="#ff0055", fill=False, linestyle="--", linewidth=1.5)
    ax_map.add_patch(risk_circle)
    ax_map.text(risk_x, risk_y - 15, f"RISK ZONE\n(S={stimulus:.1f})", color="#ffea00", fontsize=7, fontweight="bold", ha="center")

    # 6. Агенты
    colors = {"PATROL": "#00ffcc", "CHECK": "#ffea00", "RESPOND": "#ff9100", "ALERT": "#ff0055", "NO_SIGNAL": "#707070"}
    for agent in st.session_state.agents:
        c = colors[agent.state]
        ax_map.scatter(agent.x, agent.y, color=c, s=25, zorder=5)
        ax_map.text(agent.x, agent.y + 12, f"θ={agent.threshold}", color="white", fontsize=5, ha="center")

    ax_map.set_xlim(0, 600)
    ax_map.set_ylim(0, 400)
    ax_map.invert_yaxis()  # Сохраняем ориентацию координат Tkinter
    ax_map.axis("off")
    
    st.pyplot(fig_map)

# 7. Правая секция (График динамики)
with col_right:
    fig_graph, ax_graph = plt.subplots(figsize=(5, 3.2), facecolor="#121820")
    ax_graph.set_facecolor("#0d1117")
    ax_graph.set_title("REAL-TIME SWARM DYNAMICS", color="#00ffcc", fontsize=9, fontweight="bold")
    ax_graph.set_xlabel("Time (s)", color="#808080", fontsize=7)
    ax_graph.set_ylabel("Active Agents", color="#808080", fontsize=7)
    ax_graph.tick_params(colors="#808080", labelsize=7)
    
    for spine in ax_graph.spines.values():
        spine.set_color("#00ffcc")
        
    ax_graph.set_ylim(0, 20)
    if st.session_state.time_history:
        ax_graph.plot(st.session_state.time_history, st.session_state.active_history, color="#ff0055", linewidth=2)
        ax_graph.set_xlim(0, max(10, st.session_state.time_history[-1]))
    else:
        ax_graph.set_xlim(0, 10)
        
    st.pyplot(fig_graph)

    # Кнопка экспорта CSV
    if st.session_state.log_data:
        df = pd.DataFrame(st.session_state.log_data, columns=["Time_s", "Coordination_Mode", "Connection_Status", "Stimulus_S", "Active_Agents"])
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 EXPORT CSV DATA", data=csv_bytes, file_name="flood_swarm_experiment_results.csv", mime="text/csv")

# 8. Автоперерисовка экрана при запущенной симуляции
if st.session_state.is_running:
    time.sleep(0.05)
    st.rerun()
