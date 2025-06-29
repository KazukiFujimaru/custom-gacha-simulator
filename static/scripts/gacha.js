document.addEventListener('DOMContentLoaded', () => {
    // --- State & Konfigurasi Awal ---
    let playerState = {};
    let gachaConfig = {};

    // --- Elemen DOM ---
    const pull1Btn = document.getElementById('pull-1');
    const pull10Btn = document.getElementById('pull-10');
    const resultsDisplay = document.getElementById('results-display');
    const historyLog = document.getElementById('history-log');
    const notablePullsLog = document.getElementById('notable-pulls-log');
    const sessionStatsContainer = document.getElementById('session-stats-container');
    const configDisplayContainer = document.getElementById('config-display-container');
    const openSettingsBtn = document.getElementById('open-settings-btn');
    const closeSettingsBtn = document.getElementById('close-settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const configForm = document.getElementById('gacha-config-form');
    const rarityContainer = document.getElementById('rarity-settings-container');
    const addRarityBtn = document.getElementById('add-rarity-btn');

    // --- Logika Pengaturan ---
    const rarityTemplate = (rarity, values = {}) => {
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
                            <input type="number" id="soft-pity-increase-${rarity}" value="${values.soft_pity_increase || 0}" min="0" step="0.1" max="100" class="w-full bg-gray-900 border border-gray-700 rounded-md p-2">
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

    function addDynamicListeners() {
        rarityContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-rarity-btn')) {
                e.target.closest('.rarity-config-group').remove();
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
        });
    }
    
    function setupDefaultRarities() {
        rarityContainer.innerHTML = '';
        rarityContainer.insertAdjacentHTML('beforeend', rarityTemplate(5, { 
            rate: 0.6, 
            hard_pity: 90, 
            hard_pity_enabled: true,
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
            hard_pity_enabled: true
        }));
        addDynamicListeners();
    }
    
    addRarityBtn.addEventListener('click', () => {
        const existingRarities = Array.from(rarityContainer.querySelectorAll('.rarity-config-group')).map(el => parseInt(el.dataset.rarity));
        let newRarityLevel = 6;
        while(existingRarities.includes(newRarityLevel)) newRarityLevel++;
        rarityContainer.insertAdjacentHTML('afterbegin', rarityTemplate(newRarityLevel, { rate: 0.1, hard_pity: 100, hard_pity_enabled: true }));
    });

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
        return {
            pity_enabled: document.getElementById('pity-enabled').checked,
            pulls_per_period: parseInt(document.getElementById('pulls-per-period').value) || 1,
            currency: {
                cost_per_pull: parseInt(document.getElementById('cost-per-pull').value) || 1,
                cost_in_rupiah: parseFloat(document.getElementById('cost-in-rupiah').value) || 1,
            },
            rarities
        };
    }

    configForm.addEventListener('submit', (e) => {
        e.preventDefault();
        gachaConfig = readConfigFromUI();
        resetState();
        settingsModal.classList.add('hidden');
    });

    function resetState() {
        playerState = { total_pulls: 0, pity_counters: {}, guaranteed_rate_up: {}, notable_pulls: {} };
        Object.keys(gachaConfig.rarities).forEach(level => {
            playerState.pity_counters[level] = 0;
            playerState.guaranteed_rate_up[level] = false;
            if (parseInt(level) > 3) {
                 playerState.notable_pulls[level] = { regular: [], rate_up: [] };
            }
        });
        updateAllUI();
        resultsDisplay.innerHTML = `<div class="flex items-center justify-center text-gray-500 text-center col-span-full">Konfigurasi baru diterapkan. Siap menarik!</div>`;
        historyLog.innerHTML = '';
    }
    
    function updateAllUI() {
        const costPerPull = BigInt(gachaConfig.currency.cost_per_pull);
        const totalPulls = BigInt(playerState.total_pulls);
        const costInRupiah = gachaConfig.currency.cost_in_rupiah;
        const pullsPerPeriod = gachaConfig.pulls_per_period || 1;
        
        const totalGachaCurrency = totalPulls * costPerPull;
        const rupiahPerGachaCurrency = costPerPull > 0 ? costInRupiah / Number(costPerPull) : 0;
        const totalRealCurrency = Number(totalGachaCurrency) * rupiahPerGachaCurrency;
        const totalPeriods = playerState.total_pulls / pullsPerPeriod;

        let statsHTML = `
            <div class="flex justify-between items-center"><span class="font-semibold text-gray-400">Total Tarikan:</span> <span class="font-bold text-lg text-white">${playerState.total_pulls.toLocaleString('id-ID')}</span></div>
            <div class="flex justify-between items-center"><span class="font-semibold text-gray-400">Total Periode:</span> <span class="font-bold text-lg text-white">${totalPeriods.toFixed(2)}</span></div>
            <div class="flex justify-between items-center"><span class="font-semibold text-gray-400">Mata Uang Gacha:</span> <span class="font-bold text-lg text-yellow-400">${totalGachaCurrency.toLocaleString('id-ID')}</span></div>
            <div class="flex justify-between items-center"><span class="font-semibold text-gray-400">Total Uang (Simulasi):</span> <span class="font-bold text-lg text-white">Rp ${totalRealCurrency.toLocaleString('id-ID', {maximumFractionDigits: 0})}</span></div>
        `;
        
        if (gachaConfig.pity_enabled) {
            statsHTML += `<div class="space-y-3 border-t border-gray-700 pt-3 mt-3">`;
            Object.keys(playerState.pity_counters).sort((a, b) => b-a).forEach(level => {
                if (gachaConfig.rarities[level]?.hard_pity > 0) {
                    const isGuaranteed = playerState.guaranteed_rate_up[level] || false;
                    const rateUpConfig = gachaConfig.rarities[level].rate_up;
                    statsHTML += `<div class="flex justify-between items-center">
                        <span class="font-semibold text-gray-400">Pity ★${level}:</span>
                        <div class="flex items-center space-x-2">
                            ${rateUpConfig.enabled && rateUpConfig.guarantee_enabled ? `<span class="font-bold text-xs ${isGuaranteed ? 'text-green-400' : 'text-red-500'}">${isGuaranteed ? 'Jaminan' : '50/50'}</span>` : ''}
                            <span class="font-bold text-lg text-cyan-400">${playerState.pity_counters[level]}</span>
                        </div>
                    </div>`;
                }
            });
            statsHTML += `</div>`;
        }
        sessionStatsContainer.innerHTML = statsHTML;

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
        configDisplayContainer.innerHTML = configHTML;

        let notableHTML = '';
        Object.keys(playerState.notable_pulls).sort((a,b) => b-a).forEach(level => {
            const pulls = playerState.notable_pulls[level];
            if (pulls.regular.length > 0 || pulls.rate_up.length > 0) {
                notableHTML += `<div class="text-sm mb-3">
                    <div class="font-bold text-yellow-300">★${level} (Total: ${pulls.regular.length + pulls.rate_up.length})</div>`;
                if(pulls.rate_up.length > 0) {
                    notableHTML += `<div class="text-xs text-green-400 mt-1"><strong>Rate Up:</strong> ${pulls.rate_up.join(', ')}</div>`;
                }
                if(pulls.regular.length > 0) {
                    notableHTML += `<div class="text-xs text-gray-400 mt-1"><strong>Biasa:</strong> ${pulls.regular.join(', ')}</div>`;
                }
                notableHTML += `</div>`;
            }
        });
        notablePullsLog.innerHTML = notableHTML || `<div class="text-gray-500">Belum ada hasil tercatat.</div>`;
    }

    function displayResults(results) {
        resultsDisplay.innerHTML = '';
        results.forEach(item => {
            const card = document.createElement('div');
            card.className = `result-card new-item rarity-${item.rarity} p-4 rounded-lg border-2 shadow-lg flex flex-col items-center justify-center text-center font-semibold`;
            card.innerHTML = `<div class="text-lg">${'★'.repeat(item.rarity)}</div><div class="text-xs mt-1">${item.name}</div>`;
            resultsDisplay.appendChild(card);
        });
    }

    function addToHistory(results, startPullCount) {
        results.forEach((item, index) => {
            const pullNumber = startPullCount + index + 1;
            const logEntry = document.createElement('div');
            logEntry.className = `p-2 mb-2 rounded-md text-sm rarity-${item.rarity} border-l-4`;
            logEntry.textContent = `#${pullNumber}: Anda mendapatkan [${'★'.repeat(item.rarity)}] ${item.name}`;
            historyLog.prepend(logEntry);
        });
    }
    
    async function performPull(count) {
        if (!gachaConfig.rarities) { alert("Harap simpan pengaturan terlebih dahulu!"); return; }
        
        pull1Btn.disabled = true; pull10Btn.disabled = true;
        pull1Btn.classList.add('opacity-50', 'cursor-not-allowed');
        pull10Btn.classList.add('opacity-50', 'cursor-not-allowed');

        const startPullCount = playerState.total_pulls;

        try {
            const stateToSend = {
                total_pulls: playerState.total_pulls,
                pity_counters: playerState.pity_counters,
                guaranteed_rate_up: playerState.guaranteed_rate_up
            };
            const response = await fetch('/pull', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ count, state: stateToSend, config: gachaConfig }),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({error: 'Gagal berkomunikasi dengan server.'}));
                throw new Error(errorData.error || 'Terjadi kesalahan pada server.');
            }
            const data = await response.json();
            
            playerState.total_pulls = data.final_state.total_pulls;
            playerState.pity_counters = data.final_state.pity_counters;
            playerState.guaranteed_rate_up = data.final_state.guaranteed_rate_up;

            data.results.forEach((item, index) => {
                const pullNumber = startPullCount + index + 1;
                if (item.rarity > 3) {
                    const category = item.is_rate_up ? 'rate_up' : 'regular';
                    if (!playerState.notable_pulls[item.rarity]) {
                        playerState.notable_pulls[item.rarity] = { regular: [], rate_up: [] };
                    }
                    playerState.notable_pulls[item.rarity][category].push(pullNumber);
                }
            });

            displayResults(data.results);
            addToHistory(data.results, startPullCount);
            updateAllUI();
        } catch (error) {
            console.error('Error:', error);
            resultsDisplay.innerHTML = `<div class="text-red-500 col-span-full text-center p-4">${error.message}</div>`;
        } finally {
            pull1Btn.disabled = false; pull10Btn.disabled = false;
            pull1Btn.classList.remove('opacity-50', 'cursor-not-allowed');
            pull10Btn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    }

    // --- Inisialisasi ---
    openSettingsBtn.addEventListener('click', () => settingsModal.classList.remove('hidden'));
    closeSettingsBtn.addEventListener('click', () => settingsModal.classList.add('hidden'));
    setupDefaultRarities();
    configForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    pull1Btn.addEventListener('click', () => performPull(1));
    pull10Btn.addEventListener('click', () => performPull(10));
});
