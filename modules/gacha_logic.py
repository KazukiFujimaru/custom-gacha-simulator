def perform_one_pull(current_state, config, rng):
    """
    Mensimulasikan satu tarikan gacha dengan logika Pity Independen yang akurat.
    Setiap rarity memiliki jalur pity dan rate-nya sendiri.
    """
    state = current_state.copy()
    pity_enabled = config.get('pity_enabled', True)

    # 1. Tambah pity counter untuk semua rarity di awal tarikan
    if pity_enabled:
        for rarity_level in state['pity_counters']:
            state['pity_counters'][rarity_level] += 1

    rarities_config = config.get('rarities', {})
    if not rarities_config:
        return {'rarity': 3, 'name': 'Item Bintang 3', 'is_rate_up': False}, state

    sorted_rarity_levels = sorted(rarities_config.keys(), key=int, reverse=True)

    # 2. Prioritas #1: Cek Hard Pity dari Tertinggi ke Terendah
    if pity_enabled:
        for rarity_level_str in sorted_rarity_levels:
            pity_counter = state['pity_counters'].get(rarity_level_str, 0)
            hard_pity_val = rarities_config[rarity_level_str].get('hard_pity', 0)

            if hard_pity_val > 0 and pity_counter >= hard_pity_val:
                # Jika hard pity kena, langsung berikan hasilnya dan hentikan proses
                return _get_win_result_and_update_state(rarity_level_str, config, state, rng)

    # 3. Prioritas #2: Lakukan "gulungan" probabilitas independen dari Tertinggi ke Terendah
    for rarity_level_str in sorted_rarity_levels:
        rarity_config = rarities_config[rarity_level_str]
        
        # Hitung rate saat ini, termasuk penyesuaian dari soft pity
        current_rate = rarity_config.get('rate', 0.0)
        if pity_enabled:
            soft_pity_config = rarity_config.get('soft_pity', {})
            if soft_pity_config.get('enabled'):
                pity_counter = state['pity_counters'].get(rarity_level_str, 0)
                soft_pity_start = soft_pity_config.get('start', 0)
                if soft_pity_start > 0 and pity_counter >= soft_pity_start:
                    increase_pulls = pity_counter - soft_pity_start + 1
                    increase_amount = increase_pulls * soft_pity_config.get('increase', 0.0)
                    current_rate += increase_amount
        
        # Lakukan "gulungan" independen untuk rarity ini menggunakan rng yang disediakan
        if rng.random() < current_rate:
            # Jika gulungan berhasil, berikan hasilnya dan hentikan proses
            return _get_win_result_and_update_state(rarity_level_str, config, state, rng)

    # 4. Prioritas #3: Jika tidak ada yang kena, berikan item default
    return {'rarity': 3, 'name': 'Item Bintang 3', 'is_rate_up': False}, state


def _get_win_result_and_update_state(rarity_level_str, config, state, rng):
    """
    Helper function untuk memproses kemenangan: menentukan rate-up,
    me-reset pity secara independen, dan mengembalikan hasil.
    """
    rarity_config = config['rarities'][rarity_level_str]
    is_rate_up = False
    
    # Tentukan apakah rate-up menggunakan rng yang di-pass
    rate_up_config = rarity_config.get('rate_up', {})
    if rate_up_config.get('enabled'):
        is_guaranteed = state['guaranteed_rate_up'].get(rarity_level_str, False)
        if is_guaranteed:
            is_rate_up = True
            state['guaranteed_rate_up'][rarity_level_str] = False
        else:
            # Gunakan rng yang sama untuk penentuan 50/50
            if rng.random() < rate_up_config.get('chance', 0.5):
                is_rate_up = True
            elif rate_up_config.get('guarantee_enabled'):
                state['guaranteed_rate_up'][rarity_level_str] = True

    # Buat objek hasil
    result = {
        'rarity': int(rarity_level_str),
        'name': f"Item Bintang {rarity_level_str}",
        'is_rate_up': is_rate_up
    }

    # PERBAIKAN UTAMA: Reset pity HANYA untuk rarity yang dimenangkan
    if config.get('pity_enabled', True):
        state['pity_counters'][rarity_level_str] = 0
    
    return result, state
