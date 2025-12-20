import os
from dotenv import load_dotenv
import streamlit as st
from supabase import create_client, Client
from streamlit.errors import StreamlitSecretNotFoundError

# ローカル用
load_dotenv()


def _get_secret(key: str) -> str | None:
    """
    優先順位:
    1. ローカル実行時: .env
    2. Streamlit Cloud: st.secrets
    """

    # ① ローカル（.env）を最優先
    value = os.getenv(key)
    if value:
        return value

    # ② Streamlit Cloud（secrets）
    try:
        if key in st.secrets:
            return str(st.secrets[key])
    except StreamlitSecretNotFoundError:
        # ローカルで secrets.toml が無い場合は無視
        pass

    return None


def get_supabase_client() -> Client:
    url = _get_secret("SUPABASE_URL")
    anon_key = _get_secret("SUPABASE_ANON_KEY")

    if not url or not anon_key:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_ANON_KEY が未設定です。"
            "（.env または Streamlit secrets を確認してください）"
        )

    return create_client(url, anon_key)
