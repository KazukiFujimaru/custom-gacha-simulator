# fgo_analysis.py
# Skrip simulasi khusus untuk sistem gacha Fate/Grand Order.

import os
import hashlib
import collections
from datetime import datetime
from numpy.random import Generator, PCG64
import matplotlib.pyplot as plt

# --- Konfigurasi Simulasi FGO ---
GACHA_CONFIG = {
    'currency': { 'cost_in_rupiah': 49000 },
    'pulls_per_period': 40, # Perkiraan pull F2P per event/bulan
    'rarities': {
        '5': { 'rate': 0.01, 'rate_up': { 'enabled': True, 'chance': 0.80 } },
        '4': { 'rate': 0.03, 'rate_up': { 'enabled': False } },
        '3': { 'rate': 0.40, 'rate_up': { 'enabled': False } },
        # Craft Essence (CE) kita anggap sebagai rarity '0' untuk penyederhanaan
        '0': { 'rate': 0.56, 'rate_up': { 'enabled': False } } 
    },
    'pity': {
        'enabled': True,
        'hard_pity_5_star_at': 330
    }
}

# --- Logika Inti Gacha (Disesuaikan untuk FGO) ---
def create_seed():
    time_seed = str(datetime.now().timestamp()).encode('utf-8')
    os_seed = os.urandom(32)
    return int.from_bytes(hashlib.sha256(time_seed + os_seed).digest(), 'big')

def perform_one_fgo_pull(state, config, rng):
    """Mensimulasikan satu tarikan FGO."""
    state['pity_5_star'] += 1
    random_pull = rng.random()
    
    # Cek Hard Pity
    if config['pity']['enabled'] and state['pity_5_star'] >= config['pity']['hard_pity_5_star_at']:
        is_rate_up = rng.random() < config['rarities']['5']['rate_up']['chance']
        result = {'rarity': 5, 'is_rate_up': is_rate_up}
        state['pity_5_star'] = 0
        return result, state

    # Cek pull normal
    cumulative_rate = 0.0
    for rarity_str, rarity_config in config['rarities'].items():
        cumulative_rate += rarity_config['rate']
        if random_pull < cumulative_rate:
            rarity = int(rarity_str)
            is_rate_up = False
            if rarity == 5 and rarity_config['rate_up']['enabled']:
                is_rate_up = rng.random() < rarity_config['rate_up']['chance']
            
            result = {'rarity': rarity, 'is_rate_up': is_rate_up}
            if rarity == 5:
                state['pity_5_star'] = 0 # Reset pity jika dapat *5
            return result, state
    
    # Fallback, seharusnya tidak pernah tercapai jika rate total = 1.0
    return {'rarity': 0, 'is_rate_up': False}, state


# --- Fungsi Analisis & Visualisasi ---
def plot_distribution(rarity_counts, total_pulls):
    labels_map = {'5': '★5 Servant', '4': '★4', '3': '★3', '0': 'Craft Essence'}
    sorted_rarities = sorted(rarity_counts.keys(), key=int, reverse=True)
    labels = [labels_map.get(r, f"★{r}") for r in sorted_rarities]
    values = [rarity_counts[r] for r in sorted_rarities]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color=['#f8b500', '#a36eff', '#82a8d9', '#cccccc'])
    ax.set_ylabel('Jumlah Diperoleh')
    ax.set_title(f'Distribusi Hasil Gacha FGO dari {total_pulls:,} Tarikan (Efektif)')
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:,}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    plt.tight_layout()
    plt.show()

def run_fgo_simulation(paid_pulls, config):
    """Menjalankan simulasi FGO dengan memperhitungkan bonus pull."""
    print(f"Memulai simulasi FGO untuk {paid_pulls:,} tarikan berbayar...")
    
    rng = Generator(PCG64(create_seed()))
    state = {'pity_5_star': 0}
    
    rarity_counts = collections.defaultdict(int)
    rate_on_5_star_count = 0
    total_effective_pulls = 0

    # Simulasi dengan mekanik 10+1
    num_batches = paid_pulls // 10
    remaining_pulls = paid_pulls % 10

    for i in range(num_batches):
        for _ in range(11): # 10 pull berbayar + 1 bonus
            result, state = perform_one_fgo_pull(state, config, rng)
            rarity_counts[str(result['rarity'])] += 1
            if result['rarity'] == 5 and result['is_rate_up']:
                rate_on_5_star_count += 1
        total_effective_pulls += 11
        if (i+1) % 1000 == 0: print(f"  ...batch ke-{(i+1):,} selesai")

    # Sisa pull yang tidak dalam batch 10
    for _ in range(remaining_pulls):
        result, state = perform_one_fgo_pull(state, config, rng)
        rarity_counts[str(result['rarity'])] += 1
        if result['rarity'] == 5 and result['is_rate_up']:
            rate_on_5_star_count += 1
    total_effective_pulls += remaining_pulls

    print("\n--- Analisis Hasil Simulasi FGO ---")

    rupiah_per_pull = config['currency']['cost_in_rupiah']
    
    if rate_on_5_star_count > 0:
        avg_paid_pulls_for_rate_on = paid_pulls / rate_on_5_star_count
        avg_cost_for_rate_on = avg_paid_pulls_for_rate_on * rupiah_per_pull
        avg_periods_for_rate_on = avg_paid_pulls_for_rate_on / config['pulls_per_period']
        
        print(f"Total ★5 Rate On diperoleh: {rate_on_5_star_count:,}")
        print(f"\nb. Uang rata-rata per ★5 Rate On: Rp {avg_cost_for_rate_on:,.0f}")
        print(f"   (Berdasarkan rata-rata {avg_paid_pulls_for_rate_on:,.2f} tarikan BERBAYAR per perolehan)")
        print(f"\nc. Periode rata-rata per ★5 Rate On: {avg_periods_for_rate_on:,.2f} periode")
    else:
        print("\nTidak ada ★5 Rate On yang diperoleh. Coba jumlah tarikan lebih besar.")

    plot_distribution(rarity_counts, total_effective_pulls)

if __name__ == "__main__":
    TOTAL_PAID_PULLS = 300000  # Jumlah tarikan yang dibeli
    run_fgo_simulation(TOTAL_PAID_PULLS, GACHA_CONFIG)

