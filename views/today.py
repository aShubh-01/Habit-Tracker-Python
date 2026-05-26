"""
views/today.py — Today's schedule checklist (v2)
"""
import streamlit as st
from datetime import datetime, date, timedelta
from utils.styles import page_header, card, st_html
from utils.icons import render_icon
from utils.helpers import format_ampm
from config import CATEGORY_COLORS

from services.schedule_service import get_schedule, toggle_completion


def render_today():
    user = st.session_state["user"]
    user_id = user["id"]
    today_str = date.today().isoformat()
    formatted_date = date.today().strftime("%A, %B %d, %Y")

    page_header("📅 Today's Schedule", f"Track and complete your schedule for {formatted_date}")

    # Fetch today's schedule
    schedule = get_schedule(user_id, today_str)

    # ── Summary Metrics Row ──────────────────────────────────────────────────
    total_slots = len(schedule)
    completed_slots = sum(1 for item in schedule if item["completed"])
    
    # Calculate past due slots
    past_due_slots = 0
    for item in schedule:
        if not item["completed"]:
            try:
                task_end_dt = datetime.strptime(f"{item['date']} {item['end_time']}", "%Y-%m-%d %H:%M")
                if datetime.now() > task_end_dt:
                    past_due_slots += 1
            except Exception:
                pass

    col_points, col_multiplier, col_progress = st.columns([1, 1, 2])
    with col_points:
        st.metric("Total Points", f"{user.get('points', 0)} pts")
    with col_multiplier:
        streak = user.get("consistency_streak", 0)
        mult = user.get("multiplier", 1.0)
        st.metric("Streak Multiplier", f"{mult}x", f"{streak} day perfect streak")
    with col_progress:
        if total_slots > 0:
            pct = int((completed_slots / total_slots) * 100)
            status_text = f"{pct}% completed"
            if past_due_slots > 0:
                status_text += f" ({past_due_slots} past due)"
            st.metric("Today's Progress", f"{completed_slots} / {total_slots} Done", status_text)
        else:
            st.metric("Today's Progress", "0 / 0", "No habits scheduled")

    st.write("")

    # ── Empty State ──────────────────────────────────────────────────────────
    if not schedule:
        st.info("Nothing scheduled for today yet. Use the **Schedule** tab to plan your day!")
        return

    # ── Checklist ────────────────────────────────────────────────────────────
    for item in schedule:
        color = item.get("habit_color", "#6366F1")
        symbol_name = item.get("habit_symbol", "star")
        
        # Status indicators
        is_done = item["completed"]
        is_past = False
        if not is_done:
            try:
                task_end_dt = datetime.strptime(f"{item['date']} {item['end_time']}", "%Y-%m-%d %H:%M")
                if datetime.now() > task_end_dt:
                    is_past = True
            except Exception:
                pass
        
        # Determine card border accent and state
        if is_done:
            accent_color = "#10B981" # Success green
        elif is_past:
            accent_color = "#EF4444" # Past due red
        else:
            accent_color = color # Indigo or category color

        symbol_html = render_icon(symbol_name, color=accent_color, size=32)

        # Build card text
        time_slot = f"{format_ampm(item['start_time'])} – {format_ampm(item['end_time'])}"
        if is_done:
            time_slot += " [✓ Done]"
        elif is_past:
            time_slot += " [⚠️ Past Due]"
            
        desc_text = f"<p style='margin: 4px 0 0; font-size: 0.85rem; color:#6B7280;'>{item['habit_description']}</p>" if item['habit_description'] else ""

        col_card, col_action = st.columns([5, 1.2])

        with col_card:
            card_content = f"""
            <div style="display: flex; align-items: center; gap: 14px;">
                <div>{symbol_html}</div>
                <div style="flex: 1;">
                    <div style="font-size: 0.78rem; font-weight: 600; color: {accent_color}; text-transform: uppercase; letter-spacing: 0.05em;">{time_slot}</div>
                    <div style="font-weight: 700; font-size: 1.1rem; color: #1C1C1E; margin-top: 2px;">
                        {item['habit_name']}
                    </div>
                    {desc_text}
                </div>
            </div>
            """
            st_html(card(card_content, color_accent=accent_color))

        with col_action:
            st.write("") # push down slightly
            if is_done:
                # Show complete, and allow unticking
                if st.button("✓ Completed", key=f"tick_{item['id']}", use_container_width=True):
                    toggle_completion(item["id"], user_id)
                    # Refresh session state user stats
                    from services.auth_service import get_user_by_id
                    st.session_state["user"] = get_user_by_id(user_id)
                    st.rerun()
            else:
                # Show incomplete button (even if past due, user can tick whenever they want)
                btn_label = "⚠️ Complete" if is_past else "○ Complete"
                if st.button(btn_label, key=f"untick_{item['id']}", use_container_width=True):
                    toggle_completion(item["id"], user_id)
                    # Refresh session state user stats
                    from services.auth_service import get_user_by_id
                    st.session_state["user"] = get_user_by_id(user_id)
                    st.rerun()
