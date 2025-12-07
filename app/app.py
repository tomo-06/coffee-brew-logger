# app/app.py
import time
import datetime

import streamlit as st

st.set_page_config(page_title="Coffee Brew Logger", page_icon="☕", layout="centered")

st.title("Coffee Brew Logger ☕")
st.caption("抽出条件＋タイマー付きの簡易ログアプリ（MVP）")

# --- ユーザー選択 ---
st.subheader("誰が淹れている？")
user = st.radio("ユーザー", ["自分", "友人"], horizontal=True)

# 内部的なID化（あとでDBに入れる時に使いやすくする）
user_id = "me" if user == "自分" else "friend"

st.divider()

# --- タイマー機能 ---
st.subheader("抽出タイマー")

if "timer_start" not in st.session_state:
    st.session_state["timer_start"] = None
if "total_time_sec" not in st.session_state:
    st.session_state["total_time_sec"] = None

col1, col2 = st.columns(2)

with col1:
    if st.button("▶ START"):
        st.session_state["timer_start"] = time.time()
        st.session_state["total_time_sec"] = None
        st.success("タイマーを開始しました")

with col2:
    if st.button("⏹ STOP"):
        if st.session_state["timer_start"] is None:
            st.warning("先に START を押してください")
        else:
            elapsed = int(time.time() - st.session_state["timer_start"])
            st.session_state["total_time_sec"] = elapsed
            st.session_state["timer_start"] = None
            st.success(f"総抽出時間: {elapsed} 秒")

# 現在の状態表示
if st.session_state["timer_start"] is not None:
    st.info("計測中... STOP を押すと総抽出時間が記録されます")
elif st.session_state["total_time_sec"] is not None:
    st.write(f"⏱ 計測結果: **{st.session_state['total_time_sec']} 秒**")

st.divider()

# --- 抽出条件フォーム ---
st.subheader("抽出条件の記録")

with st.form("brew_form"):
    # 抽出日（デフォルトは今日）
    brewed_at = st.date_input("抽出日", value=datetime.date.today())

    bean_name = st.text_input("豆の名前（例：エチオピア ナチュラル）")
    roaster = st.text_input("ロースター（お店の名前）", placeholder="任意")

    roast_level = st.selectbox(
        "焙煎度",
        ["未選択", "浅煎り", "中煎り", "中深煎り", "深煎り"],
        index=2,
    )

    method = st.selectbox(
        "抽出方法",
        ["未選択", "V60ドリッパー", "カリタウェーブ", "フレンチプレス", "エアロプレス", "エスプレッソ", "その他"],
    )

    grind_size = st.selectbox(
        "挽き目",
        ["未選択", "極細挽き", "細挽き", "中細挽き", "中挽き", "中粗挽き", "粗挽き"],
        index=3,
    )

    dose_g = st.number_input("豆の量 (g)", min_value=0.0, max_value=50.0, value=15.0, step=0.5)
    water_ml = st.number_input("お湯の量 (ml)", min_value=0, max_value=1000, value=230, step=10)
    water_temp_c = st.number_input("お湯の温度 (℃)", min_value=70, max_value=100, value=93, step=1)

    # タイマー結果をフォームに反映（編集したければユーザーが上書きも可能）
    total_time_sec = st.number_input(
        "総抽出時間 (秒)",
        min_value=0,
        max_value=1200,
        value=st.session_state["total_time_sec"] or 0,
        step=1,
    )

    rating = st.slider("味の評価", min_value=1, max_value=5, value=4)
    notes = st.text_area("味のメモ", placeholder="例：明るい酸、後味すっきり、チョコっぽい甘さ など")

    submitted = st.form_submit_button("記録する")

if submitted:
    # ここでDB保存をする予定（今は画面表示だけ）
    st.success("記録しました ✅（今は画面表示のみ。あとでDB保存処理を追加します）")

    st.json(
        {
            "user_id": user_id,
            "brewed_at": str(brewed_at),
            "bean_name": bean_name,
            "roaster": roaster,
            "roast_level": roast_level,
            "method": method,
            "grind_size": grind_size,
            "dose_g": dose_g,
            "water_ml": water_ml,
            "water_temp_c": water_temp_c,
            "total_time_sec": total_time_sec,
            "rating": rating,
            "notes": notes,
        }
    )

    # 1回記録したらタイマー結果はリセットしておく
    st.session_state["total_time_sec"] = None
