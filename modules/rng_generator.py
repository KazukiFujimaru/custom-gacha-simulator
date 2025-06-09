import os
import hashlib
from datetime import datetime
from numpy.random import Generator, PCG64  # Memperbaiki import PCG64

def create_seed():
    """
    Membuat seed yang sangat acak dengan menggabungkan timestamp presisi tinggi
    dan byte acak dari sistem operasi.
    """
    # 1. Dapatkan timestamp saat ini dengan presisi mikrodetik.
    time_seed = str(datetime.now().timestamp()).encode('utf-8')
    
    # 2. Dapatkan byte acak dari sumber entropi OS (sangat aman).
    os_seed = os.urandom(32)
    
    # 3. Gabungkan keduanya dan hash menggunakan SHA-256 untuk menghasilkan seed akhir.
    combined_seed = time_seed + os_seed
    hashed_seed = hashlib.sha256(combined_seed).digest()
    
    # 4. Konversi hash menjadi integer untuk digunakan oleh PCG64.
    seed_int1 = int.from_bytes(hashed_seed[:8], 'big')
    seed_int2 = int.from_bytes(hashed_seed[8:16], 'big')

    return (seed_int1, seed_int2)

# Inisialisasi generator PCG64 dengan seed yang kuat.
seed = create_seed()
bitgen = PCG64(seed)
rng = Generator(bitgen)

print(seed)
print(PCG64(seed))
print(Generator(bitgen))
print(bitgen.state)  # prints the internal state dictionary of PCG64
print(rng.integers(0, 10))