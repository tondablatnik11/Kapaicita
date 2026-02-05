import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re

# --- CONFIGURATION & THEME ---
st.set_page_config(page_title="Logistics Intelligence Dashboard", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# Total Bins Capacity (Based on user management specifications)
TOTAL_CAP = {
    '800': {'K1': 4540, 'EP1': 228, 'EP2': 2367, 'EP3': 231, 'EP4': 25},
    '820': {'K1': 432, 'EP1': 0, 'EP2': 474, 'EP3': 0, 'EP4': 0}
}

# --- DATA ENGINE: HISTORICAL ARCHIVE ---
@st.cache_data
def load_full_history():
    hist_raw = [
        ('13.10.2025', '800', 'EP1', 1), ('13.10.2025', '800', 'EP2', 2), ('13.10.2025', '800', 'EP3', 43), ('13.10.2025', '800', 'EP4', 1), ('13.10.2025', '800', 'K1', 2036),
        ('13.10.2025', '820', 'EP1', 0), ('13.10.2025', '820', 'EP2', 205), ('13.10.2025', '820', 'EP3', 0), ('13.10.2025', '820', 'EP4', 0), ('13.10.2025', '820', 'K1', 226),
        ('16.10.2025', '800', 'K1', 1925), ('16.10.2025', '800', 'EP1', 0), ('16.10.2025', '800', 'EP2', 3), ('16.10.2025', '800', 'EP3', 1), ('16.10.2025', '800', 'EP4', 1),
        ('16.10.2025', '820', 'K1', 214), ('16.10.2025', '820', 'EP1', 0), ('16.10.2025', '820', 'EP2', 174), ('16.10.2025', '820', 'EP3', 0), ('16.10.2025', '820', 'EP4', 0),
        ('17.10.2025', '800', 'K1', 1922), ('17.10.2025', '800', 'EP1', 0), ('17.10.2025', '800', 'EP2', 83), ('17.10.2025', '800', 'EP3', 0), ('17.10.2025', '800', 'EP4', 1),
        ('17.10.2025', '820', 'K1', 215), ('17.10.2025', '820', 'EP1', 0), ('17.10.2025', '820', 'EP2', 98), ('17.10.2025', '820', 'EP3', 0), ('17.10.2025', '820', 'EP4', 0),
        ('20.10.2025', '800', 'K1', 1922), ('20.10.2025', '800', 'EP1', 0), ('20.10.2025', '800', 'EP2', 197), ('20.10.2025', '800', 'EP3', 0), ('20.10.2025', '800', 'EP4', 0),
        ('20.10.2025', '820', 'K1', 215), ('20.10.2025', '820', 'EP1', 0), ('20.10.2025', '820', 'EP2', 98), ('20.10.2025', '820', 'EP3', 0), ('20.10.2025', '820', 'EP4', 0),
        ('21.10.2025', '800', 'K1', 1887), ('21.10.2025', '800', 'EP1', 1), ('21.10.2025', '800', 'EP2', 141), ('21.10.2025', '800', 'EP3', 1), ('21.10.2025', '800', 'EP4', 0),
        ('21.10.2025', '820', 'K1', 215), ('21.10.2025', '820', 'EP1', 0), ('21.10.2025', '820', 'EP2', 91), ('21.10.2025', '820', 'EP3', 0), ('21.10.2025', '820', 'EP4', 0),
        ('22.10.2025', '800', 'K1', 1786), ('22.10.2025', '800', 'EP1', 0), ('22.10.2025', '800', 'EP2', 37), ('22.10.2025', '800', 'EP3', 5), ('22.10.2025', '800', 'EP4', 0),
        ('22.10.2025', '820', 'K1', 216), ('22.10.2025', '820', 'EP1', 0), ('22.10.2025', '820', 'EP2', 99), ('22.10.2025', '820', 'EP3', 0), ('22.10.2025', '820', 'EP4', 0),
        ('23.10.2025', '800', 'K1', 1735), ('23.10.2025', '800', 'EP1', 0), ('23.10.2025', '800', 'EP2', 4), ('23.10.2025', '800', 'EP3', 5), ('23.10.2025', '800', 'EP4', 0),
        ('23.10.2025', '820', 'K1', 224), ('23.10.2025', '820', 'EP1', 0), ('23.10.2025', '820', 'EP2', 99), ('23.10.2025', '820', 'EP3', 0), ('23.10.2025', '820', 'EP4', 0),
        ('24.10.2025', '800', 'K1', 1665), ('24.10.2025', '800', 'EP1', 0), ('24.10.2025', '800', 'EP2', 1), ('24.10.2025', '800', 'EP3', 1), ('24.10.2025', '800', 'EP4', 0),
        ('24.10.2025', '820', 'K1', 230), ('24.10.2025', '820', 'EP1', 0), ('24.10.2025', '820', 'EP2', 56), ('24.10.2025', '820', 'EP3', 0), ('24.10.2025', '820', 'EP4', 0),
        ('27.10.2025', '800', 'K1', 1493), ('27.10.2025', '800', 'EP1', 8), ('27.10.2025', '800', 'EP2', 63), ('27.10.2025', '800', 'EP3', 28), ('27.10.2025', '800', 'EP4', 0),
        ('27.10.2025', '820', 'K1', 172), ('27.10.2025', '820', 'EP1', 0), ('27.10.2025', '820', 'EP2', 55), ('27.10.2025', '820', 'EP3', 0), ('27.10.2025', '820', 'EP4', 0),
        ('28.10.2025', '800', 'K1', 1430), ('28.10.2025', '800', 'EP1', 7), ('28.10.2025', '800', 'EP2', 44), ('28.10.2025', '800', 'EP3', 23), ('28.10.2025', '800', 'EP4', 0),
        ('28.10.2025', '820', 'K1', 173), ('28.10.2025', '820', 'EP1', 0), ('28.10.2025', '820', 'EP2', 60), ('28.10.2025', '820', 'EP3', 0), ('28.10.2025', '820', 'EP4', 0),
        ('29.10.2025', '800', 'K1', 1439), ('29.10.2025', '800', 'EP1', 8), ('29.10.2025', '800', 'EP2', 90), ('29.10.2025', '800', 'EP3', 27), ('29.10.2025', '800', 'EP4', 0),
        ('29.10.2025', '820', 'K1', 170), ('29.10.2025', '820', 'EP1', 0), ('29.10.2025', '820', 'EP2', 64), ('29.10.2025', '820', 'EP3', 0), ('29.10.2025', '820', 'EP4', 0),
        ('30.10.2025', '800', 'K1', 1438), ('30.10.2025', '800', 'EP1', 8), ('30.10.2025', '800', 'EP2', 107), ('30.10.2025', '800', 'EP3', 28), ('30.10.2025', '800', 'EP4', 0),
        ('30.10.2025', '820', 'K1', 171), ('30.10.2025', '820', 'EP1', 0), ('30.10.2025', '820', 'EP2', 62), ('30.10.2025', '820', 'EP3', 0), ('30.10.2025', '820', 'EP4', 0),
        ('31.10.2025', '800', 'K1', 1466), ('31.10.2025', '800', 'EP1', 12), ('31.10.2025', '800', 'EP2', 112), ('31.10.2025', '800', 'EP3', 25), ('31.10.2025', '800', 'EP4', 0),
        ('31.10.2025', '820', 'K1', 176), ('31.10.2025', '820', 'EP1', 0), ('31.10.2025', '820', 'EP2', 69), ('31.10.2025', '820', 'EP3', 0), ('31.10.2025', '820', 'EP4', 0),
        ('03.11.2025', '800', 'K1', 1504), ('03.11.2025', '800', 'EP1', 12), ('03.11.2025', '800', 'EP2', 144), ('03.11.2025', '800', 'EP3', 31), ('03.11.2025', '800', 'EP4', 0),
        ('03.11.2025', '820', 'K1', 196), ('03.11.2025', '820', 'EP1', 0), ('03.11.2025', '820', 'EP2', 67), ('03.11.2025', '820', 'EP3', 0), ('03.11.2025', '820', 'EP4', 0),
        ('05.11.2025', '800', 'K1', 1543), ('05.11.2025', '800', 'EP1', 13), ('05.11.2025', '800', 'EP2', 136), ('05.11.2025', '800', 'EP3', 34), ('05.11.2025', '800', 'EP4', 0),
        ('05.11.2025', '820', 'K1', 211), ('05.11.2025', '820', 'EP1', 0), ('05.11.2025', '820', 'EP2', 74), ('05.11.2025', '820', 'EP3', 0), ('05.11.2025', '820', 'EP4', 0),
        ('06.11.2025', '800', 'K1', 1527), ('06.11.2025', '800', 'EP1', 11), ('06.11.2025', '800', 'EP2', 137), ('06.11.2025', '800', 'EP3', 35), ('06.11.2025', '800', 'EP4', 0),
        ('06.11.2025', '820', 'K1', 214), ('06.11.2025', '820', 'EP1', 0), ('06.11.2025', '820', 'EP2', 69), ('06.11.2025', '820', 'EP3', 0), ('06.11.2025', '820', 'EP4', 0),
        ('10.11.2025', '800', 'K1', 1501), ('10.11.2025', '800', 'EP1', 11), ('10.11.2025', '800', 'EP2', 229), ('10.11.2025', '800', 'EP3', 34), ('10.11.2025', '800', 'EP4', 0),
        ('10.11.2025', '820', 'K1', 205), ('10.11.2025', '820', 'EP1', 0), ('10.11.2025', '820', 'EP2', 67), ('10.11.2025', '820', 'EP3', 0), ('10.11.2025', '820', 'EP4', 0),
        ('21.11.2025', '800', 'K1', 1434), ('21.11.2025', '800', 'EP1', 17), ('21.11.2025', '800', 'EP2', 123), ('21.11.2025', '800', 'EP3', 30), ('21.11.2025', '800', 'EP4', 0),
        ('21.11.2025', '820', 'K1', 218), ('21.11.2025', '820', 'EP1', 0), ('21.11.2025', '820', 'EP2', 84), ('21.11.2025', '820', 'EP3', 0), ('21.11.2025', '820', 'EP4', 0),
        ('24.11.2025', '800', 'K1', 1445), ('24.11.2025', '800', 'EP1', 15), ('24.11.2025', '800', 'EP2', 138), ('24.11.2025', '800', 'EP3', 33), ('24.11.2025', '800', 'EP4', 2),
        ('24.11.2025', '820', 'K1', 223), ('24.11.2025', '820', 'EP1', 0), ('24.11.2025', '820', 'EP2', 93), ('24.11.2025', '820', 'EP3', 0), ('24.11.2025', '820', 'EP4', 0),
        ('25.11.2025', '800', 'K1', 1453), ('25.11.2025', '800', 'EP1', 15), ('25.11.2025', '800', 'EP2', 130), ('25.11.2025', '800', 'EP3', 33), ('25.11.2025', '800', 'EP4', 2),
        ('25.11.2025', '820', 'K1', 235), ('25.11.2025', '820', 'EP1', 0), ('25.11.2025', '820', 'EP2', 92), ('25.11.2025', '820', 'EP3', 0), ('25.11.2025', '820', 'EP4', 0),
        ('01.12.2025', '800', 'K1', 1520), ('01.12.2025', '800', 'EP1', 17), ('01.12.2025', '800', 'EP2', 115), ('01.12.2025', '800', 'EP3', 43), ('01.12.2025', '800', 'EP4', 2),
        ('01.12.2025', '820', 'K1', 223), ('01.12.2025', '820', 'EP1', 0), ('01.12.2025', '820', 'EP2', 86), ('01.12.2025', '820', 'EP3', 0), ('01.12.2025', '820', 'EP4', 0),
        ('08.12.2025', '800', 'K1', 1560), ('08.12.2025', '800', 'EP1', 18), ('08.12.2025', '800', 'EP2', 73), ('08.12.2025', '800', 'EP3', 18), ('08.12.2025', '800', 'EP4', 3),
        ('08.12.2025', '820', 'K1', 243), ('08.12.2025', '820', 'EP1', 0), ('08.12.2025', '820', 'EP2', 74), ('08.12.2025', '820', 'EP3', 0), ('08.12.2025', '820', 'EP4', 0),
        ('16.12.2025', '800', 'K1', 1599), ('16.12.2025', '800', 'EP1', 17), ('16.12.2025', '800', 'EP2', 53), ('16.12.2025', '800', 'EP3', 17), ('16.12.2025', '800', 'EP4', 4),
        ('16.12.2025', '820', 'K1', 241), ('16.12.2025', '820', 'EP1', 0), ('16.12.2025', '820', 'EP2', 78), ('16.12.2025', '820', 'EP3', 0), ('16.12.2025', '820', 'EP4', 0),
        ('18.12.2025', '800', 'K1', 1557), ('18.12.2025', '800', 'EP1', 9), ('18.12.2025', '800', 'EP2', 65), ('18.12.2025', '800', 'EP3', 10), ('18.12.2025', '800', 'EP4', 3),
        ('18.12.2025', '820', 'K1', 256), ('18.12.2025', '820', 'EP1', 0), ('18.12.2025', '820', 'EP2', 63), ('18.12.2025', '820', 'EP3', 0), ('18.12.2025', '820', 'EP4', 0),
        ('13.01.2026', '800', 'K1', 1736), ('13.01.2026', '800', 'EP1', 7), ('13.01.2026', '800', 'EP2', 50), ('13.01.2026', '800', 'EP3', 20), ('13.01.2026', '800', 'EP4', 2),
        ('13.01.2026', '820', 'K1', 249), ('13.01.2026', '820', 'EP1', 0), ('13.01.2026', '820', 'EP2', 13), ('13.01.2026', '820', 'EP3', 0), ('13.01.2026', '820', 'EP4', 0),
        ('19.01.2026', '800', 'K1', 1817), ('19.01.2026', '800', 'EP1', 11), ('19.01.2026', '800', 'EP2', 88), ('19.01.2026', '800', 'EP3', 62), ('19.01.2026', '800', 'EP4', 2),
        ('19.01.2026', '820', 'K1', 248), ('19.01.2026', '820', 'EP1', 0), ('19.01.2026', '820', 'EP2', 26), ('19.01.2026', '820', 'EP3', 0), ('19.01.2026', '820', 'EP4', 0),
        ('22.01.2026', '800', 'K1', 1827), ('22.01.2026', '800', 'EP1', 13), ('22.01.2026', '800', 'EP2', 108), ('22.01.2026', '800', 'EP3', 59), ('22.01.2026', '800', 'EP4', 2),
        ('22.01.2026', '820', 'K1', 246), ('22.01.2026', '820', 'EP1', 0), ('22.01.2026', '820', 'EP2', 50), ('22.01.2026', '820', 'EP3', 0), ('22.01.2026', '820', 'EP4', 0),
    ]
    df = pd.DataFrame(hist_raw, columns=['Date', 'WH', 'Type', 'Free_Bins'])
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    return df

# --- SESSION INITIALIZATION ---
if 'data' not in st.session_state:
    st.session_state.data = load_full_history()

# --- APP LAYOUT ---
st.title("🛡️ Logistics Intelligence Dashboard Pro")
st.markdown("---")

# Sidebar for Daily Operations (Management focus)
with st.sidebar:
    st.header("⚙️ Daily Operations")
    with st.expander("📥 Import New Data Block", expanded=True):
        new_entry = st.text_area("Paste System Output:", height=200, placeholder="DD.MM.YYYY\n\n800\nK1 - ...")
        if st.button("🚀 Process & Append"):
            if new_entry:
                date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', new_entry)
                if date_match:
                    d_str = date_match.group(1)
                    parsed_date = pd.to_datetime(d_str, dayfirst=True)
                    
                    found_data = []
                    curr_wh = None
                    for line in new_entry.split('\n'):
                        line = line.strip()
                        if line in ['800', '820']: curr_wh = line
                        m = re.match(r'(K1|EP\d)\s*-\s*(\d+)', line)
                        if m and curr_wh:
                            found_data.append({'Date': parsed_date, 'WH': curr_wh, 'Type': m.group(1), 'Free_Bins': int(m.group(2))})
                    
                    if found_data:
                        new_df = pd.DataFrame(found_data)
                        st.session_state.data = pd.concat([st.session_state.data, new_df]).drop_duplicates(subset=['Date', 'WH', 'Type'], keep='last').sort_values('Date')
                        st.success(f"Records for {d_str} successfully merged.")
                        st.rerun()
                else:
                    st.error("No valid date format found.")
    
    st.markdown("---")
    st.download_button("📂 Backup History (CSV)", st.session_state.data.to_csv(index=False).encode('utf-8'), "warehouse_history.csv", "text/csv")
    if st.button("♻️ Factory Reset History"):
        st.session_state.data = load_full_history()
        st.rerun()

# --- KPI DASHBOARD ---
df = st.session_state.data
latest_date = df['Date'].max()
prev_date = df[df['Date'] < latest_date]['Date'].max() if len(df['Date'].unique()) > 1 else latest_date

st.subheader(f"📍 Real-time Inventory Status ({latest_date.strftime('%d %B, %Y')})")
kpi1, kpi2, kpi3 = st.columns(3)

def get_wh_stats(target_date, wh):
    subset = df[(df['Date'] == target_date) & (df['WH'] == wh)]
    total_cap = sum(TOTAL_CAP[wh].values())
    total_free = subset['Free_Bins'].sum()
    occ = (1 - (total_free / total_cap)) * 100 if total_cap > 0 else 0
    return occ, total_free

occ800, free800 = get_wh_stats(latest_date, '800')
occ800_old, _ = get_wh_stats(prev_date, '800')
occ820, free820 = get_wh_stats(latest_date, '820')
occ820_old, _ = get_wh_stats(prev_date, '820')

with kpi1:
    st.metric("WH 800 Load", f"{occ800:.1f}%", f"{occ800 - occ800_old:+.1f}% vs last", delta_color="inverse")
with kpi2:
    st.metric("WH 820 Load", f"{occ820:.1f}%", f"{occ820 - occ820_old:+.1f}% vs last", delta_color="inverse")
with kpi3:
    total_occ = (occ800 + occ820) / 2
    st.metric("Global System Load", f"{total_occ:.1f}%")

st.markdown("---")

# --- TREND ANALYTICS ---
tab_trends, tab_saturation, tab_mail = st.tabs(["📈 Interactive Trends", "📊 Capacity Analytics", "✉️ Email Export"])

with tab_trends:
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.markdown("**Pallet Storage (EP) Free Bins Trend**")
        fig_ep = go.Figure()
        # WH 800 Pallets
        for ep in ['EP1', 'EP2', 'EP3', 'EP4']:
            sub = df[(df['WH'] == '800') & (df['Type'] == ep)]
            fig_ep.add_trace(go.Scatter(x=sub['Date'], y=sub['Free_Bins'], name=f"800 {ep}", mode='lines+markers'))
        # WH 820 EP2
        sub820 = df[(df['WH'] == '820') & (df['Type'] == 'EP2')]
        fig_ep.add_trace(go.Scatter(x=sub820['Date'], y=sub820['Free_Bins'], name="820 EP2", line=dict(dash='dash', width=3, color='black')))
        fig_ep.update_layout(height=450, margin=dict(l=0, r=0, t=20, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_ep, use_container_width=True)

    with c_right:
        st.markdown("**Shelf Storage (K1) Free Bins Comparison**")
        fig_k1 = px.line(df[df['Type'] == 'K1'], x='Date', y='Free_Bins', color='WH', markers=True, color_discrete_map={'800': '#1f77b4', '820': '#ff7f0e'})
        fig_k1.update_layout(height=450, margin=dict(l=0, r=0, t=20, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_k1, use_container_width=True)

with tab_saturation:
    st.markdown("**Resource Saturation by Category (%)**")
    latest_df = df[df['Date'] == latest_date].copy()
    
    def calc_occ_row(row):
        wh, t = str(row['WH']), row['Type']
        cap = TOTAL_CAP[wh].get(t, 0)
        return (1 - (row['Free_Bins'] / cap)) * 100 if cap > 0 else 0

    latest_df['Occupancy %'] = latest_df.apply(calc_occ_row, axis=1)
    plot_df = latest_df[latest_df['Occupancy %'] > 0] # Filter out non-existent categories
    
    fig_bar = px.bar(plot_df, x='Occupancy %', y='Type', color='WH', barmode='group', text_auto='.1f', orientation='h')
    fig_bar.add_vline(x=90, line_dash="dash", line_color="red", annotation_text="90% Limit")
    st.plotly_chart(fig_bar, use_container_width=True)

with tab_mail:
    st.markdown("**Automated Managerial Summary**")
    crit = latest_df[latest_df['Occupancy %'] > 90]
    crit_str = "\nURGENT: CRITICAL SATURATION (>90%):\n" + "\n".join([f"- WH {r['WH']} {r['Type']}: {r['Occupancy %']:.1f}% occupied ({r['Free_Bins']} bins free)" for _, r in crit.iterrows()]) if not crit.empty else ""

    mail_body = f"""Subject: Warehouse Capacity Status - {latest_date.strftime('%Y-%m-%d')}

Executive Summary:
-----------------
Total system occupancy is {total_occ:.1f}%.
- Warehouse 800: {occ800:.1f}% utilized ({free800} bins free)
- Warehouse 820: {occ820:.1f}% utilized ({free820} bins free)
{crit_str}

Operational Highlights:
----------------------
- Shelf locations (K1) remain within operational parameters.
- Pallet zones (EP) show {'sustained high load' if occ800 > 85 else 'normal volatility'}.

Detailed analytics available in the Live Dashboard.

Best regards,
Logistics Monitoring System
"""
    st.code(mail_body, language="markdown")
    st.info("💡 Copy the block above directly into your email body.")
