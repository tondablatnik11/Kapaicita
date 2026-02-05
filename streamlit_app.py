import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# Nastavení stránky
st.set_page_config(page_title="Warehouse Capacity Dashboard", layout="wide")

# Konstanty kapacit
TOTAL_CAP = {
    '800': {'K1': 4540, 'EP1': 228, 'EP2': 2367, 'EP3': 231, 'EP4': 25},
    '820': {'K1': 432, 'EP1': 0, 'EP2': 474, 'EP3': 0, 'EP4': 0}
}

st.title("📦 Warehouse Capacity Dashboard")
st.markdown("Copy and paste your inventory data below to generate the report.")

# Vstupní pole pro data
raw_input = st.text_area("Input Data Block:", height=250, placeholder="05.02.2026\n\n800\nK1 - 1926\n...")

def parse_text(text):
    data = []
    date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
    if not date_match: return None
    date = date_match.group(1)
    
    current_wh = None
    for line in text.split('\n'):
        line = line.strip()
        if line in ['800', '820']:
            current_wh = line
            continue
        pos_match = re.match(r'(K1|EP\d)\s*-\s*(\d+)', line)
        if pos_match and current_wh:
            data.append({
                'Warehouse': current_wh,
                'Type': pos_match.group(1),
                'Free Bins': int(pos_match.group(2))
            })
    return pd.DataFrame(data), date

if st.button("Generate Report"):
    if raw_input:
        df, report_date = parse_text(raw_input)
        
        if df is not None:
            st.success(f"Report generated for: {report_date}")
            
            # Výpočty a statistiky
            col1, col2 = st.columns(2)
            
            for i, wh in enumerate(['800', '820']):
                with [col1, col2][i]:
                    st.subheader(f"Warehouse {wh}")
                    wh_df = df[df['Warehouse'] == wh]
                    
                    # Tabulka vytížení
                    results = []
                    total_wh_cap = sum(TOTAL_CAP[wh].values())
                    total_wh_free = wh_df['Free Bins'].sum()
                    
                    for _, row in wh_df.iterrows():
                        t = row['Type']
                        free = row['Free Bins']
                        cap = TOTAL_CAP[wh].get(t, 0)
                        if cap > 0:
                            occ = (1 - free/cap) * 100
                            results.append({"Type": t, "Free": free, "Total": cap, "Occupancy": f"{occ:.1f}%"})
                    
                    st.table(pd.DataFrame(results))
                    st.metric("Overall Occupancy", f"{(1 - total_wh_free/total_wh_cap)*100:.1f}%")

            # Grafy
            st.divider()
            st.subheader("Visual Analytics")
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            sns.set_theme(style="whitegrid")

            # Graf 1: Palety (EP)
            pal_df = df[df['Type'].str.contains('EP')]
            sns.barplot(data=pal_df, x='Type', y='Free Bins', hue='Warehouse', ax=ax1)
            ax1.set_title("Free Pallet Bins")

            # Graf 2: Regály (K1)
            k1_df = df[df['Type'] == 'K1']
            sns.barplot(data=k1_df, x='Warehouse', y='Free Bins', ax=ax2, palette="viridis")
            ax2.set_title("Free Shelf Bins (K1)")

            st.pyplot(fig)
            
            # Export pro email
            st.divider()
            st.subheader("Email Export (Copy & Paste)")
            email_text = f"Subject: Warehouse Capacity - {report_date}\n\nDear Manager,\n\nStatus for {report_date}:\n"
            for wh in ['800', '820']:
                wh_free = df[df['Warehouse']==wh]['Free Bins'].sum()
                wh_total = sum(TOTAL_CAP[wh].values())
                email_text += f"- WH {wh}: {(1-wh_free/wh_total)*100:.1f}% occupied\n"
            
            st.code(email_text)
            
        else:
            st.error("Could not parse data. Please check the format.")
    else:
        st.warning("Please enter data first.")
