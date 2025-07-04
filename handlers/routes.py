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
        rarities = config.get('rarities', {})
        total_rate = sum(rarity_config.get('rate', 0) for rarity_config in rarities.values())

        if not all([isinstance(pull_count, int), isinstance(current_state, dict), isinstance(config, dict)]):
            return jsonify({'error': 'Invalid request data'}), 400

        if total_rate > 1.0:
            breakdown = " + ".join([
                f"{rarity_config.get('rate', 0)*100:.1f}%" 
                for rarity_config in rarities.values()
            ])
            return jsonify({
                'error': (
                    "Persentase peluang gacha harus berjumlah maksimal 100% dari semua rarity.\n"
                    f"({breakdown} = {total_rate * 100:.1f}%)"
                )
            }), 400

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
        rarities = config.get('rarities', {})
        total_rate = sum(rarity_config.get('rate', 0) for rarity_config in rarities.values()) 
        
        exclude_3star = config.get('exclude_3star_from_chart', False)

        if not selected_rarities_for_stats:
            selected_rarities_for_stats = [5]

        if not all([isinstance(num_pulls, int), isinstance(config, dict)]):
            return jsonify({'error': 'Invalid request data'}), 400

        if total_rate > 1.0:
            breakdown = " + ".join([
                f"{rarity_config.get('rate', 0)*100:.1f}%" 
                for rarity_config in rarities.values()
            ])
            return jsonify({
                'error': (
                    "Persentase peluang gacha harus berjumlah maksimal 100% dari semua rarity.\n"
                    f"({breakdown} = {total_rate * 100:.1f}%)"
                )
            }), 400

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
        
        if exclude_3star and '3' in rarity_counts:
            del rarity_counts['3']

        cost_per_pull_in_game_currency = config['currency']['cost_per_pull']
        cost_in_rupiah_for_one_pull = config['currency']['cost_in_rupiah']
        pulls_per_period = config['pulls_per_period']

        total_gacha_currency = total_pulls_simulated * cost_per_pull_in_game_currency
        total_real_currency = (total_gacha_currency / cost_per_pull_in_game_currency) * cost_in_rupiah_for_one_pull if cost_per_pull_in_game_currency > 0 else 0
        total_periods = total_pulls_simulated / pulls_per_period if pulls_per_period > 0 else 0

        # Calculate per-rarity statistics
        detailed_rarity_stats = {}
        
        # PENAMBAHAN: Pastikan semua rarity yang dipilih ada di hasil, bahkan jika 0
        for rarity_level in selected_rarities_for_stats:
            rarity_level_str = str(rarity_level)
            total_obtained_this_rarity = rarity_counts.get(rarity_level_str, 0)
            
            # Perbaiki pembagian dengan nol
            avg_pulls_this_rarity = num_pulls / total_obtained_this_rarity if total_obtained_this_rarity > 0 else 0
            avg_cost_this_rarity = avg_pulls_this_rarity * cost_in_rupiah_for_one_pull
            avg_periods_this_rarity = avg_pulls_this_rarity / pulls_per_period if pulls_per_period > 0 else 0

            rarity_data = {
                'total_obtained': total_obtained_this_rarity,
                'avg_pulls': avg_pulls_this_rarity,
                'avg_cost': avg_cost_this_rarity,
                'avg_periods': avg_periods_this_rarity,
            }

            rarity_config_data = config['rarities'].get(rarity_level_str, {})
            if rarity_config_data.get('rate_up', {}).get('enabled', False):
                total_rate_up_this_rarity = rate_up_counts.get(rarity_level_str, 0)
                
                avg_pulls_rate_up_this_rarity = num_pulls / total_rate_up_this_rarity if total_rate_up_this_rarity > 0 else 0
                avg_cost_rate_up_this_rarity = avg_pulls_rate_up_this_rarity * cost_in_rupiah_for_one_pull
                avg_periods_rate_up_this_rarity = avg_pulls_rate_up_this_rarity / pulls_per_period if pulls_per_period > 0 else 0
                
                rarity_data['rate_up_stats'] = {
                    'total_obtained': total_rate_up_this_rarity,
                    'avg_pulls': avg_pulls_rate_up_this_rarity,
                    'avg_cost': avg_cost_rate_up_this_rarity,
                    'avg_periods': avg_periods_rate_up_this_rarity,
                }
            
            detailed_rarity_stats[rarity_level_str] = rarity_data

        return jsonify({
            'total_pulls_simulated': total_pulls_simulated,
            'rarity_counts': rarity_counts,
            'rate_up_counts': rate_up_counts,
            'selected_rarities_for_stats': selected_rarities_for_stats, 
            'total_gacha_currency_spent': total_gacha_currency,
            'total_real_currency_spent': total_real_currency,
            'total_periods_covered': total_periods,
            'detailed_rarity_stats': detailed_rarity_stats
        })
