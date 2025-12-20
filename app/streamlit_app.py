# app/app.py
import time
import datetime
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from auth import require_login, logout
from supabase_client import get_supabase_client


# =========================
# Page config
# =========================
st.set_page_config(
    page_title="Coffee Brew Logger",
    page_icon="☕",
    layout="centered",
)

st.title("Coffee Brew Logger ☕")
st.caption("抽出条件＋タイマー付きの簡易ログアプリ（MVP）")


# =========================
# login管理
# =========================
supabase = get_supabase_client()
user = require_login(supabase)

with st.sidebar:
    st.write(f"ログイン中: {user.email}")
    if st.button("ログアウト"):
        logout(supabase)

user_id = user.id  # ★ これが auth.uid()


# =========================
# Session state 初期化
# =========================
if "timer_start" not in st.session_state:
    st.session_state["timer_start"] = None

if "total_time_sec" not in st.session_state:
    st.session_state["total_time_sec"] = None

if "flash" not in st.session_state:
    st.session_state["flash"] = None

if "do_reset" not in st.session_state:
    st.session_state["do_reset"] = False

if "set_timer_result" not in st.session_state:
    st.session_state["set_timer_result"] = None


# =========================
# フォーム初期値 & リセット
# =========================
FORM_DEFAULTS = {
    "brewed_at": datetime.date.today(),
    "bean_name": "",
    "roaster": "",
    "roast_level": "中煎り",
    "method": "ドリッパー",
    "grind_size": "中細挽き",
    "dose_g": 15.0,
    "water_ml": 200,
    "water_temp_c": 90,
    "drip_count": 1,
    "total_time_sec_input": 0,
    "rating": 4,
    "notes": "",
}

def reset_form():
    for k, v in FORM_DEFAULTS.items():
        st.session_state[k] = v

    st.session_state["timer_start"] = None
    st.session_state["total_time_sec"] = None


# =========================
# フラッシュメッセージ
# =========================
if st.session_state["flash"]:
    st.success(st.session_state["flash"])
    st.session_state["flash"] = None


# =========================
# ユーザー選択
# =========================
st.subheader("誰が淹れている？")
user = st.radio("ユーザー", ["自分", "友人"], horizontal=True)
user_id = "me" if user == "自分" else "friend"

st.divider()


# =========================
# タイマー
# =========================
# --- タイマー機能 ---
st.subheader("抽出タイマー")

col1, col2 = st.columns(2)

with col1:
    if st.button("▶ START"):
        st.session_state["timer_start"] = time.time()
        st.session_state["total_time_sec"] = None
        st.info("タイマーを開始しました")

with col2:
    if st.button("⏹ STOP"):
        if st.session_state["timer_start"] is None:
            st.warning("先に START を押してください")
        else:
            elapsed = int(time.time() - st.session_state["timer_start"])
            st.session_state["set_timer_result"] = elapsed
            st.session_state["total_time_sec"] = elapsed
            st.session_state["timer_start"] = None
            st.success(f"総抽出時間: {elapsed} 秒")

# 計測中は1秒ごとに自動更新（リアルタイム表示）
if st.session_state["timer_start"] is not None:
    st_autorefresh(interval=1000, key="timer_refresh")  # 1000ms = 1秒

    elapsed_now = int(time.time() - st.session_state["timer_start"])
    mm, ss = divmod(elapsed_now, 60)
    st.write(f"⏱ 計測中: **{mm:02d}:{ss:02d}**（{elapsed_now} 秒）")

    st.caption("STOP を押すと総抽出時間が記録されます")

elif st.session_state["total_time_sec"] is not None:
    st.write(f"✅ 計測結果: **{st.session_state['total_time_sec']} 秒**")

else:
    st.caption("START を押すと計測が始まります")


# =========================
# 抽出条件フォーム
# =========================
st.subheader("抽出条件の記録")

# 次回rerunの冒頭でフォームを初期化 or タイマー結果反映
if st.session_state["do_reset"]:
    reset_form()
    st.session_state["do_reset"] = False

if st.session_state["set_timer_result"] is not None:
    st.session_state["total_time_sec_input"] = st.session_state["set_timer_result"]
    st.session_state["set_timer_result"] = None


with st.form("brew_form"):
    brewed_at = st.date_input(
        "抽出日",
        key="brewed_at",
    )

    bean_name = st.text_input(
        "豆の名前（例：エチオピア ナチュラル）",
        key="bean_name",
    )

    roaster = st.text_input(
        "ロースター（お店の名前）",
        placeholder="任意",
        key="roaster",
    )

    roast_level = st.selectbox(
        "焙煎度",
        ["未選択", "浅煎り", "中煎り", "中深煎り", "深煎り"],
        key="roast_level",
    )

    method = st.selectbox(
        "抽出方法",
        [
            "未選択",
            "ドリッパー",
            "カリタウェーブ",
            "フレンチプレス",
            "エアロプレス",
            "エスプレッソ",
            "その他",
        ],
        key="method",
    )

    grind_size = st.selectbox(
        "挽き目",
        ["未選択", "極細挽き", "細挽き", "中細挽き", "中挽き", "中粗挽き", "粗挽き"],
        key="grind_size",
    )

    dose_g = st.number_input(
        "豆の量 (g)",
        min_value=0.0,
        max_value=50.0,
        step=0.5,
        key="dose_g",
    )

    water_ml = st.number_input(
        "お湯の量 (ml)",
        min_value=0,
        max_value=1000,
        step=10,
        key="water_ml",
    )

    water_temp_c = st.number_input(
        "お湯の温度 (℃)",
        min_value=70,
        max_value=100,
        step=1,
        key="water_temp_c",
    )

    drip_count = st.number_input(
        "ドリップ回数",
        min_value=1,
        max_value=10,
        step=1,
        key="drip_count",
    )

    total_time_sec = st.number_input(
        "総抽出時間 (秒)",
        min_value=0,
        max_value=1200,
        step=1,
        key="total_time_sec_input",
    )

    rating = st.slider(
        "味の評価",
        min_value=1,
        max_value=5,
        key="rating",
    )

    notes = st.text_area(
        "味のメモ",
        key="notes",
    )

    submitted = st.form_submit_button("記録する")


# =========================
# Supabase INSERT
# =========================
if submitted:
    supabase = get_supabase_client()

    brewed_at_dt = datetime.datetime.combine(
        brewed_at,
        datetime.time(0, 0),
    )

    payload = {
        "user_id": user_id,
        "brewed_at": brewed_at_dt.isoformat(),
        "bean_name": bean_name,
        "roaster": roaster or None,
        "roast_level": None if roast_level == "未選択" else roast_level,
        "method": None if method == "未選択" else method,
        "grind_size": None if grind_size == "未選択" else grind_size,
        "dose_g": float(dose_g),
        "water_ml": int(water_ml) if water_ml else None,
        "water_temp_c": int(water_temp_c) if water_temp_c else None,
        "drip_count": int(drip_count),
        "total_time_sec": int(total_time_sec),
        "rating": int(rating),
        "notes": notes or None,
    }

    try:
        supabase.table("brews").insert(payload).execute()

        st.session_state["flash"] = "記録しました ✅"
        st.session_state["do_reset"] = True
        st.rerun()


    except Exception as e:
        st.error("保存に失敗しました ❌")
        st.exception(e)