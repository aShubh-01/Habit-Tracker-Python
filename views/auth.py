"""
views/auth.py — Login and Signup page (v2)
"""
import streamlit as st
import textwrap
from services.auth_service import signup, login
from config import JWT_COOKIE_NAME, JWT_EXPIRY_DAYS
from utils.styles import st_html


def render_auth(cookie_manager):
    """Render login/signup and handle JWT cookie on success."""

    # Center the auth card
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st_html("""
        <div style="text-align:center; padding:2rem 0 1.5rem;">
            <div style="font-size:3.8rem; line-height: 1;">🗓️</div>
            <h1 style="color:#1C1C1E; font-size:1.8rem; font-weight:800; margin:12px 0 4px; letter-spacing:-0.02em;">Routine Planner</h1>
            <p style="color:#6B7280; font-size:0.9rem; margin-top:2px;">Streamline your routines, habits, and daily schedules.</p>
        </div>
        """)

        tab_login, tab_signup = st.tabs(["🔑 Login", "✨ Sign Up"])

        # ── Login ──────────────────────────────────────────────────────
        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="your username")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Login", use_container_width=True)

                if submitted:
                    if not username or not password:
                        st.error("Please fill in all fields.")
                    else:
                        user, result = login(username, password)
                        if user:
                            _set_auth(cookie_manager, result, user)
                        else:
                            st.error(result)

            st_html("""
            <p style="color:#6B7280; font-size:0.82rem; text-align:center; margin-top:0.75rem;">
                Demo Account: <b style="color:#6366F1;">demo</b> / <b style="color:#6366F1;">demo123</b>
            </p>
            """)

        # ── Sign Up ────────────────────────────────────────────────────
        with tab_signup:
            with st.form("signup_form"):
                new_username = st.text_input("Username", placeholder="choose a username", key="su_user")
                new_email    = st.text_input("Email (optional)", placeholder="you@example.com", key="su_email")
                new_password = st.text_input("Password", type="password", placeholder="min. 6 characters", key="su_pass")
                new_confirm  = st.text_input("Confirm Password", type="password", placeholder="repeat password", key="su_conf")
                submitted_su = st.form_submit_button("Create Account", use_container_width=True)

                if submitted_su:
                    if not new_username or not new_password:
                        st.error("Username and password are required.")
                    elif new_password != new_confirm:
                        st.error("Passwords do not match.")
                    else:
                        user, result = signup(new_username, new_password, new_email)
                        if user:
                            st.success("Account created! Logging you in…")
                            _set_auth(cookie_manager, result, user)
                        else:
                            st.error(result)


def _set_auth(cookie_manager, token: str, user: dict):
    """Store JWT in cookie and session state, then rerun."""
    from datetime import datetime, timedelta
    expires_at = datetime.now() + timedelta(days=JWT_EXPIRY_DAYS)
    cookie_manager.set(JWT_COOKIE_NAME, token, expires_at=expires_at)
    st.session_state["user"] = user
    st.session_state["token"] = token
    st.rerun()

