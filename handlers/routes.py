from flask import Blueprint, render_template, jsonify, request
from modules import gacha_logic, rng_generator

app = Blueprint('gacha', __name__)

def configure_routes(app):
    @app.route('/')
    def index():
        """Menyajikan halaman utama."""
        return render_template('index.html')

    @app.route('/pull', methods=['POST'])
    def pull():
        """Endpoint API untuk melakukan tarikan gacha."""
        data = request.json
        pull_count = data.get('count', 1)
        current_state = data.get('state')
        config = data.get('config') # <-- Terima konfigurasi dari frontend

        # Validasi sederhana
        if not all([isinstance(pull_count, int), isinstance(current_state, dict), isinstance(config, dict)]):
            return jsonify({'error': 'Invalid request data'}), 400

        results = []
        rng = rng_generator.rng # Ambil instance RNG yang sudah diinisialisasi

        for _ in range(pull_count):
            # Jalankan satu tarikan dengan state dan config yang diperbarui
            result, new_state = gacha_logic.perform_one_pull(current_state, config, rng)
            current_state = new_state
            current_state['total_pulls'] += 1
            results.append(result)

        return jsonify({
            'results': results,
            'final_state': current_state
        })