# gacha_analysis.py
# Skrip untuk simulasi gacha massal dan analisis statistik.
# Menggunakan NumPy untuk performa dan Matplotlib untuk visualisasi.

import os
import hashlib
import collections
from datetime import datetime
from numpy.random import Generator, PCG64
import matplotlib.pyplot as plt

# --- Konfigurasi Simulasi ---
# Ganti nilai-nilai ini untuk menguji skenario yang berbeda.

# Konfigurasi utama yang mendefinisikan aturan main gacha.
# Struktur ini sengaja dibuat sama dengan versi web untuk konsistensi.
GACHA_CONFIG = {
    # Pengaturan Global
    'pity_enabled': True,
    'pulls_per_period': 80,  # Rata-rata tarikan gratis yang didapat per periode/patch

    # Pengaturan Mata Uang
    'currency': {
        'cost_per_pull': 160,       # Biaya mata uang gacha untuk 1x tarikan
        'cost_in_rupiah': 30000,    # Nilai Rupiah yang setara untuk 160 mata uang gacha
    },

    # Pengaturan per Rarity
    'rarities': {
        '5': {
            'rate': 0.006,
            'hard_pity': 90,
            'soft_pity': { 'enabled': True, 'start': 74, 'increase': 0.06 },
            'rate_up': { 'enabled': True, 'chance': 0.50, 'guarantee_enabled': True }
        },
        '4': {
            'rate': 0.051,
            'hard_pity': 10,
            'soft_pity': { 'enabled': False },
            'rate_up': { 'enabled': False }
        },
        '3': {
            'rate': 1.0 - 0.006 - 0.051, # Sisanya adalah rate bintang 3
            'hard_pity': 0,
            'soft_pity': { 'enabled': False },
            'rate_up': { 'enabled': False }
        }
    }
}


# --- Logika Inti Gacha (Sama seperti versi web) ---

def create_seed():
    """
    Membuat seed yang sangat acak dengan menggabungkan timestamp presisi tinggi
    dan byte acak dari sistem operasi.
    """
    time_seed = str(datetime.now().timestamp()).encode('utf-8')
    os_seed = os.urandom(32)
    combined_seed = time_seed + os_seed
    hashed_seed = hashlib.sha256(combined_seed).digest()
    # NumPy PCG64 bisa menerima integer besar secara langsung
    return int.from_bytes(hashed_seed, 'big')

def perform_one_pull(current_state, config, rng):
    """
    Mensimulasikan satu tarikan gacha dengan konfigurasi dinamis.
    Fungsi ini adalah jantung dari simulasi.
    """
    state = current_state
    
    # Tingkatkan Pity Counters jika sistem pity aktif
    if config.get('pity_enabled', False):
        for rarity_level_str in state['pity_counters']:
            state['pity_counters'][rarity_level_str] += 1
    
    random_pull = rng.random()
    
    result = {'rarity': 3, 'name': 'Item Bintang 3', 'is_rate_up': False}
    
    sorted_rarities = sorted(config.get('rarities', {}).keys(), key=int, reverse=True)
    cumulative_rate = 0.0

    for rarity_level_str in sorted_rarities:
        rarity_level = int(rarity_level_str)
        rarity_config = config['rarities'][rarity_level_str]
        
        pity_counter = state['pity_counters'].get(rarity_level_str, 0)
        hard_pity = rarity_config.get('hard_pity', 0)
        
        current_rate = rarity_config.get('rate', 0.0)
        soft_pity_config = rarity_config.get('soft_pity', {})
        
        if config.get('pity_enabled') and soft_pity_config.get('enabled') and soft_pity_config.get('start', 0) > 0 and pity_counter >= soft_pity_config.get('start', 0):
            increase_pulls = pity_counter - soft_pity_config.get('start', 0) + 1
            increase_amount = increase_pulls * soft_pity_config.get('increase', 0.0)
            current_rate += increase_amount

        has_hit_hard_pity = (config.get('pity_enabled') and hard_pity > 0 and pity_counter >= hard_pity)
        
        if has_hit_hard_pity or random_pull < (current_rate + cumulative_rate):
            is_rate_up = False
            rate_up_config = rarity_config.get('rate_up', {})

            if rate_up_config.get('enabled'):
                is_guaranteed = state['guaranteed_rate_up'].get(rarity_level_str, False)
                if is_guaranteed:
                    is_rate_up = True
                    state['guaranteed_rate_up'][rarity_level_str] = False
                else:
                    if rng.random() < rate_up_config.get('chance', 0.5):
                        is_rate_up = True
                    else:
                        is_rate_up = False
                        if rate_up_config.get('guarantee_enabled', False):
                            state['guaranteed_rate_up'][rarity_level_str] = True

            result = {
                'rarity': rarity_level,
                'name': f"Item Bintang {rarity_level}{' (Rate Up)' if is_rate_up else ''}",
                'is_rate_up': is_rate_up
            }
            
            if config.get('pity_enabled'):
                for level_to_reset_str in sorted_rarities:
                    if int(level_to_reset_str) <= rarity_level:
                        state['pity_counters'][level_to_reset_str] = 0
            
            return result, state
            
        cumulative_rate += rarity_config.get('rate', 0.0)

    # Jika tidak ada yang kena, kembalikan hasil default (Bintang 3)
    return result, state


# --- Fungsi Analisis & Visualisasi ---

def plot_distribution(rarity_counts, total_pulls):
    """Membuat dan menampilkan diagram batang dari distribusi hasil gacha."""
    
    # Urutkan rarity dari rendah ke tinggi untuk tampilan grafik yang logis
    sorted_rarities = sorted(rarity_counts.keys(), key=int)
    labels = [f"★{r}" for r in sorted_rarities]
    values = [rarity_counts[r] for r in sorted_rarities]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color=['#82a8d9', '#a36eff', '#f8b500'])

    ax.set_ylabel('Jumlah Diperoleh')
    ax.set_title(f'Distribusi Hasil Gacha dari {total_pulls:,} Tarikan')
    ax.set_ylim(0, max(values) * 1.15) # Beri ruang di atas bar tertinggi

    # Tambahkan label angka di atas setiap bar
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:,}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

def run_simulation(num_pulls, config):
    """
    Menjalankan simulasi gacha sebanyak `num_pulls` dan mencetak hasilnya.
    """
    print(f"Memulai simulasi untuk {num_pulls:,} tarikan...")

    # Inisialisasi RNG
    rng = Generator(PCG64(create_seed()))

    # Inisialisasi state awal
    state = {
        'pity_counters': {r: 0 for r in config['rarities']},
        'guaranteed_rate_up': {r: False for r in config['rarities']}
    }

    # Variabel untuk melacak statistik
    rarity_counts = collections.defaultdict(int)
    rate_on_5_star_count = 0

    for i in range(1, num_pulls + 1):
        result, state = perform_one_pull(state, config, rng)
        rarity_counts[result['rarity']] += 1
        
        if result['rarity'] == 5 and result['is_rate_up']:
            rate_on_5_star_count += 1
            
        if i % 10000 == 0:
            print(f"  ...mencapai tarikan ke-{i:,}")

    print("\n--- Analisis Hasil Simulasi ---")

    # Kalkulasi mata uang
    cost_per_pull = config['currency']['cost_per_pull']
    cost_in_rupiah = config['currency']['cost_in_rupiah']
    rupiah_per_pull = cost_in_rupiah 
    
    # Kalkulasi statistik 5-Star Rate On
    if rate_on_5_star_count > 0:
        avg_pulls_for_rate_on = num_pulls / rate_on_5_star_count
        avg_cost_for_rate_on = avg_pulls_for_rate_on * rupiah_per_pull
        avg_periods_for_rate_on = avg_pulls_for_rate_on / config['pulls_per_period']
        
        print(f"Total ★5 Rate On diperoleh: {rate_on_5_star_count:,}")
        print(f"\nb. Uang rata-rata per ★5 Rate On: Rp {avg_cost_for_rate_on:,.0f}")
        print(f"   (Berdasarkan rata-rata {avg_pulls_for_rate_on:,.2f} tarikan per perolehan)")
        
        print(f"\nc. Periode rata-rata per ★5 Rate On: {avg_periods_for_rate_on:,.2f} periode")
        print(f"   (Dengan asumsi {config['pulls_per_period']} tarikan per periode)")
    else:
        print("\nTidak ada ★5 Rate On yang diperoleh dalam simulasi ini.")
        print("Coba jalankan dengan jumlah tarikan yang lebih besar.")

    # Tampilkan grafik distribusi
    print("\na. Menampilkan grafik persebaran hasil...")
    plot_distribution(rarity_counts, num_pulls)


# --- Titik Masuk Skrip ---
if __name__ == "__main__":
    # Tentukan berapa banyak tarikan yang ingin disimulasikan
    TOTAL_PULLS = 100000  # Semakin besar, semakin akurat hasilnya
    
    run_simulation(TOTAL_PULLS, GACHA_CONFIG)

