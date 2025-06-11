# arknights_analysis.py
# Skrip simulasi khusus untuk sistem gacha Arknights.

import os
import hashlib
import collections
from datetime import datetime
from numpy.random import Generator, PCG64
import matplotlib.pyplot as plt

# --- Konfigurasi Simulasi Arknights ---
GACHA_CONFIG = {
    'currency': { 'cost_in_rupiah': 18000 },
    'pulls_per_period': 60, # Perkiraan pull F2P per event/bulan
    'rarities': {
        '6': { 
            'rate': 0.02,
            'soft_pity': { 'enabled': True, 'start': 51, 'increase': 0.02 },
            'rate_up': { 'enabled': True, 'chance': 0.70, 'guarantee_enabled': False } # Asumsi rate up gabungan 70%
        },
        '5': { 'rate': 0.08 },
        '4': { 'rate': 0.50 },
        '3': { 'rate': 0.40 }
    }
}

# --- Logika Inti Gacha (Disesuaikan untuk Arknights) ---
def create_seed():
    time_seed = str(datetime.now().timestamp()).encode('utf-8')
    os_seed = os.urandom(32)
    return int.from_bytes(hashlib.sha256(time_seed + os_seed).digest(), 'big')

def perform_one_arknights_pull(state, config, rng):
    """Mensimulasikan satu tarikan Arknights."""
    state['pity_6_star'] += 1
    random_pull = rng.random()

    # Hitung rate *6 saat ini, dengan soft pity
    rate_6_star = config['rarities']['6']['rate']
    sp_config = config['rarities']['6']['soft_pity']
    if sp_config['enabled'] and state['pity_6_star'] >= sp_config['start']:
        increase = (state['pity_6_star'] - sp_config['start'] + 1) * sp_config['increase']
        rate_6_star += increase
    
    # Cek untuk *6
    if random_pull < rate_6_star:
        ru_config = config['rarities']['6']['rate_up']
        is_rate_up = ru_config['enabled'] and rng.random() < ru_config['chance']
        result = {'rarity': 6, 'is_rate_up': is_rate_up}
        state['pity_6_star'] = 0
        return result, state

    # Jika tidak dapat *6, cek rarity lain.
    # Rate *5, *4, *3 sekarang bersaing di sisa probabilitas (1.0 - rate_6_star)
    remaining_prob = 1.0 - rate_6_star
    prob_5_star = config['rarities']['5']['rate']
    prob_4_star = config['rarities']['4']['rate']
    
    # Skalakan ulang rate
    scale = remaining_prob / (prob_5_star + prob_4_star + config['rarities']['3']['rate'])
    scaled_prob_5 = scale * prob_5_star
    scaled_prob_4 = scale * prob_4_star
    
    # random_pull sekarang dibandingkan relatif terhadap sisa probabilitas
    # (random_pull - rate_6_star) menormalkan nilai acak ke rentang [0, remaining_prob]
    if random_pull - rate_6_star < scaled_prob_5:
        return {'rarity': 5, 'is_rate_up': False}, state
    
    if random_pull - rate_6_star < scaled_prob_5 + scaled_prob_4:
        return {'rarity': 4, 'is_rate_up': False}, state

    return {'rarity': 3, 'is_rate_up': False}, state

# --- Fungsi Analisis & Visualisasi ---
def plot_distribution(rarity_counts, total_pulls):
    labels_map = {'6': '★6', '5': '★5', '4': '★4', '3': '★3'}
    sorted_rarities = sorted(rarity_counts.keys(), key=int, reverse=True)
    labels = [labels_map.get(str(r), f"★{r}") for r in sorted_rarities]
    values = [rarity_counts[r] for r in sorted_rarities]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color=['#f8b500', '#e6a700', '#a36eff', '#82a8d9'])
    ax.set_ylabel('Jumlah Diperoleh')
    ax.set_title(f'Distribusi Hasil Gacha Arknights dari {total_pulls:,} Tarikan')
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:,}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    plt.tight_layout()
    plt.show()

def run_arknights_simulation(num_pulls, config):
    print(f"Memulai simulasi Arknights untuk {num_pulls:,} tarikan...")
    rng = Generator(PCG64(create_seed()))
    state = {'pity_6_star': 0}
    rarity_counts = collections.defaultdict(int)
    rate_on_6_star_count = 0

    for i in range(num_pulls):
        result, state = perform_one_arknights_pull(state, config, rng)
        rarity_counts[result['rarity']] += 1
        if result['rarity'] == 6 and result['is_rate_up']:
            rate_on_6_star_count += 1
        if (i+1) % 10000 == 0: print(f"  ...tarikan ke-{(i+1):,}")

    print("\n--- Analisis Hasil Simulasi Arknights ---")
    rupiah_per_pull = config['currency']['cost_in_rupiah']
    if rate_on_6_star_count > 0:
        avg_pulls = num_pulls / rate_on_6_star_count
        avg_cost = avg_pulls * rupiah_per_pull
        avg_periods = avg_pulls / config['pulls_per_period']
        print(f"Total ★6 Rate On diperoleh: {rate_on_6_star_count:,}")
        print(f"\nb. Uang rata-rata per ★6 Rate On: Rp {avg_cost:,.0f}")
        print(f"   (Berdasarkan rata-rata {avg_pulls:,.2f} tarikan per perolehan)")
        print(f"\nc. Periode rata-rata per ★6 Rate On: {avg_periods:,.2f} periode")
    else:
        print("\nTidak ada ★6 Rate On yang diperoleh.")

    plot_distribution(rarity_counts, num_pulls)

if __name__ == "__main__":
    TOTAL_PULLS = 300000
    run_arknights_simulation(TOTAL_PULLS, GACHA_CONFIG)

