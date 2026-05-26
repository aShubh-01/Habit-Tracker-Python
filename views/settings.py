"""
views/settings.py — Settings page: display name, password, account actions (v2)
"""
import streamlit as st
from utils.styles import page_header


def render_settings():
    user = st.session_state["user"]
    user_id = user["id"]

    page_header("⚙️ Settings", "Manage your account preferences and credentials.")

    from services.auth_service import update_user, get_user_by_id, delete_account, verify_password, hash_password

    tab_profile, tab_password, tab_danger = st.tabs(["👤 Profile Settings", "🔒 Password Change", "⚠️ Danger Zone"])

    # ── Profile Settings ──────────────────────────────────────────────────────
    with tab_profile:
        with st.form("settings_profile"):
            display_name = st.text_input("Display Name",
                                         value=user.get("display_name", user.get("username", "")))
            email = st.text_input("Email Address", value=user.get("email", ""), placeholder="you@example.com")
            saved = st.form_submit_button("💾 Save Changes", use_container_width=True)
            if saved:
                update_user(user_id, {"display_name": display_name.strip(), "email": email.strip().lower()})
                st.session_state["user"] = get_user_by_id(user_id)
                st.success("Profile updated successfully!")

    # ── Password Change ───────────────────────────────────────────────────────
    with tab_password:
        with st.form("settings_password"):
            current_pw = st.text_input("Current Password", type="password")
            new_pw     = st.text_input("New Password", type="password", placeholder="min. 6 characters")
            confirm_pw = st.text_input("Confirm New Password", type="password")
            change_btn = st.form_submit_button("🔒 Change Password", use_container_width=True)

            if change_btn:
                if not current_pw or not new_pw:
                    st.error("Please fill in all fields.")
                elif new_pw != confirm_pw:
                    st.error("New passwords do not match.")
                elif len(new_pw) < 6:
                    st.error("Password must be at least 6 characters long.")
                else:
                    # Verify current password
                    from db.database import get_collection
                    raw = get_collection("users").find_one({"_id": user_id})
                    if raw and verify_password(current_pw, raw.get("password_hash", "")):
                        update_user(user_id, {"password_hash": hash_password(new_pw)})
                        st.success("Password changed successfully!")
                    else:
                        st.error("Current password is incorrect.")

    # ── Danger Zone ───────────────────────────────────────────────────────────
    with tab_danger:
        st.error("⚠️ Actions in this section are permanent and cannot be undone!")

        with st.expander("🗑️ Delete Account"):
            st.error("This permanently deletes all your scheduled routines, habits library, and rewards history.")
            confirm_del = st.text_input("Type your username to confirm deletion", key="del_confirm")
            if st.button("Delete My Account", key="delete_account"):
                if confirm_del.lower() == user.get("username", "").lower():
                    delete_account(user_id)
                    st.session_state.clear()
                    st.rerun()
                else:
                    st.error("Username does not match.")

    st.divider()
    st.subheader("📋 System Details")
    st.markdown("""
    | Component | Details |
    |---|---|
    | **App** | Routine Tracker & Schedule Planner (v2) |
    | **Design** | Minimal Notion-like (Light Theme) |
    | **Database** | MongoDB |
    | **Authentication** | JWT Cookie (7-day duration) |
    | **Runtime** | Streamlit |
    """)
