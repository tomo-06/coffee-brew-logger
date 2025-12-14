import os
from dotenv import load_dotenv
import streamlit as st
from supabase import create_client, Client

load_dotenv()

def _get_secret(key: str) -> str | None:
    # Streamlit Cloudでは st.secrets に入る
    if hasattr(st, "secrets") and key in st.secrets:
        return str(st.secrets[key])
    return os.getenv(key)

def get_supabase_client() -> Client:
    url = _get_secret("SUPABASE_URL")
    key = _get_secret("SUPABASE_ANON_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_ANON_KEY が未設定です（Secrets または .env を確認してください）"
        )

    return create_client(url, key)
