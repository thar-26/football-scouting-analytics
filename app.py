import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_loader import build_player_profiles, find_undervalued_players, find_similar_players

st.set_page_config(
    page_title="FCM Scout",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #0a0a0a; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem !important; }

.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}
.metric-value { font-size: 2rem; font-weight: 700; color: #ffffff; }
.metric-label { font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

.player-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 6px;
    cursor: pointer;
    transition: all 0.2s;
}
.player-card:hover {
    background: rgba(220,38,38,0.08);
    border-color: rgba(220,38,38,0.3);
}
.player-card.selected {
    background: rgba(220,38,38,0.1);
    border-color: rgba(220,38,38,0.5);
}
.player-name { font-size: 14px; font-weight: 600; color: #ffffff; }
.player-meta { font-size: 11px; color: #6b7280; margin-top: 2px; }
.score-badge {
    background: rgba(220,38,38,0.15);
    border: 1px solid rgba(220,38,38,0.3);
    color: #ef4444;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
}
.section-title { font-size: 18px; font-weight: 700; color: #ffffff; margin-bottom: 4px; }
.section-sub { font-size: 12px; color: #6b7280; margin-bottom: 1.5rem; }
.detail-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(220,38,38,0.2);
    border-radius: 12px;
    padding: 1.5rem;
    height: 100%;
}
.detail-title { font-size: 20px; font-weight: 700; color: #ffffff; margin-bottom: 4px; }
.detail-sub { font-size: 12px; color: #6b7280; margin-bottom: 1.5rem; }
.stat-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.stat-label { font-size: 12px; color: #6b7280; }
.stat-value { font-size: 12px; color: #ffffff; font-weight: 500; }
.stSelectbox label, .stSlider label { color: #9ca3af !important; font-size: 12px !important; }
.stTabs [data-baseweb="tab"] { color: #6b7280 !important; font-size: 13px !important; }
.stTabs [aria-selected="true"] { color: #ffffff !important; }
div[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #9ca3af !important;
    text-align: left !important;
    padding: 0 !important;
    width: 100% !important;
}
div[data-testid="stButton"] button:hover {
    border-color: rgba(220,38,38,0.4) !important;
    background: rgba(220,38,38,0.05) !important;
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────
@st.cache_data
def get_profiles():
    return build_player_profiles()

with st.spinner("Loading player database..."):
    profiles = get_profiles()

# ── SESSION STATE ─────────────────────────────────────────────
if 'selected_player' not in st.session_state:
    st.session_state.selected_player = None

# ── HEADER ────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.5rem">
    <div style="font-size:11px;color:#dc2626;text-transform:uppercase;
                letter-spacing:2px;font-weight:600;margin-bottom:6px">
        ⚽ FC MIDTJYLLAND STYLE ANALYTICS
    </div>
    <div style="font-size:2.2rem;font-weight:800;color:#ffffff;
                letter-spacing:-1px;line-height:1.1">
        Player Scouting &<br>Market Intelligence
    </div>
    <div style="font-size:13px;color:#6b7280;margin-top:8px">
        Data-driven scouting across 47,000+ players — find undervalued talent before anyone else does.
    </div>
</div>
""", unsafe_allow_html=True)

# ── METRICS ───────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(profiles):,}</div><div class="metric-label">Players Tracked</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{profiles["competition_name"].nunique()}</div><div class="metric-label">Competitions</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{profiles["current_club_name"].nunique():,}</div><div class="metric-label">Clubs</div></div>', unsafe_allow_html=True)
with m4:
    avg_val = profiles['market_value_in_eur'].median() / 1_000_000
    st.markdown(f'<div class="metric-card"><div class="metric-value">€{avg_val:.1f}M</div><div class="metric-label">Median Value</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Undervalued Finder",
    "👤 Player Profile",
    "🔄 Similar Players",
    "📋 Scout Report"
])

# ── TAB 1: UNDERVALUED FINDER ─────────────────────────────────
with tab1:
    st.markdown('<div class="section-title">Undervalued Player Finder</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">FCM\'s core philosophy — find players performing above their market value. Click any player to see full details.</div>', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        position = st.selectbox("Position", ["All", "Attack", "Midfield", "Defender", "Goalkeeper"])
    with f2:
        max_age = st.slider("Max Age", 16, 30, 26)
    with f3:
        max_value = st.slider("Max Value (€M)", 1, 50, 10)
    with f4:
        min_apps = st.slider("Min Appearances", 5, 50, 10)

    pos_filter = None if position == "All" else position
    undervalued = find_undervalued_players(
        profiles,
        position_filter=pos_filter,
        max_age=max_age,
        max_value_eur=max_value * 1_000_000,
        min_appearances=min_apps
    )

    left, mid, right = st.columns([1.8, 0.05, 1.2])

    with left:
        top20 = undervalued.head(20)
        fig = px.scatter(
            top20,
            x='market_value_in_eur',
            y='goal_contributions_per_90',
            size='total_appearances',
            color='opportunity_score',
            hover_name='name',
            hover_data=['age', 'position', 'current_club_name', 'competition_name'],
            color_continuous_scale='Reds',
            title='Performance vs Market Value — Top 20 Opportunities'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.02)',
            font_color='#9ca3af',
            title_font_color='#ffffff',
            xaxis_title='Market Value (€)',
            yaxis_title='Goal Contributions per 90',
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("**Top Opportunities** — click to view player")
        for idx, row in undervalued.head(12).iterrows():
            val = f"€{row['market_value_in_eur']/1e6:.1f}M" if row['market_value_in_eur'] >= 1e6 else f"€{row['market_value_in_eur']/1e3:.0f}K"
            is_selected = st.session_state.selected_player == row['name']
            btn_label = f"{'▶ ' if is_selected else ''}{row['name']} — {val} — Score: {row['opportunity_score']:.0f}"
            if st.button(btn_label, key=f"btn_{idx}"):
                st.session_state.selected_player = row['name']
                st.rerun()

    # ── PLAYER DETAIL PANEL ───────────────────────────────────
    if st.session_state.selected_player:
        p_data = profiles[profiles['name'] == st.session_state.selected_player]
        if not p_data.empty:
            p = p_data.iloc[0]
            val = f"€{p['market_value_in_eur']/1e6:.1f}M" if p['market_value_in_eur'] >= 1e6 else f"€{p['market_value_in_eur']/1e3:.0f}K"

            st.markdown("---")
            st.markdown(f"### {p['name']} — Full Profile")

            d1, d2, d3 = st.columns(3)

            with d1:
                st.markdown('<div class="detail-card">', unsafe_allow_html=True)
                st.markdown("**Player Details**")
                details = {
                    "Position": p.get('position', 'N/A'),
                    "Age": f"{p['age']:.0f}",
                    "Club": p.get('current_club_name', 'N/A'),
                    "League": p.get('competition_name', 'N/A'),
                    "Nationality": p.get('country_of_citizenship', 'N/A'),
                    "Height": f"{p.get('height_in_cm', 'N/A')} cm",
                    "Foot": p.get('foot', 'N/A'),
                    "Market Value": val,
                    "Contract Ends": str(p.get('contract_expiration_date', 'N/A'))[:10],
                }
                for k, v in details.items():
                    st.markdown(f"""
                    <div class="stat-row">
                        <span class="stat-label">{k}</span>
                        <span class="stat-value">{v}</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with d2:
                st.markdown("**Performance Stats**")
                stats = {
                    "Total Appearances": int(p['total_appearances']) if not pd.isna(p['total_appearances']) else 0,
                    "Total Goals": int(p['total_goals']) if not pd.isna(p['total_goals']) else 0,
                    "Total Assists": int(p['total_assists']) if not pd.isna(p['total_assists']) else 0,
                    "Goals per 90": p['goals_per_90'],
                    "Assists per 90": p['assists_per_90'],
                    "Goal Contributions/90": p['goal_contributions_per_90'],
                    "Yellow Cards": int(p['yellow_cards']) if not pd.isna(p['yellow_cards']) else 0,
                    "Red Cards": int(p['red_cards']) if not pd.isna(p['red_cards']) else 0,
                    "Int'l Caps": int(p.get('international_caps', 0)) if not pd.isna(p.get('international_caps', 0)) else 0,
                }
                for k, v in stats.items():
                    st.markdown(f"""
                    <div class="stat-row">
                        <span class="stat-label">{k}</span>
                        <span class="stat-value">{v}</span>
                    </div>
                    """, unsafe_allow_html=True)

            with d3:
                # Radar chart
                categories = ['Goals/90', 'Assists/90', 'Appearances', "Int'l Caps"]
                max_vals = [2, 1.5, 300, 100]
                values = [
                    min(p['goals_per_90'], 2),
                    min(p['assists_per_90'], 1.5),
                    min(p['total_appearances'], 300) if not pd.isna(p['total_appearances']) else 0,
                    min(p.get('international_caps', 0), 100) if not pd.isna(p.get('international_caps', 0)) else 0
                ]
                normalized = [v/m for v, m in zip(values, max_vals)]
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=normalized + [normalized[0]],
                    theta=categories + [categories[0]],
                    fill='toself',
                    fillcolor='rgba(220,38,38,0.2)',
                    line=dict(color='#dc2626', width=2),
                    name=p['name']
                ))
                fig.update_layout(
                    polar=dict(
                        bgcolor='rgba(0,0,0,0)',
                        radialaxis=dict(visible=True, range=[0,1], color='#374151'),
                        angularaxis=dict(color='#9ca3af')
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#9ca3af',
                    title=dict(text='Performance Radar', font_color='#ffffff'),
                    showlegend=False,
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

            if st.button("✕ Close player profile"):
                st.session_state.selected_player = None
                st.rerun()

# ── TAB 2: PLAYER PROFILE ─────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Player Profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Search any player in the database</div>', unsafe_allow_html=True)

    player_names = sorted(profiles['name'].dropna().unique().tolist())
    selected = st.selectbox("Search player", player_names)

    if selected:
        p = profiles[profiles['name'] == selected].iloc[0]
        val = f"€{p['market_value_in_eur']/1e6:.1f}M" if p['market_value_in_eur'] >= 1e6 else f"€{p['market_value_in_eur']/1e3:.0f}K"

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Age", f"{p['age']:.0f}")
        with c2:
            st.metric("Market Value", val)
        with c3:
            st.metric("Goals per 90", p['goals_per_90'])
        with c4:
            st.metric("Assists per 90", p['assists_per_90'])

        col1, col2 = st.columns(2)

        with col1:
            categories = ['Goals/90', 'Assists/90', 'Appearances', "Int'l Caps"]
            max_vals = [2, 1.5, 300, 100]
            values = [
                min(p['goals_per_90'], 2),
                min(p['assists_per_90'], 1.5),
                min(p['total_appearances'], 300) if not pd.isna(p['total_appearances']) else 0,
                min(p.get('international_caps', 0), 100) if not pd.isna(p.get('international_caps', 0)) else 0
            ]
            normalized = [v/m for v, m in zip(values, max_vals)]
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=normalized + [normalized[0]],
                theta=categories + [categories[0]],
                fill='toself',
                fillcolor='rgba(220,38,38,0.2)',
                line=dict(color='#dc2626', width=2),
            ))
            fig.update_layout(
                polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, range=[0,1], color='#374151'),
                    angularaxis=dict(color='#9ca3af')
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#9ca3af',
                title=dict(text=f'{selected} — Performance Radar', font_color='#ffffff'),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Player Details**")
            details = {
                "Position": p.get('position', 'N/A'),
                "Club": p.get('current_club_name', 'N/A'),
                "League": p.get('competition_name', 'N/A'),
                "Nationality": p.get('country_of_citizenship', 'N/A'),
                "Height": f"{p.get('height_in_cm', 'N/A')} cm",
                "Foot": p.get('foot', 'N/A'),
                "Total Goals": int(p['total_goals']) if not pd.isna(p['total_goals']) else 0,
                "Total Assists": int(p['total_assists']) if not pd.isna(p['total_assists']) else 0,
                "Total Appearances": int(p['total_appearances']) if not pd.isna(p['total_appearances']) else 0,
                "Int'l Caps": int(p.get('international_caps', 0)) if not pd.isna(p.get('international_caps', 0)) else 0,
            }
            for k, v in details.items():
                st.markdown(f"""
                <div class="stat-row">
                    <span class="stat-label">{k}</span>
                    <span class="stat-value">{v}</span>
                </div>
                """, unsafe_allow_html=True)

# ── TAB 3: SIMILAR PLAYERS ────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">Similar Player Finder</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Find statistically similar players in cheaper markets — the FCM transfer model</div>', unsafe_allow_html=True)

    ref_player = st.selectbox("Select reference player", player_names, key="sim")
    if ref_player:
        similar = find_similar_players(profiles, ref_player)
        if similar is not None:
            ref = profiles[profiles['name'] == ref_player].iloc[0]
            ref_val = f"€{ref['market_value_in_eur']/1e6:.1f}M"
            st.markdown(f"**Reference:** {ref_player} — {ref_val} — {ref.get('current_club_name','')}")

            fig = px.bar(
                similar,
                x='name',
                y='market_value_in_eur',
                color='similarity',
                color_continuous_scale='Reds',
                title='Similar Players by Market Value',
                hover_data=['age', 'position', 'goals_per_90', 'assists_per_90']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(255,255,255,0.02)',
                font_color='#9ca3af',
                title_font_color='#ffffff'
            )
            st.plotly_chart(fig, use_container_width=True)

            for _, row in similar.iterrows():
                val = f"€{row['market_value_in_eur']/1e6:.1f}M" if row['market_value_in_eur'] >= 1e6 else f"€{row['market_value_in_eur']/1e3:.0f}K"
                savings = ref['market_value_in_eur'] - row['market_value_in_eur']
                savings_str = f"€{savings/1e6:.1f}M cheaper" if savings > 0 else "Similar price"
                st.markdown(f"""
                <div class="player-card">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div class="player-name">{row['name']}</div>
                            <div class="player-meta">{row.get('position','N/A')} · Age {row['age']:.0f} · {val}</div>
                            <div class="player-meta">G/90: {row['goals_per_90']} · A/90: {row['assists_per_90']}</div>
                        </div>
                        <div style="text-align:right">
                            <div class="score-badge">{row['similarity']:.0%} match</div>
                            <div style="font-size:10px;color:#6b7280;margin-top:4px">{savings_str}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ── TAB 4: SCOUT REPORT ───────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">Scouting Report Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Auto-generated professional scouting report based on player statistics</div>', unsafe_allow_html=True)

    report_player = st.selectbox("Select player", player_names, key="report")

    if st.button("Generate Scouting Report", type="primary"):
        p = profiles[profiles['name'] == report_player].iloc[0]
        val = f"€{p['market_value_in_eur']/1e6:.1f}M" if p['market_value_in_eur'] >= 1e6 else f"€{p['market_value_in_eur']/1e3:.0f}K"

        avg_g90 = profiles['goals_per_90'].median()
        avg_a90 = profiles['assists_per_90'].median()
        avg_val = profiles['market_value_in_eur'].median()

        g90 = p['goals_per_90']
        a90 = p['assists_per_90']
        gc90 = p['goal_contributions_per_90']
        age = p['age']
        apps = int(p['total_appearances']) if not pd.isna(p['total_appearances']) else 0
        mval = p['market_value_in_eur']

        if gc90 > (avg_g90 + avg_a90) * 1.5:
            perf_level = "elite"
        elif gc90 > (avg_g90 + avg_a90):
            perf_level = "above average"
        elif gc90 > avg_g90:
            perf_level = "average"
        else:
            perf_level = "below average"

        if mval < avg_val * 0.3 and perf_level in ["elite", "above average"]:
            value_rating = "Exceptional value — significantly underpriced for performance level"
            recommendation = "SIGN"
            rec_color = "#16a34a"
        elif mval < avg_val * 0.6 and perf_level in ["above average", "average"]:
            value_rating = "Good value — performing above market expectations"
            recommendation = "MONITOR"
            rec_color = "#d97706"
        elif mval > avg_val * 1.5:
            value_rating = "Premium priced — market value reflects reputation over current output"
            recommendation = "PASS"
            rec_color = "#dc2626"
        else:
            value_rating = "Fairly valued relative to current output"
            recommendation = "MONITOR"
            rec_color = "#d97706"

        if age < 21:
            age_note = "Young talent with significant development potential ahead."
        elif age < 24:
            age_note = "Early prime years — approaching peak performance window."
        elif age < 28:
            age_note = "In peak years — what you see is largely what you get."
        else:
            age_note = "Experienced player — limited resale value but proven quality."

        strengths = []
        if g90 > avg_g90 * 1.3:
            strengths.append(f"Strong goal threat — {g90} goals per 90 is above database median")
        if a90 > avg_a90 * 1.3:
            strengths.append(f"Creative output — {a90} assists per 90 shows consistent chance creation")
        if apps > 150:
            strengths.append(f"Proven durability — {apps} career appearances shows consistent availability")
        if age < 23 and gc90 > avg_g90:
            strengths.append("Young and already producing — high development ceiling")
        if mval < avg_val * 0.5:
            strengths.append("Low acquisition cost relative to output — excellent budget fit")
        if not strengths:
            strengths.append("Consistent contributor with steady output across appearances")

        weaknesses = []
        if g90 < avg_g90 * 0.7:
            weaknesses.append("Goal output below median — needs improvement in finishing or positioning")
        if a90 < avg_a90 * 0.7:
            weaknesses.append("Low assist rate — limited creative involvement in build-up")
        if apps < 30:
            weaknesses.append("Limited appearance record — small sample size, needs more data")
        if age > 27:
            weaknesses.append("Limited resale potential given age profile")
        if not weaknesses:
            weaknesses.append("No major statistical red flags identified at this stage")

        report = f"""
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);
                    border-radius:12px;padding:1.5rem;color:#d1d5db;font-size:13px;line-height:1.9">
            <div style="font-size:20px;font-weight:700;color:#ffffff;margin-bottom:4px">{p['name']}</div>
            <div style="font-size:12px;color:#6b7280;margin-bottom:1.5rem">
                {p.get('position','N/A')} · Age {age:.0f} · {p.get('current_club_name','N/A')} · {p.get('competition_name','N/A')} · {val}
            </div>
            <div style="font-size:11px;font-weight:600;color:#dc2626;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">Player Overview</div>
            <p>{p['name']} is a {age:.0f}-year-old {p.get('position','player')} currently at {p.get('current_club_name','their club')} in {p.get('competition_name','their league')}. With {apps} career appearances and a current market value of {val}, the player represents a <strong style="color:#ffffff">{perf_level}</strong> performance profile relative to the broader database. {age_note}</p>
            <div style="font-size:11px;font-weight:600;color:#dc2626;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;margin-top:1.2rem">Statistical Analysis</div>
            <p>Across {apps} appearances, {p['name']} has contributed {int(p['total_goals']) if not pd.isna(p['total_goals']) else 0} goals and {int(p['total_assists']) if not pd.isna(p['total_assists']) else 0} assists. On a per-90-minute basis this gives {g90} goals and {a90} assists, with a total contribution rate of {gc90} per 90. The database median is {(avg_g90+avg_a90):.2f} per 90 — placing this player in the <strong style="color:#ffffff">{perf_level}</strong> tier.</p>
            <div style="font-size:11px;font-weight:600;color:#dc2626;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;margin-top:1.2rem">Strengths</div>
            {''.join(f'<p>· {s}</p>' for s in strengths)}
            <div style="font-size:11px;font-weight:600;color:#dc2626;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;margin-top:1.2rem">Areas for Development</div>
            {''.join(f'<p>· {w}</p>' for w in weaknesses)}
            <div style="font-size:11px;font-weight:600;color:#dc2626;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;margin-top:1.2rem">Value Assessment</div>
            <p>{value_rating}. Current value of {val} against a database median of €{avg_val/1e6:.1f}M places this player in a {'below' if mval < avg_val else 'above'} average price bracket.</p>
            <div style="font-size:11px;font-weight:600;color:#dc2626;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;margin-top:1.2rem">FCM Fit Assessment</div>
            <p>FC Midtjylland's recruitment model prioritises young, high-output players from underexplored markets with strong per-90 metrics and low acquisition costs. Based on available data, {p['name']} {'aligns well' if recommendation != 'PASS' else 'does not strongly align'} with this model.</p>
            <div style="margin-top:1.5rem;padding:1rem;background:rgba(0,0,0,0.3);border-radius:8px;display:flex;align-items:center;gap:1rem">
                <div style="font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:1px">Scout Recommendation</div>
                <div style="font-size:16px;font-weight:700;color:{rec_color};background:rgba(0,0,0,0.3);padding:6px 20px;border-radius:20px;border:1px solid {rec_color}">{recommendation}</div>
            </div>
        </div>
        """
        st.markdown(report.strip(), unsafe_allow_html=True)