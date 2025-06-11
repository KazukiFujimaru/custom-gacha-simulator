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

def perform_one_pull(current_state, config, rng):
    """
    Mensimulasikan satu tarikan gacha dengan konfigurasi dinamis,
    termasuk soft pity dan rate-up per-rarity yang dapat disesuaikan.
    """
    state = current_state.copy()
    state['pity_counters'] = state.get('pity_counters', {})
    state['guaranteed_rate_up'] = state.get('guaranteed_rate_up', {})
    
    # --- Tingkatkan Pity Counters ---
    if config.get('pity_enabled', False):
        for rarity_level_str in state['pity_counters']:
            state['pity_counters'][rarity_level_str] += 1
    
    random_pull = rng.random()
    
    # --- Inisialisasi Hasil Default ---
    result = {'rarity': 3, 'name': 'Item Bintang 3', 'is_rate_up': False}
    
    # --- Iterasi Rarity dari Tertinggi ke Terendah ---
    sorted_rarities = sorted(config.get('rarities', {}).keys(), key=int, reverse=True)
    
    cumulative_rate = 0.0

    for rarity_level_str in sorted_rarities:
        rarity_level = int(rarity_level_str)
        rarity_config = config['rarities'][rarity_level_str]
        
        pity_counter = state['pity_counters'].get(rarity_level_str, 0)
        hard_pity = rarity_config.get('hard_pity', 0)
        
        # --- Hitung Rate Saat Ini (Base + Soft Pity) ---
        current_rate = rarity_config.get('rate', 0.0)
        soft_pity_config = rarity_config.get('soft_pity', {})
        if config.get('pity_enabled') and soft_pity_config.get('enabled') and soft_pity_config.get('start', 0) > 0 and pity_counter >= soft_pity_config.get('start', 0):
            increase_pulls = pity_counter - soft_pity_config.get('start', 0) + 1
            increase_amount = increase_pulls * soft_pity_config.get('increase', 0.0)
            current_rate += increase_amount

        # --- Cek Hasil ---
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
                        # PERBAIKAN: Jaminan sekarang hanya bergantung pada config di level rarity
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
            
            break # Hentikan loop karena item sudah ditemukan
            
        cumulative_rate += rarity_config.get('rate', 0.0)

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