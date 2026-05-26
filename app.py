"""
app.py — Routine Planner & Habit Checklist Entrypoint
Streamlit app run command: streamlit run app.py
"""
import streamlit as st

# ─── Page config MUST be first ───────────────────────────────────────────────
st.set_page_config(
    page_title="Routine Planner",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styles import inject_styles, st_html, xp_bar
inject_styles()


# ─── Cookie-based session ─────────────────────────────────────────────────────
from extra_streamlit_components import CookieManager

# CookieManager must be instantiated at module level (before any other st calls)
cookie_manager = CookieManager()

from config import JWT_COOKIE_NAME
from services.auth_service import validate_token


def _load_session():
    """Read JWT from cookie and validate. Populates st.session_state['user']."""
    if "user" not in st.session_state or st.session_state.get("user") is None:
        token = cookie_manager.get(JWT_COOKIE_NAME)
        if token:
            user = validate_token(token)
            if user:
                st.session_state["user"] = user
                st.session_state["token"] = token
            else:
                # Token expired or invalid — clear it
                cookie_manager.delete(JWT_COOKIE_NAME)
                st.session_state["user"] = None
        else:
            st.session_state["user"] = None


def _render_sidebar(user: dict):
    """Sidebar navigation."""
    with st.sidebar:
        # Brand Header
        st_html("""
        <div style="text-align:center; padding:1.25rem 0 0.75rem;">
            <div style="font-size:2.8rem; line-height: 1;">🗓️</div>
            <div style="font-weight:800; color:#1C1C1E; font-size:1.15rem; margin-top:8px;">Routine Planner</div>
            <div style="color:#6B7280; font-size:0.75rem;">Streamline your days</div>
        </div>
        """)

        # User Profile Indicator
        from utils.helpers import get_level_info
        li = get_level_info(user.get("xp", 0))
        display = user.get("display_name") or user.get("username", "User")
        st_html(f"""
        <div style="background:rgba(99,102,241,0.06); border:1px solid rgba(99,102,241,0.15);
                    border-radius:8px; padding:0.6rem 0.85rem; margin-bottom:0.75rem;">
            <div style="font-weight:600; color:#1C1C1E; font-size:0.88rem;">{display}</div>
            <div style="font-size:0.72rem; color:#6366F1; font-weight: 500; margin-top: 2px; margin-bottom: 4px;">
                ⭐ Lv. {li['level']} · {li['title']} · {user.get('points',0):,} pts
            </div>
            {xp_bar(li['pct'], li['xp_in_level'], li['xp_for_level'])}
        </div>
        """)

        # Navigation
        nav_items = [
            "📅 Today Checklist",
            "📋 Habits Library",
            "🗓️ Routine Planner",
            "🛍️ Reward Shop",
            "📊 Analytics & Stats",
            "👤 Profile & Level",
            "⚙️ Settings",
        ]

        PAGE_KEY_MAP = {
            "📅 Today Checklist":   "today",
            "📋 Habits Library":     "habits",
            "🗓️ Routine Planner":   "schedule",
            "🛍️ Reward Shop":       "rewards",
            "📊 Analytics & Stats": "stats",
            "👤 Profile & Level":   "profile",
            "⚙️ Settings":           "settings",
        }

        current = st.session_state.get("current_page", "today")
        current_label = next((k for k, v in PAGE_KEY_MAP.items() if v == current), nav_items[0])

        selected = st.radio(
            "Navigation",
            nav_items,
            index=nav_items.index(current_label) if current_label in nav_items else 0,
            label_visibility="collapsed",
        )
        st.session_state["current_page"] = PAGE_KEY_MAP[selected]

        st.divider()

        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            cookie_manager.delete(JWT_COOKIE_NAME)
            st.session_state.clear()
            st.rerun()


def _render_page(page_key: str):
    """Dispatch to the correct view module."""
    if page_key == "today":
        from views.today import render_today
        render_today()
    elif page_key == "habits":
        from views.habits import render_habits
        render_habits()
    elif page_key == "schedule":
        from views.schedule import render_schedule
        render_schedule()
    elif page_key == "rewards":
        from views.rewards import render_rewards
        render_rewards()
    elif page_key == "stats":
        from views.stats import render_stats
        render_stats()
    elif page_key == "profile":
        from views.profile import render_profile
        render_profile()
    elif page_key == "settings":
        from views.settings import render_settings
        render_settings()
    else:
        from views.today import render_today
        render_today()


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    _load_session()

    user = st.session_state.get("user")

    if user is None:
        # Check DB connectivity first
        from db.database import ping
        ok, err = ping()
        if not ok:
            st.error(f"⚠️ Cannot connect to MongoDB: {err}")
            st.info("Please check your `MONGODB_URL` in `.env` and restart the app.")
            st.code("MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/habit_tracker", language="bash")
            st.stop()

        from views.auth import render_auth
        render_auth(cookie_manager)
    else:
        _render_sidebar(user)
        page = st.session_state.get("current_page", "today")
        _render_page(page)


main()
