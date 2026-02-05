import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re

# --- CONFIGURATION & THEME ---
st.set_page_config(page_title="Logistics Intel: Tue/Thu Report", layout="wide")

TOTAL_CAP = {
    '800': {'K1': 4540, 'EP1': 228, 'EP2': 2367, 'EP3': 231, 'EP4': 25},
    '820': {'K1': 432, 'EP1': 0, 'EP2': 474, 'EP3': 0, 'EP4': 0}
}

# Calculate Grand Total EP Capacity (Pallets only)
GRAND_TOTAL_EP_CAP = 0
for wh in TOTAL_CAP:
    for t, cap in TOTAL_CAP[wh].items():
        if 'EP' in t:
            GRAND_TOTAL_EP_CAP += cap

# Factory Reset Data (Oct 2025 - Feb 2026)
@st.cache_data
def get_factory_data():
    raw = [('13.10.2025', '800', 'EP1', 1), ('13.10.2025', '800', 'EP2', 2), ('13.10.2025', '800', 'EP3', 43), ('13.10.2025', '800', 'EP4', 1), ('13.10.2025', '800', 'K1', 2036), ('13.10.2025', '820', 'EP1', 0), ('13.10.2025', '820', 'EP2', 205), ('13.10.2025', '820', 'EP3', 0), ('13.10.2025', '820', 'EP4', 0), ('13.10.2025', '820', 'K1', 226), ('16.10.2025', '800', 'K1', 1925), ('16.10.2025', '800', 'EP1', 0), ('16.10.2025', '800', 'EP2', 3), ('16.10.2025', '800', 'EP3', 1), ('16.10.2025', '800', 'EP4', 1), ('16.10.2025', '820', 'K1', 214), ('16.10.2025', '820', 'EP1', 0), ('16.10.2025', '820', 'EP2', 174), ('16.10.2025', '820', 'EP3', 0), ('16.10.2025', '820', 'EP4', 0), ('17.10.2025', '800', 'K1', 1922), ('17.10.2025', '800', 'EP1', 0), ('17.10.2025', '800', 'EP2', 83), ('17.10.2025', '800', 'EP3', 0), ('17.10.2025', '800', 'EP4', 1), ('17.10.2025', '820', 'K1', 215), ('17.10.2025', '820', 'EP1', 0), ('17.10.2025', '820', 'EP2', 98), ('17.10.2025', '820', 'EP3', 0), ('17.10.2025', '820', 'EP4', 0), ('20.10.2025', '800', 'K1', 1922), ('20.10.2025', '800', 'EP1', 0), ('20.10.2025', '800', 'EP2', 197), ('20.10.2025', '800', 'EP3', 0), ('20.10.2025', '800', 'EP4', 0), ('20.10.2025', '820', 'K1', 215), ('20.10.2025', '820', 'EP1', 0), ('20.10.2025', '820', 'EP2', 98), ('20.10.2025', '820', 'EP3', 0), ('20.10.2025', '820', 'EP4', 0), ('21.10.2025', '800', 'K1', 1887), ('21.10.2025', '800', 'EP1', 1), ('21.10.2025', '800', 'EP2', 141), ('21.10.2025', '800', 'EP3', 1), ('21.10.2025', '800', 'EP4', 0), ('21.10.2025', '820', 'K1', 215), ('21.10.2025', '820', 'EP1', 0), ('21.10.2025', '820', 'EP2', 91), ('21.10.2025', '820', 'EP3', 0), ('21.10.2025', '820', 'EP4', 0), ('22.10.2025', '800', 'K1', 1786), ('22.10.2025', '800', 'EP1', 0), ('22.10.2025', '800', 'EP2', 37), ('22.10.2025', '800', 'EP3', 5), ('22.10.2025', '800', 'EP4', 0), ('22.10.2025', '820', 'K1', 216), ('22.10.2025', '820', 'EP1', 0), ('22.10.2025', '820', 'EP2', 99), ('22.10.2025', '820', 'EP3', 0), ('22.10.2025', '820', 'EP4', 0), ('23.10.2025', '800', 'K1', 1735), ('23.10.2025', '800', 'EP1', 0), ('23.10.2025', '800', 'EP2', 4), ('23.10.2025', '800', 'EP3', 5), ('23.10.2025', '800', 'EP4', 0), ('23.10.2025', '820', 'K1', 224), ('23.10.2025', '820', 'EP1', 0), ('23.10.2025', '820', 'EP2', 99), ('23.10.2025', '820', 'EP3', 0), ('23.10.2025', '820', 'EP4', 0), ('24.10.2025', '800', 'K1', 1665), ('24.10.2025', '800', 'EP1', 0), ('24.10.2025', '800', 'EP2', 1), ('24.10.2025', '800', 'EP3', 1), ('24.10.2025', '800', 'EP4', 0), ('24.10.2025', '820', 'K1', 230), ('24.10.2025', '820', 'EP1', 0), ('24.10.2025', '820', 'EP2', 56), ('24.10.2025', '820', 'EP3', 0), ('24.10.2025', '820', 'EP4', 0), ('27.10.2025', '800', 'K1', 1493), ('27.10.2025', '800', 'EP1', 8), ('27.10.2025', '800', 'EP2', 63), ('27.10.2025', '800', 'EP3', 28), ('27.10.2025', '800', 'EP4', 0), ('27.10.2025', '820', 'K1', 172), ('27.10.2025', '820', 'EP1', 0), ('27.10.2025', '820', 'EP2', 55), ('27.10.2025', '820', 'EP3', 0), ('27.10.2025', '820', 'EP4', 0), ('28.10.2025', '800', 'K1', 1430), ('28.10.2025', '800', 'EP1', 7), ('28.10.2025', '800', 'EP2', 44), ('28.10.2025', '800', 'EP3', 23), ('28.10.2025', '800', 'EP4', 0), ('28.10.2025', '820', 'K1', 173), ('28.10.2025', '820', 'EP1', 0), ('28.10.2025', '820', 'EP2', 60), ('28.10.2025', '820', 'EP3', 0), ('28.10.2025', '820', 'EP4', 0), ('29.10.2025', '800', 'K1', 1439), ('29.10.2025', '800', 'EP1', 8), ('29.10.2025', '800', 'EP2', 90), ('29.10.2025', '800', 'EP3', 27), ('29.10.2025', '800', 'EP4', 0), ('29.10.2025', '820', 'K1', 170), ('29.10.2025', '820', 'EP1', 0), ('29.10.2025', '820', 'EP2', 64), ('29.10.2025', '820', 'EP3', 0), ('29.10.2025', '820', 'EP4', 0), ('30.10.2025', '800', 'K1', 1438), ('30.10.2025', '800', 'EP1', 8), ('30.10.2025', '800', 'EP2', 107), ('30.10.2025', '800', 'EP3', 28), ('30.10.2025', '800', 'EP4', 0), ('30.10.2025', '820', 'K1', 171), ('30.10.2025', '820', 'EP1', 0), ('30.10.2025', '820', 'EP2', 62), ('30.10.2025', '820', 'EP3', 0), ('30.10.2025', '820', 'EP4', 0), ('31.10.2025', '800', 'K1', 1466), ('31.10.2025', '800', 'EP1', 12), ('31.10.2025', '800', 'EP2', 112), ('31.10.2025', '800', 'EP3', 25), ('31.10.2025', '800', 'EP4', 0), ('31.10.2025', '820', 'K1', 176), ('31.10.2025', '820', 'EP1', 0), ('31.10.2025', '820', 'EP2', 69), ('31.10.2025', '820', 'EP3', 0), ('31.10.2025', '820', 'EP4', 0), ('03.11.2025', '800', 'K1', 1504), ('03.11.2025', '800', 'EP1', 12), ('03.11.2025', '800', 'EP2', 144), ('03.11.2025', '800', 'EP3', 31), ('03.11.2025', '800', 'EP4', 0), ('03.11.2025', '820', 'K1', 196), ('03.11.2025', '820', 'EP1', 0), ('03.11.2025', '820', 'EP2', 67), ('03.11.2025', '820', 'EP3', 0), ('03.11.2025', '820', 'EP4', 0), ('05.11.2025', '800', 'K1', 1543), ('05.11.2025', '800', 'EP1', 13), ('05.11.2025', '800', 'EP2', 136), ('05.11.2025', '800', 'EP3', 34), ('05.11.2025', '800', 'EP4', 0), ('05.11.2025', '820', 'K1', 211), ('05.11.2025', '820', 'EP1', 0), ('05.11.2025', '820', 'EP2', 74), ('05.11.2025', '820', 'EP3', 0), ('05.11.2025', '820', 'EP4', 0), ('06.11.2025', '800', 'K1', 1527), ('06.11.2025', '800', 'EP1', 11), ('06.11.2025', '800', 'EP2', 137), ('06.11.2025', '800', 'EP3', 35), ('06.11.2025', '800', 'EP4', 0), ('06.11.2025', '820', 'K1', 214), ('06.11.2025', '820', 'EP1', 0), ('06.11.2025', '820', 'EP2', 69), ('06.11.2025', '820', 'EP3', 0), ('06.11.2025', '820', 'EP4', 0), ('10.11.2025', '800', 'K1', 1501), ('10.11.2025', '800', 'EP1', 11), ('10.11.2025', '800', 'EP2', 229), ('10.11.2025', '800', 'EP3', 34), ('10.11.2025', '800', 'EP4', 0), ('10.11.2025', '820', 'K1', 205), ('10.11.2025', '820', 'EP1', 0), ('10.11.2025', '820', 'EP2', 67), ('10.11.2025', '820', 'EP3', 0), ('10.11.2025', '820', 'EP4', 0), ('21.11.2025', '800', 'K1', 1434), ('21.11.2025', '800', 'EP1', 17), ('21.11.2025', '800', 'EP2', 123), ('21.11.2025', '800', 'EP3', 30), ('21.11.2025', '800', 'EP4', 0), ('21.11.2025', '820', 'K1', 218), ('21.11.2025', '820', 'EP1', 0), ('21.11.2025', '820', 'EP2', 84), ('21.11.2025', '820', 'EP3', 0), ('21.11.2025', '820', 'EP4', 0), ('24.11.2025', '800', 'K1', 1445), ('24.11.2025', '800', 'EP1', 15), ('24.11.2025', '800', 'EP2', 138), ('24.11.2025', '800', 'EP3', 33), ('24.11.2025', '800', 'EP4', 2), ('24.11.2025', '820', 'K1', 223), ('24.11.2025', '820', 'EP1', 0), ('24.11.2025', '820', 'EP2', 93), ('24.11.2025', '820', 'EP3', 0), ('24.11.2025', '820', 'EP4', 0), ('25.11.2025', '800', 'K1', 1453), ('25.11.2025', '800', 'EP1', 15), ('25.11.2025', '800', 'EP2', 130), ('25.11.2025', '800', 'EP3', 33), ('25.11.2025', '800', 'EP4', 2), ('25.11.2025', '820', 'K1', 235), ('25.11.2025', '820', 'EP1', 0), ('25.11.2025', '820', 'EP2', 92), ('25.11.2025', '820', 'EP3', 0), ('25.11.2025', '820', 'EP4', 0), ('01.12.2025', '800', 'K1', 1520), ('01.12.2025', '800', 'EP1', 17), ('01.12.2025', '800', 'EP2', 115), ('01.12.2025', '800', 'EP3', 43), ('01.12.2025', '800', 'EP4', 2), ('01.12.2025', '820', 'K1', 223), ('01.12.2025', '820', 'EP1', 0), ('01.12.2025', '820', 'EP2', 86), ('01.12.2025', '820', 'EP3', 0), ('01.12.2025', '820', 'EP4', 0), ('08.12.2025', '800', 'K1', 1560), ('08.12.2025', '800', 'EP1', 18), ('08.12.2025', '800', 'EP2', 73), ('08.12.2025', '800', 'EP3', 18), ('08.12.2025', '800', 'EP4', 3), ('08.12.2025', '820', 'K1', 243), ('08.12.2025', '820', 'EP1', 0), ('08.12.2025', '820', 'EP2', 74), ('08.12.2025', '820', 'EP3', 0), ('08.12.2025', '820', 'EP4', 0), ('16.12.2025', '800', 'K1', 1599), ('16.12.2025', '800', 'EP1', 17), ('16.12.2025', '800', 'EP2', 53), ('16.12.2025', '800', 'EP3', 17), ('16.12.2025', '800', 'EP4', 4), ('16.12.2025', '820', 'K1', 241), ('16.12.2025', '820', 'EP1', 0), ('16.12.2025', '820', 'EP2', 78), ('16.12.2025', '820', 'EP3', 0), ('16.12.2025', '820', 'EP4', 0), ('18.12.2025', '800', 'K1', 1557), ('18.12.2025', '800', 'EP1', 9), ('18.12.2025', '800', 'EP2', 65), ('18.12.2025', '800', 'EP3', 10), ('18.12.2025', '800', 'EP4', 3), ('18.12.2025', '820', 'K1', 256), ('18.12.2025', '820', 'EP1', 0), ('18.12.2025', '820', 'EP2', 63), ('18.12.2025', '820', 'EP3', 0), ('18.12.2025', '820', 'EP4', 0), ('13.01.2026', '800', 'K1', 1736), ('13.01.2026', '800', 'EP1', 7), ('13.01.2026', '800', 'EP2', 50), ('13.01.2026', '800', 'EP3', 20), ('13.01.2026', '800', 'EP4', 2), ('13.01.2026', '820', 'K1', 249), ('13.01.2026', '820', 'EP1', 0), ('13.01.2026', '820', 'EP2', 13), ('13.01.2026', '820', 'EP3', 0), ('13.01.2026', '820', 'EP4', 0), ('19.01.2026', '800', 'K1', 1817), ('19.01.2026', '800', 'EP1', 11), ('19.01.2026', '800', 'EP2', 88), ('19.01.2026', '800', 'EP3', 62), ('19.01.2026', '800', 'EP4', 2), ('19.01.2026', '820', 'K1', 248), ('19.01.2026', '820', 'EP1', 0), ('19.01.2026', '820', 'EP2', 26), ('19.01.2026', '820', 'EP3', 0), ('19.01.2026', '820', 'EP4', 0), ('22.01.2026', '800', 'K1', 1827), ('22.01.2026', '800', 'EP1', 13), ('22.01.2026', '800', 'EP2', 108), ('22.01.2026', '800', 'EP3', 59), ('22.01.2026', '800', 'EP4', 2), ('22.01.2026', '820', 'K1', 246), ('22.01.2026', '820', 'EP1', 0), ('22.01.2026', '820', 'EP2', 50), ('22.01.2026', '820', 'EP3', 0), ('22.01.2026', '820', 'EP4', 0), ('05.02.2026', '800', 'K1', 1926), ('05.02.2026', '800', 'EP1', 20), ('05.02.2026', '800', 'EP2', 74), ('05.02.2026', '800', 'EP3', 46), ('05.02.2026', '800', 'EP4', 2), ('05.02.2026', '820', 'K1', 259), ('05.02.2026', '820', 'EP1', 0), ('05.02.2026', '820', 'EP2', 44), ('05.02.2026', '820', 'EP3', 0), ('05.02.2026', '820', 'EP4', 0)]
    df = pd.DataFrame(raw, columns=['Date', 'WH', 'Type', 'Free_Bins'])
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    return df

if 'data' not in st.session_state:
    st.session_state.data = get_factory_data()

# --- SIDEBAR: HISTORY MANAGER ---
with st.sidebar:
    st.header("🗂️ History Manager")
    uploaded_file = st.file_uploader("Upload 'warehouse_history.csv' to resume", type="csv")
    if uploaded_file:
        df_up = pd.read_csv(uploaded_file)
        df_up['Date'] = pd.to_datetime(df_up['Date'])
        st.session_state.data = pd.concat([st.session_state.data, df_up]).drop_duplicates(subset=['Date', 'WH', 'Type']).sort_values('Date')
        st.success("History loaded successfully.")

    st.markdown("---")
    st.header("➕ Add New Data")
    new_entry = st.text_area("Paste Today's Output:", height=150, placeholder="DD.MM.YYYY\n\n800\nK1 - ...")
    if st.button("Merge New Data"):
        if new_entry:
            date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', new_entry)
            if date_match:
                d_str = date_match.group(1)
                p_date = pd.to_datetime(d_str, dayfirst=True)
                found = []
                wh = None
                for line in new_entry.split('\n'):
                    line = line.strip()
                    if line in ['800', '820']: wh = line
                    m = re.match(r'(K1|EP\d)\s*-\s*(\d+)', line)
                    if m and wh:
                        found.append({'Date': p_date, 'WH': wh, 'Type': m.group(1), 'Free_Bins': int(m.group(2))})
                if found:
                    new_df = pd.DataFrame(found)
                    st.session_state.data = pd.concat([st.session_state.data, new_df]).drop_duplicates(subset=['Date', 'WH', 'Type'], keep='last').sort_values('Date')
                    st.success(f"Merged: {d_str}")
                    st.rerun()

    st.markdown("---")
    st.download_button("💾 Download History CSV", st.session_state.data.to_csv(index=False).encode('utf-8'), "warehouse_history.csv", "text/csv")

# --- DASHBOARD LOGIC ---
df = st.session_state.data
latest_date = df['Date'].max()

st.title("🛡️ Logistics Intel Dashboard")
st.subheader(f"Status Report: {latest_date.strftime('%A, %d %B, %Y')}")

# --- EMAIL EXPORT LOGIC ---
st.markdown("### ✉️ Managerial Email Export")

latest_df = df[df['Date'] == latest_date].copy()

# Helper function to get summary stats
def get_wh_summary(wh):
    sub = latest_df[latest_df['WH'] == wh]
    total_cap = sum(TOTAL_CAP[wh].values())
    total_free = sub['Free_Bins'].sum()
    occ_pct = (1 - total_free/total_cap) * 100 if total_cap > 0 else 0
    return total_free, total_cap, occ_pct

f800, t800, p800 = get_wh_summary('800')
f820, t820, p820 = get_wh_summary('820')

# Helper function to format specific lines with percentage
def format_type_line(wh, type_name, label):
    row = latest_df[(latest_df['WH'] == wh) & (latest_df['Type'] == type_name)]
    if row.empty:
        return f"- {type_name} ({label}): Data missing"
    
    free = row['Free_Bins'].values[0]
    cap = TOTAL_CAP[wh].get(type_name, 0)
    
    if cap == 0:
        return f"- {type_name} ({label}): {free} free (Capacity 0)"
        
    occ_pct = (1 - free/cap) * 100
    return f"- {type_name} ({label}): {free} free out of {cap} ({occ_pct:.1f}% occupied)"

# --- AGGREGATE STATS CALCULATION ---
# Total Pallets (EP)
ep_cap_800 = sum([TOTAL_CAP['800'][k] for k in TOTAL_CAP['800'] if 'EP' in k])
ep_free_800 = latest_df[(latest_df['WH']=='800') & (latest_df['Type'].str.contains('EP'))]['Free_Bins'].sum()

ep_cap_820 = sum([TOTAL_CAP['820'][k] for k in TOTAL_CAP['820'] if 'EP' in k])
ep_free_820 = latest_df[(latest_df['WH']=='820') & (latest_df['Type'].str.contains('EP'))]['Free_Bins'].sum()

total_ep_cap = ep_cap_800 + ep_cap_820
total_ep_free = ep_free_800 + ep_free_820
total_ep_occ = (1 - total_ep_free/total_ep_cap)*100 if total_ep_cap > 0 else 0

# Total KLT (K1)
k1_cap_800 = TOTAL_CAP['800']['K1']
k1_free_800_series = latest_df[(latest_df['WH']=='800') & (latest_df['Type']=='K1')]['Free_Bins']
k1_free_800 = k1_free_800_series.values[0] if not k1_free_800_series.empty else 0

k1_cap_820 = TOTAL_CAP['820']['K1']
k1_free_820_series = latest_df[(latest_df['WH']=='820') & (latest_df['Type']=='K1')]['Free_Bins']
k1_free_820 = k1_free_820_series.values[0] if not k1_free_820_series.empty else 0

total_k1_cap = k1_cap_800 + k1_cap_820
total_k1_free = k1_free_800 + k1_free_820
total_k1_occ = (1 - total_k1_free/total_k1_cap)*100 if total_k1_cap > 0 else 0

# Construct the email body
email_body = f"""Subject: Warehouse Capacity Status - {latest_date.strftime('%Y-%m-%d')}

Hello Team,

Here is the current overview of free warehouse positions.

Global Category Statistics:
---------------------------
- Pallet Positions (EP): {total_ep_free} free out of {total_ep_cap} ({total_ep_occ:.1f}% occupied)
- KLT Positions (K1): {total_k1_free} free out of {total_k1_cap} ({total_k1_occ:.1f}% occupied)

Warehouse 800 Status:
---------------------
Total Occupancy: {p800:.1f}% 
Total Free Capacity: {f800} bins

Specific Free Positions:
{format_type_line('800', 'K1', 'Shelf')}
{format_type_line('800', 'EP1', 'Pallet')}
{format_type_line('800', 'EP2', 'Pallet')}
{format_type_line('800', 'EP3', 'Pallet')}
{format_type_line('800', 'EP4', 'Pallet')}

Warehouse 820 Status:
---------------------
Total Occupancy: {p820:.1f}% 
Total Free Capacity: {f820} bins

Specific Free Positions:
{format_type_line('820', 'K1', 'Shelf')}
{format_type_line('820', 'EP2', 'Pallet')}

Historical development and trend graphs are attached as visual references.

Best regards,
Logistics Team
"""

st.code(email_body, language="markdown")
st.info("💡 Copy the block above directly into your email client.")

# --- GRAPHS FOR EXPORT ---
st.divider()
st.subheader("📊 Graphs for Export (Screenshot these)")

col1, col2 = st.columns(2)

with col1:
    # 2-in-1 Graph: Pallet Details + Total Pallet Summary
    fig_ep = go.Figure()
    
    # 1. Individual Lines
    for ep in ['EP1', 'EP2', 'EP3', 'EP4']:
        sub = df[(df['WH'] == '800') & (df['Type'] == ep)]
        fig_ep.add_trace(go.Scatter(x=sub['Date'], y=sub['Free_Bins'], name=f"800 {ep}", opacity=0.7))
    
    sub820ep = df[(df['WH'] == '820') & (df['Type'] == 'EP2')]
    fig_ep.add_trace(go.Scatter(x=sub820ep['Date'], y=sub820ep['Free_Bins'], name="820 EP2", line=dict(dash='dash', color='cyan')))
    
    # 2. Total Pallet Line
    ep_total_df = df[df['Type'].str.contains('EP')].groupby('Date')['Free_Bins'].sum().reset_index()
    
    # Custom Hover Template displaying percentage
    ep_total_df['Pct_Free'] = (ep_total_df['Free_Bins'] / GRAND_TOTAL_EP_CAP) * 100
    
    fig_ep.add_trace(go.Scatter(
        x=ep_total_df['Date'], 
        y=ep_total_df['Free_Bins'], 
        name="TOTAL Pallets", 
        line=dict(color='white', width=4),
        hovertemplate="<b>TOTAL: %{y} free bins</b><br>Available Capacity: %{text:.1f}%<extra></extra>",
        text=ep_total_df['Pct_Free']
    ))
    
    fig_ep.update_layout(title="Evolution of Pallet Positions (Details + Total)", height=400, margin=dict(l=0,r=0,t=40,b=0))
    
    # Annotations & Markers
    fig_ep.add_vline(x=latest_date, line_width=2, line_dash="dot", line_color="#F4D03F")
    fig_ep.add_annotation(x=latest_date, y=1.05, yref='paper', text="Latest Status", showarrow=False, font=dict(color="#F4D03F"))
    
    st.plotly_chart(fig_ep, use_container_width=True)

with col2:
    # Graf 2: K1 Comparison (800 K1 vs 820 K1)
    fig_k1 = go.Figure()
    for wh in ['800', '820']:
        sub = df[(df['WH'] == wh) & (df['Type'] == 'K1')]
        fig_k1.add_trace(go.Scatter(x=sub['Date'], y=sub['Free_Bins'], name=f"{wh} K1"))
    
    fig_k1.update_layout(title="Evolution of Free Shelf Positions (K1)", height=400, margin=dict(l=0,r=0,t=40,b=0))
    fig_k1.add_vline(x=latest_date, line_width=2, line_dash="dot", line_color="#F4D03F")
    fig_k1.add_annotation(x=latest_date, y=1.05, yref='paper', text="Latest Status", showarrow=False, font=dict(color="#F4D03F"))
    st.plotly_chart(fig_k1, use_container_width=True)
