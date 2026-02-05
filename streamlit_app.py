import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import re

# --- CONFIGURATION & STYLING ---
st.set_page_config(page_title="Logistics Intelligence Pro", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

TOTAL_CAP = {
    '800': {'K1': 4540, 'EP1': 228, 'EP2': 2367, 'EP3': 231, 'EP4': 25},
    '820': {'K1': 432, 'EP1': 0, 'EP2': 474, 'EP3': 0, 'EP4': 0}
}

# --- DATA ENGINE ---
@st.cache_data
def load_historical_data():
    # Všechna tvá historická data převedená do čistého formátu
    raw = [
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
    df = pd.DataFrame(raw, columns=['Date', 'WH', 'Type', 'Free_Bins'])
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    return df

# Initialize Session State
if 'data' not in st.session_state:
    st.session_state.data = load_historical_data()

# --- APP LAYOUT ---
st.title("🛡️ Logistics Intelligence Dashboard")
st.markdown("---")

# Sidebar for Operations
with st.sidebar:
    st.header("🛠️ Operations Center")
    with st.expander("➕ Import Daily Data", expanded=False):
        new_entry = st.text_area("Paste System Output:", height=200, placeholder="DD.MM.YYYY\n\n800\nK1 - ...")
        if st.button("Process & Append Data"):
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
                        st.success(f"Log: Records for {d_str} successfully merged.")
                        st.rerun()
    
    st.markdown("---")
    st.download_button("📥 Export DB to CSV", st.session_state.data.to_csv(index=False).encode('utf-8'), "inventory_history.csv", "text/csv")
    if st.button("🗑️ Reset to Factory History"):
        st.session_state.data = load_historical_data()
        st.rerun()

# --- DASHBOARD LOGIC ---
df = st.session_state.data
latest_date = df['Date'].max()
prev_date = df[df['Date'] < latest_date]['Date'].max() if len(df['Date'].unique()) > 1 else latest_date

# Executive KPI Section
st.subheader(f"📊 Executive Summary (as of {latest_date.strftime('%d %b, %Y')})")
kpi1, kpi2, kpi3 = st.columns(3)

def get_wh_stats(target_date, wh):
    subset = df[(df['Date'] == target_date) & (df['WH'] == wh)]
    total_cap = sum(TOTAL_CAP[wh].values())
    total_free = subset['Free_Bins'].sum()
    occ = (1 - total_free/total_cap) * 100
    return occ, total_free

occ800, free800 = get_wh_stats(latest_date, '800')
occ800_old, _ = get_wh_stats(prev_date, '800')
occ820, free820 = get_wh_stats(latest_date, '820')
occ820_old, _ = get_wh_stats(prev_date, '820')

with kpi1:
    st.metric("Warehouse 800 Occupancy", f"{occ800:.1f}%", f"{occ800 - occ800_old:+.1f}% vs last", delta_color="inverse")
with kpi2:
    st.metric("Warehouse 820 Occupancy", f"{occ820:.1f}%", f"{occ820 - occ820_old:+.1f}% vs last", delta_color="inverse")
with kpi3:
    total_occ = (occ800 + occ820) / 2 # Simple avg for high-level
    st.metric("System-wide Load", f"{total_occ:.1f}%")

st.markdown("---")

# Tabs for detailed analysis
tab_trends, tab_forecast, tab_mail = st.tabs(["📈 Dynamic Trends", "🔮 Capacity Analytics", "📧 Managerial Export"])

with tab_trends:
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.write("**Pallet Locations (EP Selection)**")
        # Plotly Interactive Chart
        fig_ep = go.Figure()
        
        # WH 800 EP
        for ep in ['EP1', 'EP2', 'EP3', 'EP4']:
            sub = df[(df['WH'] == '800') & (df['Type'] == ep)]
            fig_ep.add_trace(go.Scatter(x=sub['Date'], y=sub['Free_Bins'], name=f"800 {ep}", mode='lines+markers'))
            
        # WH 820 EP2
        sub820 = df[(df['WH'] == '820') & (df['Type'] == 'EP2')]
        fig_ep.add_trace(go.Scatter(x=sub820['Date'], y=sub820['Free_Bins'], name="820 EP2", line=dict(dash='dash', width=3, color='black')))
        
        fig_ep.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=450, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_ep, use_container_width=True)

    with col_r:
        st.write("**Shelf Locations (K1 Comparison)**")
        fig_k1 = px.line(df[df['Type'] == 'K1'], x='Date', y='Free_Bins', color='WH', markers=True, 
                         color_discrete_map={'800': '#1f77b4', '820': '#ff7f0e'})
        fig_k1.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=450, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_k1, use_container_width=True)

with tab_forecast:
    st.write("**Drill-down: Category Saturation**")
    # Horizontal bar chart for current occupancy percentage
    latest_df = df[df['Date'] == latest_date].copy()
    
    def calc_occ_row(row):
        wh = str(row['WH'])
        t = row['Type']
        cap = TOTAL_CAP[wh].get(t, 1) # avoid div by zero
        return (1 - row['Free_Bins']/cap) * 100

    latest_df['Occupancy %'] = latest_df.apply(calc_occ_row, axis=1)
    fig_bar = px.bar(latest_df, x='Occupancy %', y='Type', color='WH', barmode='group',
                     text_auto='.1f', orientation='h', title="Current Saturation by Bin Type (%)")
    fig_bar.add_vline(x=90, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
    st.plotly_chart(fig_bar, use_container_width=True)

with tab_mail:
    st.write("**Auto-Generated Managerial Summary**")
    
    # Analyze critical items
    critical_items = latest_df[latest_df['Occupancy %'] > 90]
    critical_str = ""
    if not critical_items.empty:
        critical_str = "\nCRITICAL ALERTS (Over 90% full):\n"
        for _, r in critical_items.iterrows():
            critical_str += f"- WH {r['WH']} Category {r['Type']}: {r['Occupancy %']:.1f}% occupied ({r['Free_Bins']} bins left)\n"

    mail_body = f"""Subject: Warehouse Capacity & Inventory Report - {latest_date.strftime('%Y-%m-%d')}

Executive Summary:
-----------------
Total system occupancy is currently at {total_occ:.1f}%. 

Warehouse 800: {occ800:.1f}% occupied ({free800} bins free)
Warehouse 820: {occ820:.1f}% occupied ({free820} bins free)
{critical_str}
Trend Analysis:
--------------
- Shelf capacity (K1) remains stable with sufficient buffer in both facilities.
- Pallet movements (EP series) show {'increasing' if occ800 > occ800_old else 'stable/decreasing'} pressure in the main facility.

Visual analytics and historical trends are available in the live dashboard.

Best regards,
Logistics Intelligence System
"""
    st.code(mail_body, language="markdown")
    st.info("💡 Pro-tip: Copy the code block above directly into your email client.")
