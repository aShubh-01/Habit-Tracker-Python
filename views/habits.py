"""
views/habits.py — Manage the Habits Library (v2)
"""
import streamlit as st
from utils.styles import page_header, card, st_html
from utils.icons import render_icon, ICONS, ICON_EMOJIS
from config import CATEGORIES, CATEGORY_COLORS
from services.habit_service import get_habits, create_habit, update_habit, delete_habit


AVAILABLE_SYMBOLS = list(ICONS.keys())
# Filter out non-category icons from selection to keep it clean, but keep checks/locks out of default list
HABIT_SYMBOLS = [sym for sym in AVAILABLE_SYMBOLS if sym not in ["check", "lock", "lock-open", "trash", "plus"]]


def render_habits():
    user = st.session_state["user"]
    user_id = user["id"]

    page_header("📋 Habits Library", "Manage your reusable habits. Add them to your calendar on the Schedule page.")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_list, tab_add = st.tabs(["📋 View Library", "➕ Add Habit to Library"])

    # ── View Library Tab ──────────────────────────────────────────────────────
    with tab_list:
        habits = get_habits(user_id)
        if not habits:
            st.info("Your library is empty. Go to the **Add Habit** tab to create your first habit!")
        else:
            col_filter, _ = st.columns([2, 2])
            with col_filter:
                cat_filter = st.selectbox("Filter by Category", ["All"] + CATEGORIES)
            
            filtered_habits = habits
            if cat_filter != "All":
                filtered_habits = [h for h in habits if h["category"] == cat_filter]

            if not filtered_habits:
                st.write("No habits found in this category.")
            else:
                for h in filtered_habits:
                    color = h.get("color") or CATEGORY_COLORS.get(h["category"], "#6366F1")
                    symbol_html = render_icon(h.get("symbol", "star"), color=color, size=32)
                    
                    with st.expander(f"{h['name']} ({h['category']})"):
                        # Show habit details in a nice full-width card
                        st_html(f"""
                        <div style="display:flex; align-items:center; gap:16px; margin-bottom:16px; padding: 12px; background: #FFFFFF; border-radius: 8px; border: 1px solid #E5E7EB; border-left: 4px solid {color};">
                            <div style="background: #F3F4F6; padding: 8px; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                                {symbol_html}
                            </div>
                            <div style="flex: 1;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <strong style="font-size:1.15rem; color:#1C1C1E;">{h['name']}</strong>
                                    <span style="font-size:0.82rem; color:#6B7280; background:#E5E7EB; padding: 2px 8px; border-radius: 12px; font-weight: 500;">{h['category']}</span>
                                </div>
                                <p style="color:#4B5563; font-size:0.9rem; margin: 6px 0 0;">{h.get('description', '') or 'No description provided.'}</p>
                                <div style="font-size:0.8rem; color:#6366F1; font-weight: 600; margin-top: 6px;">🎯 {h.get('points', 10)} points rewarded on completion</div>
                            </div>
                        </div>
                        """)
                        
                        st.markdown("**✏️ Edit Habit Details**")
                        
                        col_e1, col_e2, col_e3 = st.columns([2, 1.5, 1.5])
                        with col_e1:
                            edit_name = st.text_input("Name", value=h["name"], key=f"edit_name_{h['id']}")
                            edit_desc = st.text_area("Description", value=h.get("description", ""), key=f"edit_desc_{h['id']}", max_chars=200, height=125)
                        with col_e2:
                            edit_cat = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(h["category"]), key=f"edit_cat_{h['id']}")
                            edit_sym = st.selectbox("Symbol Icon", HABIT_SYMBOLS, index=HABIT_SYMBOLS.index(h.get("symbol", "star")), format_func=lambda s: ICON_EMOJIS.get(s, s), key=f"edit_sym_{h['id']}")
                        with col_e3:
                            edit_points = st.number_input("Completion Points", min_value=1, max_value=100, value=h.get("points", 10), key=f"edit_pts_{h['id']}")
                            default_col = h.get("color") or CATEGORY_COLORS.get(edit_cat, "#6366F1")
                            edit_color = st.color_picker("Accent Color", value=default_col, key=f"edit_col_{h['id']}")
                        
                        st.write("")
                        col_btn1, col_btn2, _ = st.columns([1.5, 1.5, 5])
                        with col_btn1:
                            if st.button("💾 Save Changes", key=f"save_btn_{h['id']}", use_container_width=True):
                                if not edit_name.strip():
                                    st.error("Name is required.")
                                else:
                                    update_habit(h["id"], {
                                        "name": edit_name.strip(),
                                        "description": edit_desc.strip(),
                                        "category": edit_cat,
                                        "symbol": edit_sym,
                                        "points": int(edit_points),
                                        "color": edit_color
                                    })
                                    st.success("Habit updated!")
                                    st.rerun()
                        with col_btn2:
                            if st.button("🗑️ Delete", key=f"del_btn_{h['id']}", use_container_width=True):
                                delete_habit(h["id"])
                                st.warning("Habit deleted.")
                                st.rerun()

    # ── Add Habit Tab ────────────────────────────────────────────────────────
    with tab_add:
        st.markdown("### Create a New Habit")
        st.write("Define a habit once here, then schedule it for any day or time on the **Schedule** page.")
        
        with st.form("add_habit_form_v2"):
            name = st.text_input("Habit Name *", placeholder="e.g. Learn Python, Morning Meditation, Run 5K")
            description = st.text_area("Description / Intention", placeholder="What are the details of this routine?", max_chars=300)
            
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox("Category", CATEGORIES)
                points = st.number_input("Points on Completion", min_value=1, max_value=100, value=10, help="Points spent to claim rewards in the Reward Shop.")
            
            with col2:
                symbol = st.selectbox("Monochrome Icon", HABIT_SYMBOLS, index=0, format_func=lambda s: ICON_EMOJIS.get(s, s))
                # Show chosen icon preview dynamically below form or in a header.
                default_color = CATEGORY_COLORS.get(category, "#6366F1")
                color = st.color_picker("Accent Color (Optional)", value=default_color)

            st.write("")
            submitted = st.form_submit_button("🌱 Add to Library", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.error("Habit name is required.")
                else:
                    create_habit(user_id, name, description, category, symbol, int(points), color)
                    st.success(f"Habit **{name}** added to your library! Proceed to the **Schedule** tab to plan it.")
                    st.rerun()
