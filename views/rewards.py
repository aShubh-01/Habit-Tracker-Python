"""
views/rewards.py — Reward Shop where users design and redeem real-life rewards (v2)
"""
import streamlit as st
import textwrap
from datetime import datetime
from utils.styles import page_header, card, st_html
from utils.icons import render_icon, ICONS, ICON_EMOJIS
from services.reward_service import (
    get_rewards, create_reward, delete_reward, redeem_reward, get_redemptions
)


REWARD_SYMBOLS = ["gift", "sparkles", "heart", "sun", "moon", "trophy", "star", "musical-note", "camera", "bolt"]


def render_rewards():
    user = st.session_state["user"]
    user_id = user["id"]

    page_header("🛍️ Reward Shop", "Exchange points earned from habits for real-life self-care rewards.")

    # Show points balance prominently
    points_balance = user.get("points", 0)
    st_html(f"""
    <div style="background:#FFFbeb; border:1px solid #FEF3C7; border-radius:12px; padding:1.25rem; text-align:center; margin-bottom:1.5rem;">
        <span style="font-size:0.9rem; color:#D97706; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Your Points Balance</span>
        <div style="font-size:2.5rem; font-weight:800; color:#D97706; margin-top:4px;">🪙 {points_balance:,} pts</div>
        <p style="margin: 6px 0 0; font-size:0.85rem; color:#B45309;">Complete scheduled habits to earn points, then redeem them here!</p>
    </div>
    """)

    tab_shop, tab_create, tab_history = st.tabs(["🛍️ Redeem Rewards", "➕ Design Reward", "📜 Redemption History"])

    # ── Redeem Rewards Tab ───────────────────────────────────────────────────
    with tab_shop:
        # Display alerts if set in session state
        if st.session_state.get("redeem_error"):
            st_html(f"""
            <div style="background:#FEF2F2; border:1px solid #FCA5A5; border-left:4px solid #EF4444; border-radius:8px; padding:12px 16px; margin-bottom:1.5rem; display:flex; align-items:center; gap:12px;">
                <div style="font-size:1.5rem; line-height:1;">⚠️</div>
                <div style="font-size:0.9rem; color:#991B1B; font-weight: 500;">
                    {st.session_state["redeem_error"]}
                </div>
            </div>
            """)
            del st.session_state["redeem_error"]
            
        if st.session_state.get("redeem_success"):
            st_html(f"""
            <div style="background:#ECFDF5; border:1px solid #A7F3D0; border-left:4px solid #10B981; border-radius:8px; padding:12px 16px; margin-bottom:1.5rem; display:flex; align-items:center; gap:12px;">
                <div style="font-size:1.5rem; line-height:1;">🎉</div>
                <div style="font-size:0.9rem; color:#065F46; font-weight: 500;">
                    {st.session_state["redeem_success"]}
                </div>
            </div>
            """)
            del st.session_state["redeem_success"]

        rewards = get_rewards(user_id)
        if not rewards:
            st.info("No rewards designed yet. Go to the **Design Reward** tab to create one!")
        else:
            col_list = st.columns(2)
            for idx, r in enumerate(rewards):
                with col_list[idx % 2]:
                    symbol = r.get("symbol", "gift")
                    symbol_html = render_icon(symbol, color="#D97706", size=32)
                    cost = r["cost"]
                    
                    # Highlight if they can afford it
                    can_afford = points_balance >= cost
                    border_accent = "#FEF3C7" if can_afford else "#E5E7EB"
                    accent_color = "#D97706" if can_afford else "#9CA3AF"
                    
                    card_content = f"""
                    <div style="display:flex; align-items:start; justify-content:space-between; height:100%;">
                        <div style="display:flex; align-items:start; gap:12px;">
                            <div style="margin-top:2px;">{symbol_html}</div>
                            <div>
                                <strong style="font-size:1.1rem; color:#1C1C1E;">{r['name']}</strong>
                                <p style="color:#6B7280; font-size:0.85rem; margin: 4px 0 0;">{r.get('description','')}</p>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:1rem; font-weight:800; color:#D97706; display:block;">{cost} pts</span>
                        </div>
                    </div>
                    """
                    st_html(card(card_content, color_accent=accent_color))
                    
                    # Buttons
                    col_b1, col_b2 = st.columns([3, 1])
                    with col_b1:
                        if st.button(f"🛒 Redeem ({cost} pts)", key=f"red_{r['id']}", use_container_width=True):
                            if not can_afford:
                                st.session_state["redeem_error"] = f"You need {cost} points to redeem <b>{r['name']}</b>, but you only have {points_balance} points! Complete more habits on your schedule to earn points."
                                st.rerun()
                            else:
                                record, err = redeem_reward(user_id, r["id"])
                                if err:
                                    st.session_state["redeem_error"] = err
                                else:
                                    st.session_state["redeem_success"] = f"Successfully redeemed <b>{r['name']}</b>! Enjoy your reward 🎉"
                                    # Refresh user balance in session
                                    from services.auth_service import get_user_by_id
                                    st.session_state["user"] = get_user_by_id(user_id)
                                st.rerun()
                    with col_b2:
                        if st.button("🗑️", key=f"del_rew_{r['id']}", use_container_width=True, help="Delete reward option"):
                            delete_reward(r["id"])
                            st.warning("Reward option deleted.")
                            st.rerun()
                    st.write("")

    # ── Design Reward Tab ────────────────────────────────────────────────────
    with tab_create:
        st.markdown("### Design a Custom Reward")
        st.write("Reward yourself with real-life activities or treats. Choose a points cost that matches the effort required!")
        
        with st.form("create_reward_form"):
            name = st.text_input("Reward Name *", placeholder="e.g. 1 Hour of Gaming, Cheat Meal, Buy New Book")
            description = st.text_area("Reward Description", placeholder="e.g. Indulge in gaming without guilt, or get a burger.")
            
            col1, col2 = st.columns(2)
            with col1:
                cost = st.number_input("Cost (Points)", min_value=1, max_value=10000, value=100, step=10)
            with col2:
                symbol = st.selectbox("Symbol", REWARD_SYMBOLS, format_func=lambda s: ICON_EMOJIS.get(s, s))
                
            submitted = st.form_submit_button("🎨 Add Reward to Shop", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.error("Reward name is required.")
                else:
                    create_reward(user_id, name, description, int(cost), symbol)
                    st.success(f"Reward **{name}** added to the shop!")
                    st.rerun()

    # ── Redemption History Tab ───────────────────────────────────────────────
    with tab_history:
        st.markdown("### Redemption Logs")
        redemptions = get_redemptions(user_id)
        if not redemptions:
            st.write("You haven't redeemed any rewards yet.")
        else:
            for log in redemptions:
                date_dt = datetime.fromisoformat(log["redeemed_at"])
                date_str = date_dt.strftime("%B %d, %Y at %I:%M %p")
                symbol_html = render_icon(log.get("reward_symbol", "gift"), color="#6B7280", size=18)
                
                st_html(f"""
                <div style="display:flex; align-items:center; justify-content:space-between; padding: 10px 14px; border: 1px solid #E5E7EB; border-radius:8px; margin-bottom:8px; background:#FFFFFF;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        {symbol_html}
                        <div>
                            <span style="font-weight:600; color:#1C1C1E; font-size:0.92rem;">{log['reward_name']}</span>
                            <div style="font-size:0.75rem; color:#6B7280;">Redeemed on {date_str}</div>
                        </div>
                    </div>
                    <span style="font-weight:700; color:#D97706; font-size:0.9rem;">- {log['points_spent']} pts</span>
                </div>
                """)
