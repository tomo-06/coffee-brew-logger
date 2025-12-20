import streamlit as st
from supabase import Client

def require_login(supabase: Client):
    if "sb_user" not in st.session_state:
        st.session_state["sb_user"] = None

    if st.session_state["sb_user"] is not None:
        return st.session_state["sb_user"]

    st.subheader("ログイン")
    email = st.text_input("メールアドレス")
    password = st.text_input("パスワード", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("ログイン"):
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                st.session_state["sb_user"] = res.user
                st.rerun()
            else:
                st.error("ログインに失敗しました")

    with col2:
        st.caption("※ダミーメールでもOK（Confirm email OFFの場合）")

    st.stop()

def logout(supabase: Client):
    supabase.auth.sign_out()
    st.session_state.clear()
    st.rerun()
