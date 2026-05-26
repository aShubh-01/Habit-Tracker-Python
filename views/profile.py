"""
views/profile.py — User profile and level statistics (v2)
"""
import streamlit as st
import textwrap
from utils.styles import page_header, xp_bar, card, st_html
from utils.icons import render_icon
from utils.helpers import get_level_info


def render_profile():
    user = st.session_state["user"]
    user_id = user["id"]

    # Refresh user session details from DB
    from services.auth_service import get_user_by_id
    user = get_user_by_id(user_id)
    st.session_state["user"] = user

    page_header("👤 Profile & Leveling", "Track your progress, level stats, and consistency.")

    li = get_level_info(user.get("xp", 0))

    # ── Avatar + Level ────────────────────────────────────────────────────────
    col_av, col_stats = st.columns([1, 2])

    with col_av:
        avatar = _level_avatar(li["level"])
        st_html(f"""
        <div style="background:#FFFFFF; border:1px solid #E5E7EB; border-radius:12px;
                    padding:2rem; text-align:center; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <div style="font-size:4.5rem; line-height: 1;">{avatar}</div>
            <div style="font-weight:800; color:#1C1C1E; font-size:1.2rem; margin-top:12px;">
                {user.get('display_name', user['username'])}
            </div>
            <div style="font-size:0.82rem; color:#6B7280; margin-top:2px;">@{user['username']}</div>
            <div style="margin-top:12px; background:#EEF2F6; border-radius:6px;
                        padding:4px 12px; display:inline-block;">
                <span style="color:#6366F1; font-weight:600; font-size:0.85rem;">
                    Lv. {li['level']} · {li['title']}
                </span>
            </div>
        </div>
        """)

    with col_stats:
        # Load counts from DB
        from services.stats_service import get_routine_stats
        stats = get_routine_stats(user_id, days=365) # Lifetime stats
        
        st_html(f"""
        <div style="background:#FFFFFF; border:1px solid #E5E7EB; border-radius:12px; padding:1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
            <div style="font-weight:700; color:#1C1C1E; font-size:1.05rem; margin-bottom:14px; border-bottom:1px solid #EEF2F6; padding-bottom:8px;">📊 Overall Performance</div>
        """)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🪙 Points Balance", f"{stats['points']:,} pts")
        c2.metric("⚡ Cumulative XP", f"{stats['xp']:,}")
        c3.metric("🎯 Level", f"Lvl {stats['level']}")
        
        st.write("") # spacing
        
        c1.metric("🔥 Perfect Streak", f"{stats['streak']} days")
        c2.metric("📈 XP Multiplier", f"{user.get('multiplier', 1.0)}x")
        c3.metric("✓ Total Checked", f"{stats['total_completed']} slots")
        
        st_html("</div>")

    # ── XP Bar ────────────────────────────────────────────────────────────────
    st.write("")
    st_html(xp_bar(li["pct"], li["xp_in_level"], li["xp_for_level"]))

    st.write("---")

    # ── Member since ──────────────────────────────────────────────────────────
    created = user.get("created_at", "")[:10]
    st.caption(f"🗓 Account Active Since: {created} · Email: {user.get('email') or 'none'}")


def _level_avatar(level: int) -> str:
    if level < 5: return "🌱"
    elif level < 10: return "🌿"
    elif level < 20: return "✨"
    elif level < 40: return "⚡"
    else: return "👑"
