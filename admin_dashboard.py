"""
admin_dashboard.py — Admin Dashboard v1.0
──────────────────────────────────────────
✅ Section 1 — Bihar District Heatmap
✅ Section 2 — Trending Scam Patterns
✅ Section 3 — User Management
✅ Section 4 — Excel Export
✅ Section 5 — Low Accuracy Alerts
✅ Section 6 — Advanced Charts
"""

import os
import re
import io
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd


# ══════════════════════════════════════════════════════════
#  BIHAR DISTRICTS DATA
# ══════════════════════════════════════════════════════════

BIHAR_DISTRICTS = [
    "पटना", "गया", "मुजफ्फरपुर", "भागलपुर", "दरभंगा",
    "पूर्णिया", "आरा", "बेगूसराय", "कटिहार", "मधुबनी",
    "मुंगेर", "सहरसा", "छपरा", "हाजीपुर", "सीतामढ़ी",
    "सुपौल", "समस्तीपुर", "सिवान", "बक्सर", "रोहतास",
    "औरंगाबाद", "जहानाबाद", "नवादा", "नालंदा", "शेखपुरा",
    "लखीसराय", "जमुई", "बांका", "खगड़िया", "अररिया",
    "किशनगंज", "मधेपुरा", "शिवहर", "वैशाली", "गोपालगंज",
    "सारण", "पश्चिम चंपारण", "पूर्वी चंपारण", "भोजपुर", "कैमूर",
];


# ══════════════════════════════════════════════════════════
#  DATABASE HELPERS (Admin specific)
# ══════════════════════════════════════════════════════════

def _conn():
    import sqlite3
    db = os.path.join(os.path.dirname(__file__), "cyber_raksha.db")
    c = sqlite3.connect(db, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def get_all_data_for_export():
    """Excel export के लिए सभी data।"""
    conn = _conn()
    complaints = [dict(r) for r in conn.execute(
        "SELECT * FROM complaints ORDER BY created_at DESC"
    ).fetchall()]
    scans = [dict(r) for r in conn.execute(
        "SELECT id, alert_count, risk_level, source, created_at FROM scan_logs ORDER BY created_at DESC LIMIT 1000"
    ).fetchall()]
    try:
        feedback = [dict(r) for r in conn.execute(
            "SELECT * FROM feedback ORDER BY created_at DESC"
        ).fetchall()]
    except Exception:
        feedback = []
    conn.close()
    return complaints, scans, feedback


def get_trending_patterns(days: int = 7) -> list:
    """पिछले N दिनों में सबसे ज़्यादा आए scam patterns।"""
    conn = _conn()
    since = (datetime.now() - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT message FROM scan_logs WHERE created_at >= ? AND alert_count > 0",
        (since,)
    ).fetchall()
    conn.close()

    from security_engine import FRAUD_KEYWORDS
    keyword_counts = {}
    for row in rows:
        msg = (row["message"] or "").lower()
        for kw in FRAUD_KEYWORDS:
            if kw.lower() in msg:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

    sorted_kw = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_kw[:15]


def get_hourly_distribution() -> dict:
    """दिन के किस घंटे सबसे ज़्यादा scam आते हैं।"""
    conn = _conn()
    rows = conn.execute(
        "SELECT strftime('%H', created_at) as hour, COUNT(*) as count FROM scan_logs WHERE alert_count > 0 GROUP BY hour"
    ).fetchall()
    conn.close()
    return {int(r["hour"]): r["count"] for r in rows}


def get_weekly_trend() -> list:
    """पिछले 4 हफ्तों का trend।"""
    conn = _conn()
    rows = conn.execute("""
        SELECT strftime('%Y-W%W', created_at) as week,
               COUNT(*) as scans,
               SUM(CASE WHEN alert_count >= 4 THEN 1 ELSE 0 END) as dangerous
        FROM scan_logs
        WHERE created_at >= date('now', '-28 days')
        GROUP BY week ORDER BY week
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_low_accuracy_scans(threshold: float = 50.0) -> list:
    """जिन scans पर 'wrong' feedback मिला।"""
    conn = _conn()
    try:
        rows = conn.execute("""
            SELECT f.id, f.vote, f.risk_level, f.message, f.created_at,
                   f.comment
            FROM feedback f
            WHERE f.vote = 'wrong'
            ORDER BY f.created_at DESC
            LIMIT 50
        """).fetchall()
    except Exception:
        rows = []
    conn.close()
    return [dict(r) for r in rows]


def get_admin_list() -> list:
    """सभी admins की list।"""
    conn = _conn()
    rows = conn.execute(
        "SELECT id, username, created_at FROM admins ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_admin(username: str, password: str) -> bool:
    """नया admin जोड़ें।"""
    import hashlib
    conn = _conn()
    try:
        conn.execute(
            "INSERT INTO admins (username, password_hash, created_at) VALUES (?,?,?)",
            (username,
             hashlib.sha256(password.encode()).hexdigest(),
             datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False


def delete_admin(username: str, current_user: str) -> bool:
    """Admin delete करें (खुद को नहीं)।"""
    if username == current_user:
        return False
    conn = _conn()
    conn.execute("DELETE FROM admins WHERE username=?", (username,))
    conn.commit()
    conn.close()
    return True


# ══════════════════════════════════════════════════════════
#  EXCEL EXPORT
# ══════════════════════════════════════════════════════════

def generate_excel_report() -> bytes:
    """सभी data का Excel report।"""
    complaints, scans, feedback = get_all_data_for_export()
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # Sheet 1: Complaints
        if complaints:
            df_c = pd.DataFrame(complaints)
            df_c["created_at"] = df_c["created_at"].str[:16].str.replace("T"," ")
            df_c.to_excel(writer, sheet_name="शिकायतें", index=False)

        # Sheet 2: Scan Logs
        if scans:
            df_s = pd.DataFrame(scans)
            df_s["created_at"] = df_s["created_at"].str[:16].str.replace("T"," ")
            df_s.to_excel(writer, sheet_name="Scan Logs", index=False)

        # Sheet 3: Feedback
        if feedback:
            df_f = pd.DataFrame(feedback)
            df_f["created_at"] = df_f["created_at"].str[:16].str.replace("T"," ")
            df_f.to_excel(writer, sheet_name="Feedback", index=False)

        # Sheet 4: Summary
        summary = pd.DataFrame([{
            "Total Complaints": len(complaints),
            "Total Scans":      len(scans),
            "Total Feedback":   len(feedback),
            "Report Date":      datetime.now().strftime("%Y-%m-%d %H:%M"),
        }])
        summary.to_excel(writer, sheet_name="Summary", index=False)

    return buf.getvalue()


# ══════════════════════════════════════════════════════════
#  MAIN RENDER FUNCTION
# ══════════════════════════════════════════════════════════

def render_admin_dashboard(current_user: str = "admin"):
    """पूरा Admin Dashboard render करें।"""

    st.markdown("""
    <div style="background:linear-gradient(135deg,#1e3c78,#2a5298);
                color:white;padding:16px 20px;border-radius:12px;margin-bottom:16px">
        <h2 style="margin:0;font-size:1.4rem">🔐 Admin Dashboard</h2>
        <p style="margin:4px 0 0;opacity:0.85;font-size:0.85rem">
            KDSP बिहार — Advanced Analytics & Management
        </p>
    </div>""", unsafe_allow_html=True)

    # Dashboard tabs
    d_tabs = st.tabs([
        "🗺️ District Map",
        "📈 Trending",
        "📊 Advanced Charts",
        "🔔 Accuracy Alerts",
        "👤 User Mgmt",
        "📥 Excel Export",
    ])

    # ══════════════════════════════════════════════════
    #  SECTION 1 — Bihar District Heatmap
    # ══════════════════════════════════════════════════
    with d_tabs[0]:
        st.write("### 🗺️ Bihar District — Complaint Heatmap")
        st.caption("Note: Demo data दिख रहा है। Real deployment में GPS/district field add करें।")

        # Real data पहले, demo fallback
        from database import get_district_distribution
        real_data = get_district_distribution()

        if real_data:
            district_data = {d: 0 for d in BIHAR_DISTRICTS}
            district_data.update(real_data)
            # Unknown districts भी दिखाएं
            for d, c in real_data.items():
                if d not in district_data:
                    district_data[d] = c
            st.success(f"✅ Real data — {sum(real_data.values())} शिकायतें {len(real_data)} जिलों से")
        else:
            import random
            random.seed(42)
            district_data = {d: random.randint(0, 25) for d in BIHAR_DISTRICTS}
            st.info("ℹ️ Demo data — अभी कोई जिला-tagged शिकायत नहीं है।")

        # Top 5 districts highlight
        top5 = sorted(district_data.items(), key=lambda x: x[1], reverse=True)[:5]

        col_map, col_rank = st.columns([2, 1])
        with col_map:
            # Visual heatmap (HTML table-style)
            max_val = max(district_data.values()) or 1
            html_rows = ""
            for i, (dist, count) in enumerate(
                sorted(district_data.items(), key=lambda x: x[1], reverse=True)
            ):
                pct   = count / max_val
                r     = int(231 * pct)
                g     = int(76  * (1 - pct * 0.7))
                b     = int(60  * (1 - pct))
                color = f"rgb({r},{g},{b})"
                bar   = "█" * int(pct * 20)
                html_rows += (
                    f'<tr><td style="padding:3px 8px;font-size:0.82rem">'
                    f'<b>{dist}</b></td>'
                    f'<td style="padding:3px 8px">'
                    f'<span style="color:{color};font-family:monospace">{bar}</span>'
                    f'</td>'
                    f'<td style="padding:3px 8px;color:{color};font-weight:700">'
                    f'{count}</td></tr>'
                )
            st.markdown(
                f'<div style="max-height:400px;overflow-y:auto;border:1px solid #eee;'
                f'border-radius:8px;padding:8px">'
                f'<table style="width:100%">{html_rows}</table></div>',
                unsafe_allow_html=True
            )

        with col_rank:
            st.write("**🏆 Top 5 Districts**")
            for i, (dist, count) in enumerate(top5):
                medal = ["🥇","🥈","🥉","4️⃣","5️⃣"][i]
                st.markdown(
                    f'<div style="background:#fff3cd;border-radius:8px;'
                    f'padding:8px 12px;margin:4px 0;border-left:4px solid #f39c12">'
                    f'{medal} <b>{dist}</b><br>'
                    f'<span style="color:#e74c3c;font-size:1.1rem;font-weight:700">'
                    f'{count} शिकायतें</span></div>',
                    unsafe_allow_html=True
                )

            st.divider()
            total_dist = sum(district_data.values())
            st.metric("📊 कुल शिकायतें", total_dist)
            st.metric("📍 जिले", len(BIHAR_DISTRICTS))
            avg = round(total_dist / len(BIHAR_DISTRICTS), 1)
            st.metric("📈 औसत/जिला", avg)

        # District CSV
        df_dist = pd.DataFrame(
            sorted(district_data.items(), key=lambda x: x[1], reverse=True),
            columns=["जिला", "शिकायतें"]
        )
        csv_dist = df_dist.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 District Data CSV", csv_dist,
                           "district_data.csv", "text/csv",
                           use_container_width=True)

    # ══════════════════════════════════════════════════
    #  SECTION 2 — Trending Scam Patterns
    # ══════════════════════════════════════════════════
    with d_tabs[1]:
        st.write("### 📈 Trending Scam Patterns")

        period = st.radio("Period:", ["7 दिन","14 दिन","30 दिन"],
                          horizontal=True, key="trend_period")
        days_map = {"7 दिन": 7, "14 दिन": 14, "30 दिन": 30}
        days = days_map[period]

        trending = get_trending_patterns(days)

        if trending:
            st.write(f"**पिछले {days} दिनों में top keywords:**")
            for i, (kw, count) in enumerate(trending[:10]):
                pct   = count / trending[0][1] * 100 if trending[0][1] > 0 else 0
                color = "#e74c3c" if pct > 60 else "#e67e22" if pct > 30 else "#f39c12"
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;'
                    f'margin:4px 0;background:#f8f9fa;border-radius:8px;padding:6px 10px">'
                    f'<span style="min-width:24px;font-weight:700;color:#666">'
                    f'#{i+1}</span>'
                    f'<span style="flex:1;font-weight:600">{kw}</span>'
                    f'<div style="flex:2;background:#e0e0e0;border-radius:4px;height:10px">'
                    f'<div style="background:{color};width:{pct:.0f}%;height:10px;'
                    f'border-radius:4px"></div></div>'
                    f'<span style="min-width:40px;text-align:right;color:{color};'
                    f'font-weight:700">{count}x</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            # Demo data
            st.info("अभी scan data कम है। Demo patterns दिख रहे हैं।")
            demo = [("otp",18),("kyc",14),("lottery",11),("account block",8),
                    ("prize",6),("click here",5),("winner",4),("urgent",3)]
            for i,(kw,count) in enumerate(demo):
                pct = count/18*100
                color = "#e74c3c" if pct>60 else "#e67e22" if pct>30 else "#f39c12"
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;margin:4px 0;'
                    f'background:#f8f9fa;border-radius:8px;padding:6px 10px">'
                    f'<span style="min-width:24px;font-weight:700;color:#666">#{i+1}</span>'
                    f'<span style="flex:1;font-weight:600">{kw}</span>'
                    f'<div style="flex:2;background:#e0e0e0;border-radius:4px;height:10px">'
                    f'<div style="background:{color};width:{pct:.0f}%;height:10px;border-radius:4px"></div></div>'
                    f'<span style="min-width:40px;text-align:right;color:{color};font-weight:700">{count}x</span>'
                    f'</div>', unsafe_allow_html=True
                )

        # Weekly trend
        st.divider()
        st.write("**📅 साप्ताहिक Trend (पिछले 4 हफ्ते)**")
        weekly = get_weekly_trend()
        if weekly and len(weekly) >= 2:
            df_w = pd.DataFrame(weekly)
            st.bar_chart(df_w.set_index("week")[["scans","dangerous"]],
                         color=["#3498db","#e74c3c"])
        else:
            demo_weekly = pd.DataFrame({
                "week":      ["2025-W01","2025-W02","2025-W03","2025-W04"],
                "scans":     [23, 31, 28, 45],
                "dangerous": [8,  12, 9,  18],
            })
            st.bar_chart(demo_weekly.set_index("week")[["scans","dangerous"]],
                         color=["#3498db","#e74c3c"])
            st.caption("Demo data — real scans के बाद actual trend दिखेगा")

    # ══════════════════════════════════════════════════
    #  SECTION 3 — Advanced Charts
    # ══════════════════════════════════════════════════
    with d_tabs[2]:
        st.write("### 📊 Advanced Analytics Charts")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            # Hourly distribution
            st.write("**⏰ दिन के किस समय ज़्यादा फ्रॉड?**")
            hourly = get_hourly_distribution()
            if hourly:
                df_h = pd.DataFrame([
                    {"hour": f"{h:02d}:00", "count": hourly.get(h, 0)}
                    for h in range(24)
                ])
                st.bar_chart(df_h.set_index("hour")["count"],
                             color="#e74c3c", height=220)
            else:
                # Demo
                import random; random.seed(7)
                demo_h = {h: random.randint(0,15) for h in range(24)}
                demo_h.update({10:18,11:22,14:19,15:25,20:21,21:28,22:30})
                df_hd = pd.DataFrame([
                    {"hour": f"{h:02d}:00", "count": demo_h[h]}
                    for h in range(24)
                ])
                st.bar_chart(df_hd.set_index("hour")["count"],
                             color="#e74c3c", height=220)
                st.caption("Demo data")

        with chart_col2:
            # Source breakdown
            st.write("**📱 App vs WhatsApp**")
            from database import get_source_breakdown
            src = get_source_breakdown()
            if src:
                df_src = pd.DataFrame(
                    list(src.items()), columns=["Source","Count"]
                )
                df_src["Source"] = df_src["Source"].replace({
                    "streamlit":"🖥️ App","whatsapp":"📱 WhatsApp",
                    "bulk_upload":"📄 Bulk"
                })
                st.bar_chart(df_src.set_index("Source")["Count"],
                             color="#2a5298", height=220)
            else:
                demo_src = pd.DataFrame({
                    "Source":["🖥️ App","📱 WhatsApp","📄 Bulk"],
                    "Count":[45,78,12]
                })
                st.bar_chart(demo_src.set_index("Source")["Count"],
                             color="#2a5298", height=220)
                st.caption("Demo data")

        st.divider()

        # Risk level pie-style
        st.write("**🎯 Risk Level Distribution**")
        from database import get_risk_distribution, get_scan_stats
        risk = get_risk_distribution()
        ss   = get_scan_stats()

        r1,r2,r3,r4 = st.columns(4)
        items = list(risk.items())
        colors_map = ["#27ae60","#f39c12","#e67e22","#e74c3c"]
        for col, (label, count), color in zip([r1,r2,r3,r4], items, colors_map):
            col.markdown(
                f'<div style="background:{color}15;border:2px solid {color};'
                f'border-radius:10px;padding:12px;text-align:center">'
                f'<div style="font-size:1.5rem;font-weight:900;color:{color}">'
                f'{count}</div>'
                f'<div style="font-size:0.75rem;color:#555">{label}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.divider()

        # Scan vs Complaint ratio
        st.write("**📊 Overall Stats**")
        s1,s2,s3,s4 = st.columns(4)
        s1.metric("🔍 कुल Scans",     ss.get("total",0))
        s2.metric("🚨 Dangerous",      ss.get("dangerous",0))
        s3.metric("📄 Complaints",     ss.get("total_complaints",0))
        conv = round(ss.get("dangerous",0)/max(ss.get("total",1),1)*100,1)
        s4.metric("⚠️ Danger Rate",   f"{conv}%")

    # ══════════════════════════════════════════════════
    #  SECTION 4 — Low Accuracy Alerts
    # ══════════════════════════════════════════════════
    with d_tabs[3]:
        st.write("### 🔔 Low Accuracy Alerts — Feedback Analysis")

        from database import get_feedback_stats
        fb = get_feedback_stats()

        # Overall accuracy
        acc = fb["accuracy"]
        color = "#27ae60" if acc >= 80 else "#e67e22" if acc >= 60 else "#e74c3c"

        if fb["total"] > 0:
            a1,a2,a3,a4 = st.columns(4)
            a1.metric("📊 कुल Feedback", fb["total"])
            a2.metric("✅ सही",   fb["correct"])
            a3.metric("❌ गलत",   fb["wrong"])
            a4.metric("🎯 Accuracy", f"{acc}%",
                      delta="Good" if acc>=80 else "Needs improvement")

            # Accuracy bar
            st.markdown(f"""
            <div style="background:#f8f9fa;border-radius:10px;padding:14px 16px">
                <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                    <span style="font-weight:700">Model Accuracy</span>
                    <span style="font-weight:900;color:{color};font-size:1.3rem">{acc}%</span>
                </div>
                <div style="background:#e0e0e0;border-radius:6px;height:16px">
                    <div style="background:{color};width:{acc}%;height:16px;
                         border-radius:6px;transition:width 0.5s"></div>
                </div>
                <div style="margin-top:6px;font-size:0.8rem;color:#888">
                    {'🟢 अच्छा!' if acc>=80 else '🟡 Improvement चाहिए' if acc>=60 else '🔴 Action लें!'}
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("📊 अभी feedback नहीं है। Users scan करने के बाद 👍/❌ दबाएंगे।")

        st.divider()

        # Wrong predictions
        wrong_scans = get_low_accuracy_scans()
        if wrong_scans:
            st.write(f"**❌ {len(wrong_scans)} Incorrect Predictions:**")
            for item in wrong_scans[:10]:
                msg_preview = (item.get("message","") or "")[:80]
                st.markdown(
                    f'<div style="background:#fff0f0;border-left:4px solid #e74c3c;'
                    f'border-radius:8px;padding:10px 14px;margin:6px 0">'
                    f'<div style="font-size:0.8rem;color:#888">'
                    f'{item["created_at"][:16].replace("T"," ")} | '
                    f'Predicted: <b>{item.get("risk_level","?")}</b></div>'
                    f'<div style="margin-top:4px;font-size:0.88rem">'
                    f'{msg_preview}{"..." if len(msg_preview)==80 else ""}</div>'
                    f'{f"""<div style="font-size:0.8rem;color:#555;margin-top:4px">💬 {item["comment"]}</div>""" if item.get("comment") else ""}'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.success("🎉 कोई incorrect prediction नहीं! Model अच्छा काम कर रहा है।")

        # Recommendations
        if fb.get("total",0) > 5 and acc < 70:
            st.divider()
            st.warning("**🔧 सुझाव:**")
            st.markdown("""
- `FRAUD_KEYWORDS` में नए keywords जोड़ें (`security_engine.py`)
- `scam_database.json` में नए patterns add करें
- Risk thresholds adjust करें (`RISK_LEVELS`)
            """)

    # ══════════════════════════════════════════════════
    #  SECTION 5 — User Management
    # ══════════════════════════════════════════════════
    with d_tabs[4]:
        st.write("### 👤 User Management")

        admins = get_admin_list()
        st.write(f"**कुल Admins: {len(admins)}**")

        for admin in admins:
            col_u, col_del = st.columns([4,1])
            is_self = admin["username"] == current_user
            col_u.markdown(
                f'<div style="background:{"#e8f5e9" if is_self else "#f5f5f5"};'
                f'border-radius:8px;padding:8px 12px;margin:2px 0">'
                f'👤 <b>{admin["username"]}</b>'
                f'{"  🟢 (आप)" if is_self else ""}'
                f'<span style="color:#888;font-size:0.75rem;margin-left:8px">'
                f'Created: {admin["created_at"][:10]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            if not is_self:
                if col_del.button("🗑️", key=f"del_{admin['username']}",
                                   help=f"Delete {admin['username']}"):
                    if delete_admin(admin["username"], current_user):
                        st.success(f"✅ {admin['username']} हटाया गया।")
                        st.rerun()

        st.divider()

        # Add new admin
        st.write("**➕ नया Admin जोड़ें**")
        with st.form("add_admin_form"):
            new_user = st.text_input("Username")
            new_pass = st.text_input("Password", type="password")
            new_pass2 = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("✅ जोड़ें", use_container_width=True):
                if not new_user or not new_pass:
                    st.error("Username और Password ज़रूरी है।")
                elif new_pass != new_pass2:
                    st.error("Passwords मेल नहीं खाते!")
                elif len(new_pass) < 8:
                    st.error("Password कम से कम 8 अक्षर का होना चाहिए।")
                elif add_admin(new_user, new_pass):
                    st.success(f"✅ {new_user} जोड़ा गया!")
                    st.rerun()
                else:
                    st.error("Username already exists!")

    # ══════════════════════════════════════════════════
    #  SECTION 6 — Excel Export
    # ══════════════════════════════════════════════════
    with d_tabs[5]:
        st.write("### 📥 Excel Export — Full Data")
        st.caption("सभी complaints, scan logs, और feedback एक Excel file में।")

        complaints, scans, feedback = get_all_data_for_export()

        # Stats
        e1,e2,e3 = st.columns(3)
        e1.metric("📋 Complaints", len(complaints))
        e2.metric("🔍 Scan Logs",  len(scans))
        e3.metric("👍 Feedback",   len(feedback))

        st.divider()

        # Excel download
        try:
            xl_bytes = generate_excel_report()
            fname = f"CyberRaksha_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            st.download_button(
                "📥 Full Excel Report Download",
                xl_bytes,
                fname,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
            st.success("✅ Excel file तैयार है — 4 sheets: शिकायतें, Scan Logs, Feedback, Summary")
        except ImportError:
            st.error("⚠️ `openpyxl` install करें: `pip install openpyxl`")

        st.divider()

        # CSV downloads (individual)
        st.write("**📄 Individual CSV Downloads:**")
        c1, c2, c3 = st.columns(3)
        if complaints:
            df_c = pd.DataFrame(complaints)
            c1.download_button("📋 Complaints CSV",
                df_c.to_csv(index=False).encode("utf-8-sig"),
                "complaints.csv","text/csv",use_container_width=True)
        if scans:
            df_s = pd.DataFrame(scans)
            c2.download_button("🔍 Scan Logs CSV",
                df_s.to_csv(index=False).encode("utf-8-sig"),
                "scan_logs.csv","text/csv",use_container_width=True)
        if feedback:
            df_f = pd.DataFrame(feedback)
            c3.download_button("👍 Feedback CSV",
                df_f.to_csv(index=False).encode("utf-8-sig"),
                "feedback.csv","text/csv",use_container_width=True)
