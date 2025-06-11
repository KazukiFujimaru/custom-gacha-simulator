# hsr_analysis.py
# Skrip simulasi khusus untuk sistem gacha Honkai: Star Rail.

import os
import hashlib
import collections
from datetime import datetime
from numpy.random import Generator, PCG64
import matplotlib.pyplot as plt

# --- Konfigurasi Simulasi HSR ---
GACHA_CONFIG = {
    'currency': { 'cost_in_rupiah': 30000 },
    'pulls_per_period': 80,
    'rarities': {
        '5': { 
            'rate': 0.006, 
            'hard_pity': 90,
            'soft_pity': { 'enabled': True, 'start': 74, 'increase': 0.07 },
            'rate_up': { 'enabled': True, 'chance': 0.50, 'guarantee_enabled': True }
        },
        '4': { 
            'rate': 0.051, # Base rate, rate sebenarnya disesuaikan oleh pity
            'hard_pity': 10,
            'soft_pity': { 'enabled': False },
            'rate_up': { 'enabled': True, 'chance': 0.50, 'guarantee_enabled': True }
        },
        '3': { 'rate': 0.943 }
    }
}

# --- Logika Inti Gacha (Disesuaikan untuk HSR) ---
def create_seed():
    time_seed = str(datetime.now().timestamp()).encode('utf-8')
    os_seed = os.urandom(32)
    return int.from_bytes(hashlib.sha256(time_seed + os_seed).digest(), 'big')

def perform_one_hsr_pull(state, config, rng):
    """Mensimulasikan satu tarikan HSR dengan semua mekanik pity."""
    state['pity_5_star'] += 1
    state['pity_4_star'] += 1
    
    # Cek Hard Pity Bintang 5
    if state['pity_5_star'] >= config['rarities']['5']['hard_pity']:
        return get_5_star(state, config, rng)
    
    # Cek Hard Pity Bintang 4
    if state['pity_4_star'] >= config['rarities']['4']['hard_pity']:
        # Di jaminan ke-10, ada peluang 0.6% untuk dapat *5, sisanya *4
        if rng.random() < 0.006:
            return get_5_star(state, config, rng)
        else:
            return get_4_star(state, config, rng)

    # Cek pull normal
    random_pull = rng.random()
    rate_5_star = config['rarities']['5']['rate']
    
    # Hitung rate soft pity *5
    sp_config = config['rarities']['5']['soft_pity']
    if sp_config['enabled'] and state['pity_5_star'] >= sp_config['start']:
        increase = (state['pity_5_star'] - sp_config['start'] + 1) * sp_config['increase']
        rate_5_star += increase
        
    if random_pull < rate_5_star:
        return get_5_star(state, config, rng)
    
    if random_pull < rate_5_star + config['rarities']['4']['rate']:
        return get_4_star(state, config, rng)

    return {'rarity': 3, 'is_rate_up': False}, state

def get_5_star(state, config, rng):
    is_rate_up = False
    ru_config = config['rarities']['5']['rate_up']
    if ru_config['enabled']:
        if state['guaranteed_5_star']:
            is_rate_up = True
            state['guaranteed_5_star'] = False
        else:
            if rng.random() < ru_config['chance']:
                is_rate_up = True
            else:
                is_rate_up = False
                if ru_config['guarantee_enabled']:
                    state['guaranteed_5_star'] = True
    state['pity_5_star'] = 0
    state['pity_4_star'] = 0
    return {'rarity': 5, 'is_rate_up': is_rate_up}, state

def get_4_star(state, config, rng):
    is_rate_up = False
    ru_config = config['rarities']['4']['rate_up']
    if ru_config['enabled']:
        if state['guaranteed_4_star']:
            is_rate_up = True
            state['guaranteed_4_star'] = False
        else:
            if rng.random() < ru_config['chance']:
                is_rate_up = True
            else:
                is_rate_up = False
                if ru_config['guarantee_enabled']:
                    state['guaranteed_4_star'] = True
    state['pity_4_star'] = 0
    return {'rarity': 4, 'is_rate_up': is_rate_up}, state

# --- Fungsi Analisis & Visualisasi ---
def plot_distribution(rarity_counts, total_pulls):
    # ... (fungsi plot sama seperti FGO, bisa di-copy paste)
    labels_map = {'5': '★5', '4': '★4', '3': '★3'}
    sorted_rarities = sorted(rarity_counts.keys(), key=int, reverse=True)
    labels = [labels_map.get(str(r), f"★{r}") for r in sorted_rarities]
    values = [rarity_counts[r] for r in sorted_rarities]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color=['#f8b500', '#a36eff', '#82a8d9'])
    ax.set_ylabel('Jumlah Diperoleh')
    ax.set_title(f'Distribusi Hasil Gacha HSR dari {total_pulls:,} Tarikan')
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:,}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')
    plt.tight_layout()
    plt.show()

def run_hsr_simulation(num_pulls, config):
    print(f"Memulai simulasi HSR untuk {num_pulls:,} tarikan...")
    rng = Generator(PCG64(create_seed()))
    state = {'pity_5_star': 0, 'pity_4_star': 0, 'guaranteed_5_star': False, 'guaranteed_4_star': False}
    rarity_counts = collections.defaultdict(int)
    rate_on_5_star_count = 0

    for i in range(num_pulls):
        result, state = perform_one_hsr_pull(state, config, rng)
        rarity_counts[result['rarity']] += 1
        if result['rarity'] == 5 and result['is_rate_up']:
            rate_on_5_star_count += 1
        if (i+1) % 10000 == 0: print(f"  ...tarikan ke-{(i+1):,}")

    print("\n--- Analisis Hasil Simulasi HSR ---")
    rupiah_per_pull = config['currency']['cost_in_rupiah']
    if rate_on_5_star_count > 0:
        avg_pulls = num_pulls / rate_on_5_star_count
        avg_cost = avg_pulls * rupiah_per_pull
        avg_periods = avg_pulls / config['pulls_per_period']
        print(f"Total ★5 Rate On diperoleh: {rate_on_5_star_count:,}")
        print(f"\nb. Uang rata-rata per ★5 Rate On: Rp {avg_cost:,.0f}")
        print(f"   (Berdasarkan rata-rata {avg_pulls:,.2f} tarikan per perolehan)")
        print(f"\nc. Periode rata-rata per ★5 Rate On: {avg_periods:,.2f} periode")
    else:
        print("\nTidak ada ★5 Rate On yang diperoleh.")

    plot_distribution(rarity_counts, num_pulls)

if __name__ == "__main__":
    TOTAL_PULLS = 300000
    run_hsr_simulation(TOTAL_PULLS, GACHA_CONFIG)
