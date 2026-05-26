"""
views/stats.py — Performance statistics and insights (v2)
"""
import streamlit as st
from datetime import date, datetime
import calendar
from utils.styles import page_header, card, st_html
from utils.icons import render_icon
from services.stats_service import get_routine_stats, get_category_stats, get_smart_suggestions



def render_stats():
    user = st.session_state["user"]
    user_id = user["id"]

    page_header("📊 Progress & Analytics", "Reflect on your routine patterns, consistency, and achievements.")

    # ── Time Filter ──────────────────────────────────────────────────────────
    col_filter, _ = st.columns([2, 3])
    with col_filter:
        days_option = st.selectbox(
            "Analyze Performance For",
            [7, 14, 30, 60],
            format_func=lambda x: f"Past {x} Days",
            index=2 # default 30 days
        )

    # ── Fetch Data ───────────────────────────────────────────────────────────
    stats = get_routine_stats(user_id, days=days_option)
    categories = get_category_stats(user_id, days=days_option)
    suggestions = get_smart_suggestions(user_id)

    # ── Key Stats ────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Scheduled", f"{stats['total_scheduled']} slots")
    with col2:
        st.metric("Total Completed", f"{stats['total_completed']} slots")
    with col3:
        st.metric("Completion Rate", f"{stats['completion_rate']}%")
    with col4:
        st.metric("Perfect Days", f"{stats['perfect_days']} days", help="Days where 100% of scheduled habits were ticked off.")

    st.write("---")

    # ── Left Column: Category Breakdown | Right Column: Suggestions ──────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("##### 📁 Completion by Category")
        st.write("Distribution of your habits completed during this period.")
        
        max_completions = max(c["count"] for c in categories) if categories else 0
        
        if max_completions == 0:
            st.info("No completed habits in this timeframe to display.")
        else:
            for cat in categories:
                count = cat["count"]
                color = cat["color"]
                # Calculate percentage relative to max completions for progress bar scaling
                pct = int((count / max_completions) * 100) if max_completions > 0 else 0
                
                st_html(f"""
                <div style="margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.88rem; margin-bottom:3px; color:#1C1C1E;">
                        <strong>{cat['category']}</strong>
                        <span style="color:#6B7280; font-weight:600;">{count} completed</span>
                    </div>
                    <div style="background:#E5E7EB; border-radius:10px; height:8px; overflow:hidden; width:100%;">
                        <div style="background:{color}; width:{pct}%; height:100%; border-radius:10px;"></div>
                    </div>
                </div>
                """)

    with col_right:
        st.markdown("##### 💡 Insights & Tips")
        st.write("Personalized insights based on your routine history.")
        
        suggestions_content = ""
        for sug in suggestions:
            suggestions_content += f"""
            <div style="display:flex; align-items:start; gap:10px; margin-bottom:12px;">
                <div style="margin-top:2px;">{render_icon("sparkles", color="#6366F1", size=18)}</div>
                <div style="font-size:0.88rem; color:#4B5563; line-height:1.4;">{sug}</div>
            </div>
            """
            
        if not suggestions_content:
            st.write("No insights generated yet. Keep tracking your routines!")
        else:
            st_html(card(f"""
            <div style="padding: 4px 0;">
                {suggestions_content}
            </div>
            """, color_accent="#6366F1"))

    st.write("---")
    st.markdown("### 📅 Consistency Calendar")
    st.write("A visual grid of habit completions and consistency this month.")
    
    today_val = date.today()
    col_y, col_m = st.columns(2)
    with col_y:
        selected_year = st.selectbox("Year", [today_val.year, today_val.year - 1], index=0, key="stats_month_year")
    with col_m:
        selected_month = st.selectbox("Month", list(range(1, 13)), index=today_val.month - 1, format_func=lambda m: calendar.month_name[m], key="stats_month_num")
        
    _render_month_calendar_grid(user_id, selected_year, selected_month)


def _render_month_calendar_grid(user_id: str, year: int, month: int):
    """Draw a dot calendar grid for monthly statistics."""
    from collections import defaultdict
    from services.schedule_service import get_schedule_range
    
    cal = calendar.Calendar(calendar.SUNDAY)
    month_days = cal.monthdayscalendar(year, month)
    
    # Query all schedule entries for this month
    start_date = date(year, month, 1).isoformat()
    last_day_val = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day_val).isoformat()
    
    entries = get_schedule_range(user_id, start_date, end_date)
    
    # Group entries by day
    day_entries = defaultdict(list)
    for entry in entries:
        try:
            d = datetime.strptime(entry["date"], "%Y-%m-%d").day
            day_entries[d].append(entry)
        except Exception:
            pass

    weeks_html = ""
    for week in month_days:
        week_html = "<div style='display:grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-bottom: 8px;'>"
        for day in week:
            if day == 0:
                week_html += "<div style='background:#F4F4F2; border: 1px dashed #E5E7EB; border-radius:8px; min-height:60px;'></div>"
            else:
                is_today = (date.today() == date(year, month, day))
                border_css = "border: 2px solid #6366F1;" if is_today else "border: 1px solid #E5E7EB;"
                bg_css = "background:#FFFFFF;"
                
                # Check completions for this day
                items = day_entries[day]
                dots_html = ""
                stats_label = ""
                
                if items:
                    completed = sum(1 for x in items if x["completed"])
                    total = len(items)
                    stats_label = f"<span style='font-size:0.68rem; color:#6B7280; font-weight:600;'>{completed}/{total}</span>"
                    
                    # render small dots
                    for x in items:
                        # Red if not completed and past its scheduled end time
                        is_past_due = False
                        if not x["completed"]:
                            try:
                                end_dt = datetime.strptime(f"{x['date']} {x['end_time']}", "%Y-%m-%d %H:%M")
                                if datetime.now() > end_dt:
                                    is_past_due = True
                            except Exception:
                                pass
                                
                        dot_color = "#10B981" if x["completed"] else ("#EF4444" if is_past_due else "#6366F1")
                        dots_html += f"<span style='height:6px; width:6px; background-color:{dot_color}; border-radius:50%; display:inline-block; margin: 1px;' title='{x['habit_name']}'></span>"
                
                week_html += f"""
                <div style='{bg_css} {border_css} border-radius:8px; padding: 8px; min-height:60px; display:flex; flex-direction:column; justify-content:space-between; box-shadow: 0 1px 2px rgba(0,0,0,0.02);'>
                    <div style='display:flex; justify-content:space-between; align-items:center; line-height:1;'>
                        <span style='font-size:0.8rem; font-weight:700; color:#1C1C1E;'>{day}</span>
                        {stats_label}
                    </div>
                    <div style='display:flex; flex-wrap:wrap; gap:2px; margin-top:8px;'>{dots_html}</div>
                </div>
                """
        week_html += "</div>"
        weeks_html += week_html

    calendar_header = """
    <div style='display:grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-bottom: 8px; text-align:center; font-size:0.8rem; font-weight:700; color:#6B7280; text-transform:uppercase;'>
        <div>Sun</div><div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div>
    </div>
    """
    
    # Legend
    st_html("""
    <div style="display:flex; gap:16px; font-size:0.8rem; margin-bottom:12px; color:#6B7280; flex-wrap:wrap;">
        <div><span style="height:8px; width:8px; background-color:#10B981; border-radius:50%; display:inline-block; margin-right:4px;"></span>Done</div>
        <div><span style="height:8px; width:8px; background-color:#6366F1; border-radius:50%; display:inline-block; margin-right:4px;"></span>Todo</div>
        <div><span style="height:8px; width:8px; background-color:#EF4444; border-radius:50%; display:inline-block; margin-right:4px;"></span>Missed (Past Due)</div>
    </div>
    """)
    
    st_html(calendar_header + weeks_html)

