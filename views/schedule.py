"""
views/schedule.py — Routine builder and calendar views (v2)
"""
import streamlit as st
from datetime import datetime, date, timedelta
from utils.styles import page_header, card, st_html
from utils.icons import render_icon, ICON_EMOJIS
from utils.helpers import format_ampm
from config import CATEGORY_COLORS, CATEGORIES
from services.habit_service import get_habits
from services.schedule_service import (
    create_schedule_entry, get_schedule, delete_schedule_entry,
    get_schedule_range
)
from db.database import get_collection


def get_week_range(d: date) -> tuple[date, date]:
    """Return Monday and Sunday of the week containing date d."""
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_hour_label(h: int) -> str:
    """Format hour integer into AM/PM label."""
    if h == 0: return "12 AM"
    if h == 12: return "12 PM"
    if h < 12: return f"{h} AM"
    return f"{h-12} PM"




@st.dialog("➕ Add Task to Schedule")
def show_add_task_modal(user_id: str, default_date: date):
    """Modal dialog to schedule a habit."""
    habits = get_habits(user_id)
    if not habits:
        st.warning("You must create habits in your library first!")
        if st.button("Go to Habits Library", key="modal_go_habits"):
            st.session_state["current_page"] = "habits"
            st.rerun()
        return

    habit_option = st.selectbox(
        "Choose Habit",
        habits,
        format_func=lambda h: f"{ICON_EMOJIS.get(h.get('symbol', 'star'), '⭐').split(' ')[0]} {h['name']} ({h['category']})",
        key="modal_habit"
    )

    selected_date = st.date_input("Date", value=default_date, key="modal_date")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        start_time = st.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M").time(), key="modal_start")
    with col_t2:
        end_time = st.time_input("End Time", value=datetime.strptime("10:00", "%H:%M").time(), key="modal_end")

    if st.button("🗓️ Schedule Task", use_container_width=True, key="modal_submit"):
        start_str = start_time.strftime("%H:%M")
        end_str = end_time.strftime("%H:%M")
        
        create_schedule_entry(
            user_id=user_id,
            habit_id=habit_option["id"],
            date_str=selected_date.isoformat(),
            start_time=start_str,
            end_time=end_str,
            auto_lock_enabled=False,
            auto_lock_hours=1
        )
        st.success("Added to schedule!")
        st.rerun()




def render_calendar_grid(schedule_items: list, view_mode: str, active_date: date):
    """Draw an absolute positioned scrollable HTML calendar grid with embedded actions."""
    row_height = 60
    total_grid_height = 24 * row_height
    
    # Hours lines and labels HTML
    lines_html = ""
    for h in range(24):
        label = get_hour_label(h)
        lines_html += f"""
        <div style="position: absolute; left: 55px; right: 0; top: {h * row_height}px; border-top: 1px dashed #E5E7EB; height: 0;"></div>
        <div style="position: absolute; left: 5px; width: 45px; top: {h * row_height - 7}px; font-size: 0.68rem; color: #9CA3AF; text-align: right;">{label}</div>
        """
        
    # Vertical grid separator lines (for week view)
    vertical_lines_html = ""
    if view_mode == "week":
        for i in range(1, 7):
            vertical_lines_html += f"""
            <div style="position: absolute; top: 0; bottom: 0; left: calc(55px + ({i} * (100% - 55px) / 7)); border-left: 1px solid #E5E7EB; width: 0;"></div>
            """
            
    # Task cards HTML
    tasks_html = ""
    for item in schedule_items:
        try:
            # Parse start and end times
            start_h, start_m = map(int, item["start_time"].split(":"))
            end_h, end_m = map(int, item["end_time"].split(":"))
            
            start_val = start_h + start_m / 60.0
            end_val = end_h + end_m / 60.0
            if end_val < start_val:
                end_val += 24.0
                
            top = start_val * row_height
            height = (end_val - start_val) * row_height
            
            # Position columns
            if view_mode == "today":
                left_css = "calc(55px + 4px)"
                width_css = "calc(100% - 55px - 8px)"
            else: # week view
                dt = datetime.strptime(item["date"], "%Y-%m-%d")
                weekday_idx = dt.weekday() # 0 = Mon, 6 = Sun
                left_css = f"calc(55px + {weekday_idx} * (100% - 55px) / 7 + 4px)"
                width_css = f"calc((100% - 55px) / 7 - 8px)"
                
            # Styling based on completion/lock state
            is_done = item.get("completed", False)
            is_past = False
            if not is_done:
                try:
                    task_end_dt = datetime.strptime(f"{item['date']} {item['end_time']}", "%Y-%m-%d %H:%M")
                    if datetime.now() > task_end_dt:
                        is_past = True
                except Exception:
                    pass
            
            color = item.get("habit_color", "#6366F1")
            
            if is_done:
                accent = "#10B981"
                bg = "#ECFDF5"
                text_col = "#065F46"
                border_style = "border: 1px solid #10B98140; border-left: 4px solid #10B981;"
                check_symbol = "🟢"
            elif is_past:
                accent = "#EF4444"
                bg = "#FEF2F2"
                text_col = "#991B1B"
                border_style = "border: 1px solid #EF444440; border-left: 4px solid #EF4444;"
                check_symbol = "🔴"
            else:
                accent = color
                bg = f"{color}0D"
                text_col = "#1C1C1E"
                border_style = f"border: 1px solid {color}40; border-left: 4px solid {color};"
                check_symbol = "⚪"
                
            tasks_html += f"""
            <div style="
                position: absolute;
                top: {top}px;
                height: {height - 2}px;
                left: {left_css};
                width: {width_css};
                background: {bg};
                {border_style}
                border-radius: 6px;
                padding: 4px 6px;
                font-size: 0.72rem;
                color: {text_col};
                overflow: hidden;
                box-shadow: 0 1px 2px rgba(0,0,0,0.02);
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                line-height: 1.1;
            ">
                <div style="width: 100%;">
                    <strong style="font-weight: 700; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; color: {text_col}; display: block;">
                        {item['habit_name']}
                    </strong>
                    <div style="font-size: 0.65rem; opacity: 0.8; margin-top: 1px; white-space: nowrap; overflow: hidden;">
                        {format_ampm(item['start_time'])} - {format_ampm(item['end_time'])}
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; justify-content: space-between; border-top: 1px solid {accent}30; padding-top: 3px; margin-top: 2px;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <a href="?action=toggle&id={item['id']}" target="_self" style="text-decoration: none; font-size: 0.75rem;" title="Toggle Completion">
                            {check_symbol}
                        </a>
                    </div>
                    <a href="?action=delete&id={item['id']}" target="_self" style="text-decoration: none; font-size: 0.7rem;" title="Delete Slot">
                        🗑️
                    </a>
                </div>
            </div>
            """
        except Exception:
            pass
            
    # Week header row if week view
    week_header_html = ""
    if view_mode == "week":
        monday, _ = get_week_range(active_date)
        cols_header_html = ""
        for i in range(7):
            d = monday + timedelta(days=i)
            day_lbl = d.strftime("%a %e")
            is_today = (d == date.today())
            bold_style = "color:#6366F1; font-weight:800;" if is_today else "color:#4B5563; font-weight:600;"
            cols_header_html += f"""
            <div style="flex: 1; text-align: center; font-size: 0.78rem; {bold_style}">{day_lbl}</div>
            """
        week_header_html = f"""
        <div style="display: flex; border-bottom: 1px solid #E5E7EB; background: #F9FAFB; padding: 6px 0; border-top-left-radius: 8px; border-top-right-radius: 8px;">
            <div style="width: 55px;"></div>
            {cols_header_html}
        </div>
        """
        
    grid_html = f"""
    {week_header_html}
    <div style="max-height: 520px; overflow-y: auto; position: relative; border: 1px solid #E5E7EB; border-radius: 8px; border-top-left-radius: 0; border-top-right-radius: 0; background: #FFFFFF; height: 540px;">
        <div style="position: relative; height: {total_grid_height}px; width: 100%;">
            {lines_html}
            {vertical_lines_html}
            {tasks_html}
        </div>
    </div>
    """
    st_html(grid_html)


def render_schedule():
    user = st.session_state["user"]
    user_id = user["id"]

    page_header("🗓️ Routine Planner", "Build your daily routine calendar. Assign habits to specific time slots.")


    # Initialize states
    if "schedule_active_date" not in st.session_state:
        st.session_state["schedule_active_date"] = date.today()
    if "schedule_view_mode" not in st.session_state:
        st.session_state["schedule_view_mode"] = "today"

    active_date = st.session_state["schedule_active_date"]

    # ── Header & Toolbar Area ────────────────────────────────────────────────
    col_sel_mode, col_add_task = st.columns([4, 1], vertical_alignment="center")
    
    with col_sel_mode:
        col_radio, col_nav = st.columns([1.5, 3.5], vertical_alignment="center")
        with col_radio:
            view_mode = st.radio(
                "View Mode Selector",
                ["Today", "Week"],
                index=0 if st.session_state["schedule_view_mode"] == "today" else 1,
                horizontal=True,
                label_visibility="collapsed",
                key="sched_view_mode_radio"
            )
            if view_mode.lower() != st.session_state["schedule_view_mode"]:
                st.session_state["schedule_view_mode"] = view_mode.lower()
                st.rerun()
                
        with col_nav:
            col_nav_prev, col_nav_label, col_nav_next = st.columns([1, 4, 1], vertical_alignment="center")
            with col_nav_prev:
                if st.button("◀ Back", key="nav_prev_btn", use_container_width=True):
                    if st.session_state["schedule_view_mode"] == "today":
                        st.session_state["schedule_active_date"] -= timedelta(days=1)
                    else:
                        st.session_state["schedule_active_date"] -= timedelta(days=7)
                    st.rerun()

            with col_nav_next:
                if st.button("Next ▶", key="nav_next_btn", use_container_width=True):
                    if st.session_state["schedule_view_mode"] == "today":
                        st.session_state["schedule_active_date"] += timedelta(days=1)
                    else:
                        st.session_state["schedule_active_date"] += timedelta(days=7)
                    st.rerun()

            with col_nav_label:
                if st.session_state["schedule_view_mode"] == "today":
                    label_text = active_date.strftime("%A, %B %d, %Y")
                else:
                    monday, sunday = get_week_range(active_date)
                    label_text = f"Week of {monday.strftime('%b %d')} – {sunday.strftime('%b %d, %Y')}"
                st.markdown(f"<h5 style='text-align:center; margin:0; color:#1C1C1E; font-weight:700; line-height:1.2;'>{label_text}</h5>", unsafe_allow_html=True)

    with col_add_task:
        if st.button("➕ Add Task", use_container_width=True, key="trigger_add_task_btn"):
            show_add_task_modal(user_id, date.today())

    st.write("")

    # Fetch tasks
    if st.session_state["schedule_view_mode"] == "today":
        schedule_items = get_schedule(user_id, active_date.isoformat())
    else:
        monday, sunday = get_week_range(active_date)
        schedule_items = get_schedule_range(user_id, monday.isoformat(), sunday.isoformat())

    # Render Calendar Grid
    render_calendar_grid(schedule_items, st.session_state["schedule_view_mode"], active_date)
