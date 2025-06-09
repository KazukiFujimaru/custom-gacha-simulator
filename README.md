# Flask Gacha Simulator

Simulator gacha game yang dibuat dengan Flask, menggunakan algoritma PCG (Permuted Congruential Generator) untuk menghasilkan angka acak berkualitas tinggi.

## Fitur

- Simulasi sistem gacha dengan mekanisme pity
- Soft pity dan hard pity untuk bintang 5
- Rate up system dengan jaminan 50/50
- Interface web yang responsif dengan Tailwind CSS
- RNG berkualitas tinggi menggunakan PCG algorithm

## Instalasi

1. Clone repository ini
2. Buat virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # atau
   venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan aplikasi:
   ```bash
   python app.py
   ```
5. Buka browser dan kunjungi `http://127.0.0.1:5000`

## Struktur Project

- `app.py` - Main Flask application
- `handlers/` - Blueprint handlers untuk routing
- `modules/` - Business logic dan utility functions
- `static/` - Static files (CSS, JS, images)
- `templates/` - HTML templates
- `tests/` - Unit tests

## Deployment ke Vercel

Project ini sudah dikonfigurasi untuk deployment ke Vercel. Cukup push ke repository yang terhubung dengan Vercel.

## Testing

Jalankan unit tests:
```bash
python -m pytest tests/
```

## License

MIT License
```

---
