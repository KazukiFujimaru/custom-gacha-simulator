import collections
from flask import Blueprint, render_template, jsonify, request
from modules import gacha_logic, rng_generator

app = Blueprint('gacha', __name__)

def configure_routes(app):
    @app.route('/')
    def index():
        """Menyajikan halaman utama simulator gacha."""
        return render_template('index.html')

    @app.route('/statistik')
    def statistics_page():
        """Menyajikan halaman statistik gacha."""
        return render_template('statistik.html')

    @app.route('/pull', methods=['POST'])
    def pull():
        """Endpoint API untuk melakukan tarikan gacha."""
        data = request.json
        pull_count = data.get('count', 1)
        current_state = data.get('state')
        config = data.get('config')

        if not all([isinstance(pull_count, int), isinstance(current_state, dict), isinstance(config, dict)]):
            return jsonify({'error': 'Invalid request data'}), 400

        results = []
        rng = rng_generator.rng

        for _ in range(pull_count):
            result, new_state = gacha_logic.perform_one_pull(current_state, config, rng)
            current_state = new_state
            current_state['total_pulls'] += 1
            results.append(result)

        return jsonify({
            'results': results,
            'final_state': current_state
        })

    @app.route('/api/run_statistics', methods=['POST'])
    def run_statistics():
        """Endpoint API untuk menjalankan simulasi gacha massal dan mengembalikan statistik."""
        data = request.json
        num_pulls = data.get('num_pulls', 100000)
        config = data.get('config')
        selected_rarities_for_stats = data.get('selected_rarities_for_stats', []) 
        
        # Jika tidak ada rarity yang dipilih, gunakan default 5
        if not selected_rarities_for_stats:
            selected_rarities_for_stats = [5]

        if not all([isinstance(num_pulls, int), isinstance(config, dict)]):
            return jsonify({'error': 'Invalid request data'}), 400

        rng_stats = rng_generator.rng

        state = {
            'pity_counters': {r: 0 for r in config['rarities']},
            'guaranteed_rate_up': {r: False for r in config['rarities']}
        }

        rarity_counts = collections.defaultdict(int)
        rate_up_counts = collections.defaultdict(int)
        
        total_pulls_simulated = 0

        # Run simulation
        for i in range(num_pulls):
            result, state = gacha_logic.perform_one_pull(state, config, rng_stats)
            rarity_counts[str(result['rarity'])] += 1
            if result['is_rate_up']:
                rate_up_counts[str(result['rarity'])] += 1
            total_pulls_simulated += 1

        cost_per_pull_in_game_currency = config['currency']['cost_per_pull']
        cost_in_rupiah_for_one_pull = config['currency']['cost_in_rupiah']
        pulls_per_period = config['pulls_per_period']

        total_gacha_currency = total_pulls_simulated * cost_per_pull_in_game_currency
        total_real_currency = total_pulls_simulated * cost_in_rupiah_for_one_pull
        total_periods = total_pulls_simulated / pulls_per_period if pulls_per_period > 0 else 0

        # Calculate per-rarity statistics
        detailed_rarity_stats = {}
        all_configured_rarities = sorted([int(r) for r in config['rarities'].keys()], reverse=True)

        # Filter and sort selected rarities to match config keys
        rarities_to_process = sorted([r for r in all_configured_rarities if r in selected_rarities_for_stats], reverse=True)

        for rarity_level in rarities_to_process:
            rarity_level_str = str(rarity_level)
            
            # General stats for this rarity
            total_obtained_this_rarity = rarity_counts.get(rarity_level_str, 0)
            
            avg_pulls_this_rarity = num_pulls / total_obtained_this_rarity if total_obtained_this_rarity > 0 else float('inf')
            avg_cost_this_rarity = avg_pulls_this_rarity * cost_in_rupiah_for_one_pull if avg_pulls_this_rarity != float('inf') else float('inf')
            avg_periods_this_rarity = avg_pulls_this_rarity / pulls_per_period if pulls_per_period > 0 and avg_pulls_this_rarity != float('inf') else float('inf')

            rarity_data = {
                'total_obtained': total_obtained_this_rarity,
                'avg_pulls': avg_pulls_this_rarity,
                'avg_cost': avg_cost_this_rarity,
                'avg_periods': avg_periods_this_rarity,
            }

            # Rate-up specific stats if enabled for this rarity
            rarity_config_data = config['rarities'].get(rarity_level_str, {})
            if rarity_config_data.get('rate_up', {}).get('enabled', False):
                total_rate_up_this_rarity = rate_up_counts.get(rarity_level_str, 0)
                
                avg_pulls_rate_up_this_rarity = num_pulls / total_rate_up_this_rarity if total_rate_up_this_rarity > 0 else float('inf')
                avg_cost_rate_up_this_rarity = avg_pulls_rate_up_this_rarity * cost_in_rupiah_for_one_pull if avg_pulls_rate_up_this_rarity != float('inf') else float('inf')
                avg_periods_rate_up_this_rarity = avg_pulls_rate_up_this_rarity / pulls_per_period if pulls_per_period > 0 and avg_pulls_rate_up_this_rarity != float('inf') else float('inf')
                
                rarity_data['rate_up_stats'] = {
                    'total_obtained': total_rate_up_this_rarity,
                    'avg_pulls': avg_pulls_rate_up_this_rarity,
                    'avg_cost': avg_cost_rate_up_this_rarity,
                    'avg_periods': avg_periods_rate_up_this_rarity,
                }
            
            detailed_rarity_stats[rarity_level_str] = rarity_data


        return jsonify({
            'total_pulls_simulated': total_pulls_simulated,
            'rarity_counts': rarity_counts, # Tetap kembalikan untuk grafik
            'rate_up_counts': rate_up_counts, # Tetap kembalikan jika diperlukan
            'selected_rarities_for_stats': selected_rarities_for_stats, 
            'total_gacha_currency_spent': total_gacha_currency,
            'total_real_currency_spent': total_real_currency,
            'total_periods_covered': total_periods,
            'detailed_rarity_stats': detailed_rarity_stats # BARU: Statistik detail per rarity
        })