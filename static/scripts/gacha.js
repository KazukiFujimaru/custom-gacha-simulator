// State management di sisi klien
let state = {
    pity_5_star: 0,
    pity_4_star: 0,
    is_guaranteed_rate_up: false,
    total_pulls: 0
};

const CURRENCY_PER_PULL = 160;
const PULL_COST_IDR = 320; // Asumsi Rp 320 per 160 currency

// Elemen DOM
const pull1Btn = document.getElementById('pull-1');
const pull10Btn = document.getElementById('pull-10');
const resultsDisplay = document.getElementById('results-display');
const historyLog = document.getElementById('history-log');
const totalPullsEl = document.getElementById('total-pulls');
const totalSpentEl = document.getElementById('total-spent');
const pity5El = document.getElementById('pity-5');
const pity4El = document.getElementById('pity-4');
const guaranteedStatusEl = document.getElementById('guaranteed-status');

// Fungsi untuk memperbarui UI statistik
function updateStatsUI() {
    totalPullsEl.textContent = state.total_pulls;
    totalSpentEl.textContent = `Rp ${(state.total_pulls * PULL_COST_IDR).toLocaleString('id-ID')}`;
    pity5El.textContent = state.pity_5_star;
    pity4El.textContent = state.pity_4_star;
    if (state.is_guaranteed_rate_up) {
        guaranteedStatusEl.textContent = 'AKTIF';
        guaranteedStatusEl.className = 'font-bold text-lg text-green-400';
    } else {
        guaranteedStatusEl.textContent = 'TIDAK AKTIF';
         guaranteedStatusEl.className = 'font-bold text-lg text-red-500';
    }
}

// Fungsi untuk menampilkan hasil di UI
function displayResults(results) {
    resultsDisplay.innerHTML = ''; // Hapus hasil sebelumnya
    results.forEach(item => {
        const card = document.createElement('div');
        card.className = `result-card new-item rarity-${item.rarity} p-4 rounded-lg border-2 shadow-lg flex flex-col items-center justify-center text-center font-semibold`;
        card.innerHTML = `<div class="text-lg">${'★'.repeat(item.rarity)}</div><div class="text-xs mt-1">${item.name}</div>`;
        resultsDisplay.appendChild(card);
    });
}

// Fungsi untuk menambahkan entri ke riwayat
function addToHistory(results) {
    results.forEach(item => {
        const logEntry = document.createElement('div');
        logEntry.className = `p-2 mb-2 rounded-md text-sm rarity-${item.rarity} border-l-4`;
        logEntry.textContent = `#${state.total_pulls - (results.length - 1) + Array.from(historyLog.children).length}: Anda mendapatkan [${'★'.repeat(item.rarity)}] ${item.name}`;
        // Tambahkan di awal
        historyLog.prepend(logEntry);
    });
}

// Fungsi untuk melakukan tarikan
async function performPull(count) {
    // Nonaktifkan tombol selama proses
    pull1Btn.disabled = true;
    pull10Btn.disabled = true;
    pull1Btn.classList.add('opacity-50');
    pull10Btn.classList.add('opacity-50');

    try {
        const response = await fetch('/pull', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                count: count,
                state: state
            }),
        });

        if (!response.ok) {
            throw new Error('Gagal berkomunikasi dengan server.');
        }

        const data = await response.json();
        
        // Update state dengan data baru dari server
        state = data.final_state;

        displayResults(data.results);
        addToHistory(data.results.slice().reverse()); // Balik agar urutan di log benar
        updateStatsUI();

    } catch (error) {
        console.error('Error:', error);
        resultsDisplay.innerHTML = `<div class="text-red-500 col-span-full">${error.message}</div>`;
    } finally {
        // Aktifkan kembali tombol
        pull1Btn.disabled = false;
        pull10Btn.disabled = false;
        pull1Btn.classList.remove('opacity-50');
        pull10Btn.classList.remove('opacity-50');
    }
}

// Tambahkan event listener ke tombol
pull1Btn.addEventListener('click', () => performPull(1));
pull10Btn.addEventListener('click', () => performPull(10));

// Inisialisasi UI saat halaman dimuat
updateStatsUI();