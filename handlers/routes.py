from flask import Blueprint, render_template, jsonify, request
from modules.gacha_logic import perform_multiple_pulls, GACHA_CONFIG

app = Blueprint('gacha', __name__)

def configure_routes(app):
    @app.route('/')
    def index():
        """Menyajikan halaman utama (HTML, CSS, JS)."""
        return render_template('index.html', GACHA_CONFIG=GACHA_CONFIG)

    @app.route('/pull', methods=['POST'])
    def pull():
        """
        Endpoint API yang dipanggil oleh JavaScript saat pengguna menekan tombol tarikan.
        """
        data = request.json
        pull_count = data.get('count', 1)
        current_state = data.get('state')
        
        results, final_state = perform_multiple_pulls(current_state, pull_count)
        
        # Kirim kembali hasil dan state akhir ke klien dalam format JSON
        return jsonify({
            'results': results,
            'final_state': final_state
        })