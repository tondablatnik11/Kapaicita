import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os

# =================================================================
# NASTAVENÍ CELKOVÝCH KAPACIT
# =================================================================
TOTAL_CAP = {
    '800': {'K1': 4540, 'EP1': 228, 'EP2': 2367, 'EP3': 231, 'EP4': 25},
    '820': {'K1': 432, 'EP1': 0, 'EP2': 474, 'EP3': 0, 'EP4': 0}
}

# =================================================================
# SEM VLOŽ NOVÁ DATA (TEXTOVÝ BLOK)
# =================================================================
NEW_RAW_INPUT = """
05.02.2026

800
K1 - 1926
EP1 - 20
EP2 - 74 
EP3 - 46
EP4 - 2

820
K1 - 259
EP1 - 0
EP2 - 44
EP3 - 0
EP4 - 0
"""

def parse_input(text):
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
                'Date': pd.to_datetime(date, dayfirst=True),
                'WH': current_wh,
                'Type': pos_match.group(1),
                'Free_Bins': int(pos_match.group(2))
            })
    return pd.DataFrame(data)

def run_app():
    # 1. Načtení historie nebo vytvoření nové
    history_file = 'warehouse_history.csv'
    if os.path.exists(history_file):
        df_history = pd.read_csv(history_file)
        df_history['Date'] = pd.to_datetime(df_history['Date'])
    else:
        df_history = pd.DataFrame()

    # 2. Parsování nového vstupu
    new_df = parse_input(NEW_RAW_INPUT)
    if new_df is None:
        print("Chyba: Nebylo nalezeno datum nebo platná data.")
        return

    # 3. Sloučení a odstranění duplicit (pokud bys omylem spustil stejné datum 2x)
    df_combined = pd.concat([df_history, new_df]).drop_duplicates(subset=['Date', 'WH', 'Type'], keep='last')
    df_combined.to_csv(history_file, index=False)
    
    # Příprava pro grafy (Pivot)
    df_pivot = df_combined.pivot_table(index=['Date', 'WH'], columns='Type', values='Free_Bins').reset_index()
    df_pivot = df_pivot.sort_values('Date')

    # 4. GENEROVÁNÍ GRAFŮ
    sns.set_theme(style="whitegrid")
    latest_date_str = new_df['Date'].max().strftime('%d.%m.%Y')
    
    # Graf Palety
    plt.figure(figsize=(12, 6))
    wh800 = df_pivot[df_pivot['WH'] == '800']
    wh820 = df_pivot[df_pivot['WH'] == '820']
    
    plt.plot(wh820['Date'], wh820['EP2'], 'r-s', label='820 EP2 (Free)', linewidth=2)
    for ep in ['EP1', 'EP2', 'EP3', 'EP4']:
        if ep in wh800.columns:
            plt.plot(wh800['Date'], wh800[ep], label=f'800 {ep} (Free)')
    
    plt.title(f'Pallet Bins: Free Capacity Trend ({latest_date_str})')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('pallet_trend.png', dpi=300)

    # Graf K1
    plt.figure(figsize=(12, 6))
    plt.plot(wh800['Date'], wh800['K1'], 'tab:blue', marker='o', label='800 K1 (Free)')
    plt.plot(wh820['Date'], wh820['K1'], 'tab:orange', marker='o', label='820 K1 (Free)')
    plt.axhline(y=TOTAL_CAP['800']['K1'], color='tab:blue', linestyle='--', alpha=0.3)
    plt.axhline(y=TOTAL_CAP['820']['K1'], color='tab:orange', linestyle='--', alpha=0.3)
    plt.title(f'Shelf Bins (K1): Free vs Total Capacity ({latest_date_str})')
    plt.legend()
    plt.tight_layout()
    plt.savefig('shelf_trend.png', dpi=300)

    # 5. EXPORT PRO EMAIL
    with open('email_export.txt', 'w', encoding='utf-8') as f:
        f.write(f"SUBJECT: Warehouse Capacity Overview - {latest_date_str}\n\n")
        f.write(f"Dear Manager,\n\nBelow is the updated capacity status for warehouses 800 and 820:\n\n")
        
        for wh in ['800', '820']:
            wh_data = new_df[new_df['WH'] == wh]
            f.write(f"--- WAREHOUSE {wh} ---\n")
            total_wh_cap = sum(TOTAL_CAP[wh].values())
            total_wh_free = wh_data['Free_Bins'].sum()
            
            for _, row in wh_data.iterrows():
                t = row['Type']
                free = row['Free_Bins']
                cap = TOTAL_CAP[wh].get(t, 0)
                if cap > 0:
                    occ = (1 - free/cap) * 100
                    status = "!! CRITICAL !!" if occ > 90 else "OK"
                    f.write(f"  {t}: {free} free bins / {cap} total ({occ:.1f}% occupied) -> {status}\n")
            
            total_occ = (1 - total_wh_free/total_wh_cap) * 100
            f.write(f"Overall WH {wh} Occupancy: {total_occ:.1f}%\n\n")
        
        f.write("Historical trend charts are attached to this email.\n\nBest regards,\nYour Logistics Team")

    print(f"Hotovo! Grafy uloženy. Text pro email najdeš v 'email_export.txt'.")

if __name__ == "__main__":
    run_app()