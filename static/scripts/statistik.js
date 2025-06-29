document.addEventListener('DOMContentLoaded', () => {
    let gachaConfig = {};
    let chartInstance = null;

    const runSimulationBtn = document.getElementById('run-simulation-btn');
    const numSimulationsInput = document.getElementById('num-simulations');
    const statisticsDisplay = document.getElementById('statistics-display');
    const rarityDistributionChart = document.getElementById('rarity-distribution-chart');
    const configDisplayContainer = document.getElementById('config-display-container');
    const openSettingsBtn = document.getElementById('open-settings-btn');
    const closeSettingsBtn = document.getElementById('close-settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const configForm = document.getElementById('gacha-config-form');
    const rarityContainer = document.getElementById('rarity-settings-container');
    const addRarityBtn = document.getElementById('add-rarity-btn');
    const selectedRaritiesForStatsContainer = document.getElementById('selected-rarities-for-stats-container');

    // MODIFIKASI 1: Memperbarui template untuk menyertakan checkbox "Aktifkan Hard Pity"
    const rarityTemplate = (rarity, values = {}) => {
        // Menentukan nilai default jika tidak ada, hard pity defaultnya aktif
        const hardPityEnabled = values.hard_pity_enabled !== false;
        const softPityEnabled = values.soft_pity_enabled === true;
        const rateUpEnabled = values.rate_up_enabled === true;

        return `
        <fieldset class="border border-gray-700 p-4 rounded-lg rarity-config-group" data-rarity="${rarity}">
            <legend class="px-2 font-semibold text-lg text-yellow-400 flex justify-between items-center w-full">
                <span>Pengaturan Bintang ★${rarity}</span>
                <button type="button" class="remove-rarity-btn text-red-500 hover:text-red-400 text-2xl font-bold leading-none">&times;</button>
            </legend>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                <div>
                    <label for="rate-${rarity}" class="mb-1 block font-medium text-gray-300">Rate Dasar (%)</label>
                    <input type="number" id="rate-${rarity}" value="${values.rate || 0}" step="0.1" min="0" max="100" class="w-full bg-gray-900 border border-gray-700 rounded-md p-2">
                </div>
                
                <div class="space-y-2">
                    <div class="flex items-center justify-between">
                        <label for="hard-pity-enabled-${rarity}" class="font-medium text-gray-300">Aktifkan Hard Pity</label>
                        <input type="checkbox" id="hard-pity-enabled-${rarity}" data-rarity="${rarity}" class="options-toggle h-6 w-6 rounded text-indigo-500 bg-gray-700" ${hardPityEnabled ? 'checked' : ''}>
                    </div>
                    <div id="hard-pity-options-${rarity}" class="options-group ${hardPityEnabled ? 'visible' : ''}">
                        <label for="hard-pity-${rarity}" class="mb-1 block font-medium text-gray-300 sr-only">Hard Pity</label>
                        <input type="number" id="hard-pity-${rarity}" value="${values.hard_pity || 0}" min="0" class="w-full bg-gray-900 border border-gray-700 rounded-md p-2" ${!hardPityEnabled ? 'disabled' : ''}>
                    </div>
                </div>

            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-4">
                <div class="border-t border-gray-600 pt-4 mt-4 space-y-4">
                    <div class="flex items-center justify-between">
                        <label for="soft-pity-enabled-${rarity}" class="font-medium text-gray-300">Aktifkan Soft Pity</label>
                        <input type="checkbox" id="soft-pity-enabled-${rarity}" data-rarity="${rarity}" class="options-toggle h-6 w-6 rounded text-indigo-500 bg-gray-700" ${softPityEnabled ? 'checked' : ''}>
                    </div>
                    <div id="soft-pity-options-${rarity}" class="options-group grid grid-cols-1 gap-4 ${softPityEnabled ? 'visible' : ''}">
                        <div>
                            <label for="soft-pity-start-${rarity}" class="mb-1 block font-medium text-gray-300">Mulai di Tarikan ke-</label>
                            <input type="number" id="soft-pity-start-${rarity}" value="${values.soft_pity_start || 0}" min="0" class="w-full bg-gray-900 border border-gray-700 rounded-md p-2">
                        </div>
                        <div>
                            <label for="soft-pity-increase-${rarity}" class="mb-1 block font-medium text-gray-300">Kenaikan Rate (%)</label>
                            <input type="number" id="soft-pity-increase-${rarity}" value="${values.soft_pity_increase || 0}" min="0" max="100" step="0.1" class="w-full bg-gray-900 border border-gray-700 rounded-md p-2">
                        </div>
                    </div>
                </div>
                <div class="border-t border-gray-600 pt-4 mt-4 space-y-4">
                    <div class="flex items-center justify-between">
                        <label for="rate-up-enabled-${rarity}" class="font-medium text-gray-300">Aktifkan Rate Up</label>
                        <input type="checkbox" id="rate-up-enabled-${rarity}" data-rarity="${rarity}" class="options-toggle h-6 w-6 rounded text-indigo-500 bg-gray-700" ${rateUpEnabled ? 'checked' : ''}>
                    </div>
                    <div id="rate-up-options-${rarity}" class="options-group grid grid-cols-1 gap-4 ${rateUpEnabled ? 'visible' : ''}">
                        <div>
                            <label for="rate-up-chance-${rarity}" class="mb-1 block font-medium text-gray-300">Peluang Rate Up (%)</label>
                            <input type="number" id="rate-up-chance-${rarity}" value="${values.rate_up_chance || 50}" min="0" max="100" class="w-full bg-gray-900 border border-gray-700 rounded-md p-2">
                        </div>
                        <div class="flex items-center justify-between p-2 rounded-md bg-gray-900/50">
                           <label for="guarantee-enabled-${rarity}" class="font-medium text-gray-300">Jaminan Rate Up</label>
                           <input type="checkbox" id="guarantee-enabled-${rarity}" class="h-6 w-6 rounded text-indigo-500 bg-gray-700" ${values.guarantee_enabled ? 'checked' : ''}>
                        </div>
                    </div>
                </div>
            </div>
        </fieldset>
    `;
    }

    // MODIFIKASI 2: Menambahkan listener untuk checkbox hard pity
    function addDynamicListeners() {
        rarityContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-rarity-btn')) {
                e.target.closest('.rarity-config-group').remove();
                populateSelectedRaritiesCheckboxes(gachaConfig.selected_rarities_for_stats); 
            }
        });
        rarityContainer.addEventListener('change', (e) => {
            if (e.target.classList.contains('options-toggle')) {
                const rarity = e.target.dataset.rarity;
                let optionsDiv;
                let inputElement;

                if (e.target.id.includes('hard-pity-enabled')) {
                    optionsDiv = document.getElementById(`hard-pity-options-${rarity}`);
                    inputElement = document.getElementById(`hard-pity-${rarity}`);
                    if (inputElement) {
                        inputElement.disabled = !e.target.checked;
                    }
                } else if (e.target.id.includes('soft-pity-enabled')) {
                    optionsDiv = document.getElementById(`soft-pity-options-${rarity}`);
                } else if (e.target.id.includes('rate-up-enabled')) {
                    optionsDiv = document.getElementById(`rate-up-options-${rarity}`);
                }
                
                if (optionsDiv) {
                    optionsDiv.classList.toggle('visible', e.target.checked);
                }
            }
            populateSelectedRaritiesCheckboxes(gachaConfig.selected_rarities_for_stats); 
        });
    }
    
    function populateSelectedRaritiesCheckboxes(currentlySelectedRarities = [5]) {
        selectedRaritiesForStatsContainer.innerHTML = '';
        const existingRarities = Array.from(rarityContainer.querySelectorAll('.rarity-config-group'))
                                    .map(el => parseInt(el.dataset.rarity))
                                    .sort((a,b) => b-a);

        existingRarities.forEach(rarity => {
            const isChecked = currentlySelectedRarities.includes(rarity);
            const checkboxHtml = `
                <div class="flex items-center p-2 rounded-md bg-gray-900/50">
                    <input type="checkbox" id="stat-rarity-${rarity}" value="${rarity}" class="stat-rarity-checkbox h-5 w-5 rounded text-blue-500 bg-gray-700 border-gray-600 focus:ring-blue-600" ${isChecked ? 'checked' : ''}>
                    <label for="stat-rarity-${rarity}" class="ml-2 font-medium text-gray-300">★${rarity}</label>
                </div>
            `;
            selectedRaritiesForStatsContainer.insertAdjacentHTML('beforeend', checkboxHtml);
        });
    }

    // MODIFIKASI 4: Menyesuaikan data default agar sesuai struktur baru
    function setupDefaultRarities() {
        rarityContainer.innerHTML = '';
        rarityContainer.insertAdjacentHTML('beforeend', rarityTemplate(5, { 
            rate: 0.6, 
            hard_pity: 90, 
            hard_pity_enabled: true, // Ditambahkan
            soft_pity_enabled: true, 
            soft_pity_start: 74, 
            soft_pity_increase: 6, 
            rate_up_enabled: true, 
            rate_up_chance: 50, 
            guarantee_enabled: true 
        }));
        rarityContainer.insertAdjacentHTML('beforeend', rarityTemplate(4, { 
            rate: 5.1, 
            hard_pity: 10,
            hard_pity_enabled: true // Ditambahkan
        }));
        addDynamicListeners();
    }
    
    addRarityBtn.addEventListener('click', () => {
        const existingRarities = Array.from(rarityContainer.querySelectorAll('.rarity-config-group')).map(el => parseInt(el.dataset.rarity));
        let newRarityLevel = 6;
        while(existingRarities.includes(newRarityLevel)) newRarityLevel++;
        rarityContainer.insertAdjacentHTML('afterbegin', rarityTemplate(newRarityLevel, { rate: 0.1, hard_pity: 100, hard_pity_enabled: true }));
        populateSelectedRaritiesCheckboxes(gachaConfig.selected_rarities_for_stats); 
    });

    // MODIFIKASI 3: Membaca status checkbox hard pity saat menyimpan konfigurasi
    function readConfigFromUI() {
        const rarities = {};
        rarityContainer.querySelectorAll('.rarity-config-group').forEach(group => {
            const level = group.dataset.rarity;
            
            const hardPityEnabled = document.getElementById(`hard-pity-enabled-${level}`).checked;
            const softPityEnabled = document.getElementById(`soft-pity-enabled-${level}`).checked;
            const rateUpEnabled = document.getElementById(`rate-up-enabled-${level}`).checked;

            rarities[level] = {
                rate: parseFloat(document.getElementById(`rate-${level}`).value) / 100,
                hard_pity: hardPityEnabled ? parseInt(document.getElementById(`hard-pity-${level}`).value) : 0,
                soft_pity: {
                    enabled: softPityEnabled,
                    start: softPityEnabled ? parseInt(document.getElementById(`soft-pity-start-${level}`).value) : 0,
                    increase: softPityEnabled ? parseFloat(document.getElementById(`soft-pity-increase-${level}`).value) / 100 : 0,
                },
                rate_up: {
                    enabled: rateUpEnabled,
                    chance: rateUpEnabled ? parseFloat(document.getElementById(`rate-up-chance-${level}`).value) / 100 : 0.5,
                    guarantee_enabled: rateUpEnabled ? document.getElementById(`guarantee-enabled-${level}`).checked : false,
                }
            };
        });

        const selectedRarities = Array.from(document.querySelectorAll('.stat-rarity-checkbox:checked'))
                                    .map(checkbox => parseInt(checkbox.value));

        return {
            pity_enabled: document.getElementById('pity-enabled').checked,
            pulls_per_period: parseInt(document.getElementById('pulls-per-period').value) || 1,
            selected_rarities_for_stats: selectedRarities.length > 0 ? selectedRarities : [5],
            currency: {
                cost_per_pull: parseInt(document.getElementById('cost-per-pull').value) || 1,
                cost_in_rupiah: parseFloat(document.getElementById('cost-in-rupiah').value) || 1
            },
            rarities
        };
    }

    configForm.addEventListener('submit', (e) => {
        e.preventDefault();
        gachaConfig = readConfigFromUI();
        updateConfigDisplay();
        settingsModal.classList.add('hidden');
    });

    function updateConfigDisplay() {
        let configHTML = '';
        Object.keys(gachaConfig.rarities).sort((a,b) => b-a).forEach(level => {
             const config = gachaConfig.rarities[level];
             let softPityText = 'N/A';
             if (gachaConfig.pity_enabled && config.soft_pity.enabled && config.soft_pity.start > 0) {
                 softPityText = `Mulai di ${config.soft_pity.start} (+${(config.soft_pity.increase * 100).toFixed(1)}%/pull)`;
             }
             configHTML += `<div class="border-t border-gray-700 mt-2 pt-2">
                    <div class="flex justify-between font-bold text-yellow-300"><span>★${level}</span></div>
                    <div class="flex justify-between"><span>Rate Dasar:</span> <span>${(config.rate * 100).toFixed(2)}%</span></div>
                    <div class="flex justify-between"><span>Hard Pity:</span> <span>${gachaConfig.pity_enabled && config.hard_pity > 0 ? config.hard_pity : 'N/A'}</span></div>
                    <div class="flex justify-between"><span>Soft Pity:</span> <span class="text-right">${softPityText}</span></div>
                </div>`;
        });
        const displayedRarities = gachaConfig.selected_rarities_for_stats.length > 0 ? 
                                   gachaConfig.selected_rarities_for_stats.sort((a,b) => b-a).map(r => `★${r}`).join(', ') :
                                   'Tidak ada (Default: ★5)';
        configHTML += `<div class="border-t border-gray-700 mt-2 pt-2">
                            <div class="flex justify-between font-bold text-blue-300"><span>Statistik Rate Up untuk:</span></div>
                            <span>${displayedRarities}</span>
                        </div>`;
        configDisplayContainer.innerHTML = configHTML;
    }

    async function runSimulation() {
        if (!gachaConfig.rarities || Object.keys(gachaConfig.rarities).length === 0) {
            alert("Harap simpan pengaturan gacha terlebih dahulu!");
            return;
        }
        if (gachaConfig.selected_rarities_for_stats.length === 0) {
            alert("Harap pilih setidaknya satu rarity untuk ditampilkan statistiknya!");
            return;
        }

        runSimulationBtn.disabled = true;
        runSimulationBtn.classList.add('opacity-50', 'cursor-not-allowed');
        statisticsDisplay.innerHTML = `<div class="text-center text-gray-400">Menjalankan simulasi... Ini mungkin memakan waktu beberapa saat untuk ${numSimulationsInput.value.toLocaleString('id-ID')} tarikan.</div>`;
        rarityDistributionChart.innerHTML = `<div class="text-center text-gray-400">Mempersiapkan grafik...</div>`;

        try {
            const numPulls = parseInt(numSimulationsInput.value);
            // PERBAIKAN: Menghapus trailing comma dari objek fetch
            const response = await fetch('/api/run_statistics', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    num_pulls: numPulls, 
                    config: gachaConfig, 
                    selected_rarities_for_stats: gachaConfig.selected_rarities_for_stats 
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({error: 'Gagal berkomunikasi dengan server.'}));
                throw new Error(errorData.error || 'Terjadi kesalahan pada server.');
            }

            const data = await response.json();
            displayStatistics(data);
            drawChart(data);

        } catch (error) {
            console.error('Error running simulation:', error);
            statisticsDisplay.innerHTML = `<div class="text-red-500 text-center p-4">Error: ${error.message}</div>`;
            rarityDistributionChart.innerHTML = `<div class="text-red-500 text-center p-4">Gagal membuat grafik.</div>`;
        } finally {
            runSimulationBtn.disabled = false;
            runSimulationBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    function displayStatistics(data) {
        let statsHTML = `
            <h3 class="text-xl font-bold text-white mb-4">Ringkasan Simulasi (${data.total_pulls_simulated.toLocaleString('id-ID')} Tarikan)</h3>
            <div class="space-y-2 text-md mb-6 border-b-2 border-gray-700 pb-4">
                <div class="flex justify-between"><span>Total Mata Uang Gacha Dihabiskan:</span> <span class="font-semibold text-yellow-400">${data.total_gacha_currency_spent.toLocaleString('id-ID')}</span></div>
                <div class="flex justify-between"><span>Estimasi Total Rupiah Dihabiskan:</span> <span class="font-semibold text-green-400">Rp ${data.total_real_currency_spent.toLocaleString('id-ID', {maximumFractionDigits: 0})}</span></div>
                <div class="flex justify-between"><span>Total Periode Tercover:</span> <span class="font-semibold">${data.total_periods_covered.toFixed(2)}</span></div>
            </div>
            <h3 class="text-xl font-bold text-white mb-4">Statistik Detail per Rarity</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2   gap-6">
        `;
        
        const sortedSelectedRarities = data.selected_rarities_for_stats.sort((a, b) => b - a);
        
        if (sortedSelectedRarities.length === 0) {
            statsHTML += `<p class="text-gray-500 text-center col-span-full">Tidak ada rarity yang dipilih untuk statistik detail.</p>`;
        } else {
            sortedSelectedRarities.forEach(rarityLevel => {
                const rarityData = data.detailed_rarity_stats[rarityLevel];
                if (rarityData) {
                    statsHTML += `
                        <div class="bg-gray-700 p-4 rounded-lg shadow-md border-l-4 rarity-${rarityLevel}-border rarity-stat-card"> <h4 class="text-lg font-bold text-yellow-300 mb-3 border-b border-gray-600 pb-2">Statistik ★${rarityLevel}</h4>
                            <div class="flex-grow space-y-1 text-sm">
                                <div class="flex justify-between"><span>Total Diperoleh:</span> <span class="font-semibold">${rarityData.total_obtained.toLocaleString('id-ID')}</span></div>
                                <div class="flex justify-between"><span>Rata-rata Tarikan per ★${rarityLevel}:</span> <span class="font-semibold">${rarityData.avg_pulls.toFixed(2)}</span></div>
                                <div class="flex justify-between"><span>Rata-rata Biaya (Rupiah) per ★${rarityLevel}:</span> <span class="font-semibold">Rp ${rarityData.avg_cost.toLocaleString('id-ID', {maximumFractionDigits: 0})}</span></div>
                                <div class="flex justify-between"><span>Rata-rata Periode per ★${rarityLevel}:</span> <span class="font-semibold">${rarityData.avg_periods.toFixed(2)}</span></div>
                            </div>
                    `;

                    if (rarityData.rate_up_stats) {
                        const rateUpStats = rarityData.rate_up_stats;
                        statsHTML += `
                            <div class="border-t border-gray-600 pt-3 mt-3">
                                <h5 class="font-bold text-green-400 mb-2">Statistik Rate Up ★${rarityLevel}</h5>
                                <div class="space-y-1 text-sm">
                                    <div class="flex justify-between"><span>Jumlah Rate Up Diperoleh:</span> <span class="font-semibold">${rateUpStats.total_obtained.toLocaleString('id-ID')}</span></div>
                                    <div class="flex justify-between"><span>Rata-rata Tarikan per Rate Up:</span> <span class="font-semibold">${rateUpStats.avg_pulls.toFixed(2)}</span></div>
                                    <div class="flex justify-between"><span>Rata-rata Biaya (Rupiah) per Rate Up:</span> <span class="font-semibold">Rp ${rateUpStats.avg_cost.toLocaleString('id-ID', {maximumFractionDigits: 0})}</span></div>
                                    <div class="flex justify-between"><span>Rata-rata Periode per Rate Up:</span> <span class="font-semibold">${rateUpStats.avg_periods.toFixed(2)}</span></div>
                                </div>
                            </div>
                        `;
                    }
                    statsHTML += `</div>`;
                }
            });
        }
        statsHTML += `</div>`; // Tutup grid container
        statisticsDisplay.innerHTML = statsHTML;
    }

    function drawChart(data) {
        rarityDistributionChart.innerHTML = '<canvas id="rarityChart"></canvas>';
        const ctx = document.getElementById('rarityChart').getContext('2d');

        if (chartInstance) {
            chartInstance.destroy();
        }
        
        const sortedRarities = Object.keys(data.rarity_counts).sort((a, b) => b - a);
        const labels = sortedRarities.map(r => `★${r}`);
        const values = sortedRarities.map(r => data.rarity_counts[r]);
        const backgroundColors = sortedRarities.map(r => {
            switch(r) {
                case '6': return '#ff8a78';
                case '5': return '#f8b500';
                case '4': return '#a36eff';
                case '3': return '#60a5fa';
                default: return '#cccccc';
            }
        });

        chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Jumlah Diperoleh',
                    data: values,
                    backgroundColor: backgroundColors,
                    borderColor: backgroundColors.map(color => color.replace('rgb', 'rgba').replace(')', ', 1)')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: `Distribusi Hasil Gacha dari ${data.total_pulls_simulated.toLocaleString('id-ID')} Tarikan`,
                        color: '#e2e8f0',
                        font: { size: 18 }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toLocaleString('id-ID');
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Rarity',
                            color: '#cbd5e1'
                        },
                        ticks: { color: '#cbd5e1' },
                        grid: { color: '#4b5563' }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Jumlah Diperoleh',
                            color: '#cbd5e1'
                        },
                        ticks: {
                            color: '#cbd5e1',
                            callback: function(value) {
                                return value.toLocaleString('id-ID');
                            }
                        },
                        grid: { color: '#4b5563' }
                    }
                }
            }
        });
    }

    // --- Inisialisasi ---
    openSettingsBtn.addEventListener('click', () => {
        settingsModal.classList.remove('hidden');
        populateSelectedRaritiesCheckboxes(gachaConfig.selected_rarities_for_stats); 
    });
    closeSettingsBtn.addEventListener('click', () => settingsModal.classList.add('hidden'));
    runSimulationBtn.addEventListener('click', runSimulation);

    // Initial setup (urutan panggilan di sini sangat penting)
    setupDefaultRarities(); 
    setTimeout(() => {
        gachaConfig = readConfigFromUI(); 
        populateSelectedRaritiesCheckboxes(gachaConfig.selected_rarities_for_stats); 
        configForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }, 100); 
});
