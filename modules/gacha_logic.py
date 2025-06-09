from .rng_generator import rng

# --- Konfigurasi Gacha ---
GACHA_CONFIG = {
    'rate_5_star': 0.006,  # Probabilitas dasar mendapatkan bintang 5 (0.6%)
    'rate_4_star': 0.051,  # Probabilitas dasar mendapatkan bintang 4 (5.1%)
    'soft_pity_start': 74, # Soft pity untuk bintang 5 dimulai pada tarikan ke-74
    'hard_pity_5_star': 90, # Jaminan bintang 5 pada tarikan ke-90
    'hard_pity_4_star': 10, # Jaminan bintang 4 setiap 10 tarikan
    'soft_pity_increase': 0.06, # Peningkatan rate setiap tarikan setelah soft pity
    'rate_up_chance': 0.5, # Peluang 50% mendapatkan karakter rate-up saat dapat bintang 5
}

def perform_one_pull(current_state, config):
    """
    Mensimulasikan satu tarikan gacha tunggal, dengan mempertimbangkan semua
    mekanisme pity dan rate-up.
    """
    # Salin state untuk dimodifikasi
    state = current_state.copy()

    # Tingkatkan penghitung pity
    state['pity_5_star'] += 1
    state['pity_4_star'] += 1

    # Inisialisasi hasil tarikan
    result = {'rarity': 3, 'name': 'Item Bintang 3', 'is_rate_up': False}

    # Tentukan probabilitas bintang 5 saat ini, dengan mempertimbangkan soft pity
    current_5_star_rate = config['rate_5_star']
    if state['pity_5_star'] >= config['soft_pity_start']:
        increase_amount = (state['pity_5_star'] - config['soft_pity_start'] + 1) * config['soft_pity_increase']
        current_5_star_rate += increase_amount

    # Hasilkan angka acak antara 0.0 dan 1.0
    random_pull = rng.random()

    # --- Cek Hasil ---
    
    # Cek Hard Pity Bintang 5
    if state['pity_5_star'] >= config['hard_pity_5_star']:
        is_5_star = True
    else:
        is_5_star = random_pull < current_5_star_rate

    if is_5_star:
        rarity = 5
        # Cek rate up/off (50/50)
        if state['is_guaranteed_rate_up']:
            is_rate_up = True
            state['is_guaranteed_rate_up'] = False
        else:
            if rng.random() < config['rate_up_chance']:
                is_rate_up = True
            else:
                is_rate_up = False
                state['is_guaranteed_rate_up'] = True
        
        result = {'rarity': 5, 'name': f"Item Bintang 5 {'(Rate Up)' if is_rate_up else '(Rate Off)'}", 'is_rate_up': is_rate_up}
        state['pity_5_star'] = 0 # Reset pity 5-star
        state['pity_4_star'] = 0 # Reset pity 4-star juga (kebanyakan game begini)
    
    # Cek Hard Pity Bintang 4
    elif state['pity_4_star'] >= config['hard_pity_4_star']:
        result = {'rarity': 4, 'name': 'Item Bintang 4', 'is_rate_up': False}
        state['pity_4_star'] = 0 # Reset pity 4-star
        
    # Cek Rate Bintang 4
    elif random_pull < (current_5_star_rate + config['rate_4_star']):
        result = {'rarity': 4, 'name': 'Item Bintang 4', 'is_rate_up': False}
        state['pity_4_star'] = 0 # Reset pity 4-star

    return result, state

def perform_multiple_pulls(current_state, pull_count):
    """
    Melakukan multiple pulls dan mengembalikan hasil serta state akhir
    """
    results = []
    
    # Lakukan simulasi sebanyak jumlah tarikan
    for _ in range(pull_count):
        # Jalankan satu tarikan
        result, new_state = perform_one_pull(current_state, GACHA_CONFIG)
        # Perbarui state untuk tarikan berikutnya
        current_state = new_state
        # Tambahkan total pull
        current_state['total_pulls'] += 1
        results.append(result)
    
    return results, current_state