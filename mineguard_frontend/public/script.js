// script.js (FULL updated file)
// ===============================
// Backend API Configuration
// ===============================
const API_BASE_URL = 'https://mineguard-2p44.onrender.com';

// Default fallback values
const fallbackWeatherData = { temperature: 28, humidity: 60, rainfall: 2, wind_speed: 12 };
const fallbackSensorData = { displacement: 0.0, vibration: 0.0, pore_pressure: 0.0 };
const fallbackRiskPrediction = "Unknown";

// ===============================
// State flags
// ===============================
let vibrationChart = null;
let vibrationData = [];
let timeLabels = [];
let timeCounter = 0;
let vibrationIntervalId = null;
let hasActiveCoords = false; // becomes true once user clicks Predict with valid coords

// ===============================
// Init
// ===============================
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    setupEventListeners();
    animateCards();

    // Initialize chart (empty) so the canvas is ready; we won't start updates
    initializeVibrationChart(empty = true);

    // Ensure initial UI shows zeros (Option A)
    showZeroState();
});

// ===============================
// Helpers
// ===============================
function isCoordsValid(lat, lon) {
    // Accept non-empty numeric values not equal to 0 (as per Option A)
    if (lat === "" || lon === "" || lat === null || lon === null) return false;
    const nLat = Number(lat);
    const nLon = Number(lon);
    if (Number.isNaN(nLat) || Number.isNaN(nLon)) return false;
    // treat lat/lon that are exactly 0 as invalid for this app
    if (nLat === 0 && nLon === 0) return false;
    // latitude range and longitude range sanity check
    if (nLat < -90 || nLat > 90) return false;
    if (nLon < -180 || nLon > 180) return false;
    return true;
}

function showZeroState() {
    // Display zeros in the cards when no valid coordinates
    document.getElementById('temperature').textContent = `0°C`;
    document.getElementById('humidity').textContent = `0%`;
    document.getElementById('rainfall').textContent = `0mm`;
    document.getElementById('windSpeed').textContent = `0 km/h`;

    document.getElementById('displacement').textContent = `0.0mm`;
    document.getElementById('vibration').textContent = `0.00 Hz`;
    document.getElementById('porePressure').textContent = `0.0 kPa`;

    updateRiskDisplay('unknown'); // show a neutral state
    clearVibrationChart();
}

// Clear chart data (keep chart object)
function clearVibrationChart() {
    if (!vibrationChart) return;
    timeLabels = [];
    vibrationData = [];
    timeCounter = 0;
    vibrationChart.data.labels = [];
    vibrationChart.data.datasets[0].data = [];
    vibrationChart.update();
}

// Start live updates only after successful predict
function startVibrationPolling() {
    // avoid multiple intervals
    if (vibrationIntervalId !== null) return;

    // fetch immediately then every 5s
    fetchAndUpdateVibration();
    vibrationIntervalId = setInterval(fetchAndUpdateVibration, 5000);
}

function stopVibrationPolling() {
    if (vibrationIntervalId !== null) {
        clearInterval(vibrationIntervalId);
        vibrationIntervalId = null;
    }
}

// ===============================
// Weather Data
// ===============================
async function loadWeatherData(lat, lon) {
    try {
        const res = await fetch(`${API_BASE_URL}/weather/${lat}/${lon}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        const temp = data.summary?.temperature ?? fallbackWeatherData.temperature;
        const humidity = data.summary?.humidity ?? fallbackWeatherData.humidity;
        const rainfall = data.summary?.rainfall ?? fallbackWeatherData.rainfall;
        const wind = data.summary?.wind_speed ?? fallbackWeatherData.wind_speed;

        document.getElementById('temperature').textContent = `${temp}°C`;
        document.getElementById('humidity').textContent = `${humidity}%`;
        document.getElementById('rainfall').textContent = `${rainfall}mm`;
        document.getElementById('windSpeed').textContent = `${wind} km/h`;

        return data;
    } catch (err) {
        console.error("Weather Error:", err);
        // Use fallback only if user provided coords
        document.getElementById('temperature').textContent = `${fallbackWeatherData.temperature}°C`;
        document.getElementById('humidity').textContent = `${fallbackWeatherData.humidity}%`;
        document.getElementById('rainfall').textContent = `${fallbackWeatherData.rainfall}mm`;
        document.getElementById('windSpeed').textContent = `${fallbackWeatherData.wind_speed} km/h`;
        return null;
    }
}

// ===============================
// Sensor Data
// ===============================
async function loadSensorData() {
    try {
        const res = await fetch(`${API_BASE_URL}/sensors/vibration`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        const disp = (data.displacement !== undefined) ? data.displacement : fallbackSensorData.displacement;
        const vib = (data.vibration !== undefined) ? data.vibration : fallbackSensorData.vibration;
        const pore = (data.pore_pressure !== undefined) ? data.pore_pressure : fallbackSensorData.pore_pressure;

        document.getElementById('displacement').textContent = `${disp}mm`;
        document.getElementById('vibration').textContent = `${Number(vib).toFixed(2)} Hz`;
        document.getElementById('porePressure').textContent = `${pore} kPa`;
        return data;
    } catch (err) {
        console.error("Sensor Error:", err);
        // Use fallback values
        document.getElementById('displacement').textContent = `${fallbackSensorData.displacement}mm`;
        document.getElementById('vibration').textContent = `${fallbackSensorData.vibration.toFixed(2)} Hz`;
        document.getElementById('porePressure').textContent = `${fallbackSensorData.pore_pressure} kPa`;
        return null;
    }
}

// ===============================
// Risk Prediction
// ===============================
async function loadRiskPrediction(lat, lon) {
    try {
        const res = await fetch(`${API_BASE_URL}/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lat, lon })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        let riskValue =
            data.prediction?.risk ||
            data.prediction?.risk_level ||
            data.risk ||
            data.risk_level ||
            fallbackRiskPrediction;

        // unify to string
        riskValue = String(riskValue).toLowerCase();

        updateRiskDisplay(riskValue);

        // show web alert once if high
        if (riskValue.includes('high')) {
            showWebAlert(data.alert || "⚠️ HIGH RISK of Rockfall detected!", "high");
        } else if (riskValue.includes('medium') || riskValue.includes('moderate')) {
            showWebAlert(data.alert || "⚠️ MODERATE RISK — Monitor site closely.", "moderate");
        } else if (riskValue.includes('low')) {
            showWebAlert(data.alert || "✅ LOW RISK — Conditions stable.", "low");
        }
        return data;
    } catch (err) {
        console.error("Risk Error:", err);
        updateRiskDisplay('unknown');
        return null;
    }
}

// Update the risk card visuals
function updateRiskDisplay(risk) {
    const el = document.getElementById('riskLevel');
    const bar = document.getElementById('riskBar');

    const normalized = (typeof risk === 'string') ? risk : String(risk);
    const low = normalized.includes('low');
    const med = normalized.includes('medium') || normalized.includes('moderate');
    const high = normalized.includes('high');

    if (high) {
        el.textContent = 'High';
        bar.style.width = '90%';
        bar.className = 'h-2 rounded-full bg-red-400';
    } else if (med) {
        el.textContent = 'Medium';
        bar.style.width = '60%';
        bar.className = 'h-2 rounded-full bg-amber-400';
    } else if (low) {
        el.textContent = 'Low';
        bar.style.width = '30%';
        bar.className = 'h-2 rounded-full bg-green-400';
    } else {
        el.textContent = '—'; // neutral
        bar.style.width = '0%';
        bar.className = 'h-2 rounded-full bg-gray-200';
    }

    const lastUpdated = document.getElementById('lastUpdated');
    if (lastUpdated) lastUpdated.textContent = new Date().toLocaleTimeString();
}

// ===============================
// Event handlers, UI
// ===============================
function setupEventListeners() {
    const predictBtn = document.getElementById('predictBtn');
    const latInput = document.getElementById('latitude');
    const lonInput = document.getElementById('longitude');

    predictBtn.addEventListener('click', async () => {
        const latVal = latInput.value;
        const lonVal = lonInput.value;

        if (!isCoordsValid(latVal, lonVal)) {
            // Invalid coords => show zeros and stop polling
            hasActiveCoords = false;
            stopVibrationPolling();
            showZeroState();
            showWebAlert("Enter valid non-zero coordinates and press Predict.", "warning");
            return;
        }

        // Valid coordinates — run the full fetch flow
        hasActiveCoords = true;

        // disable button while loading
        const originalHtml = predictBtn.innerHTML;
        predictBtn.disabled = true;
        predictBtn.innerHTML = '<i data-lucide="loader-2" class="h-4 w-4 mr-2 animate-spin"></i> Predicting...';
        lucide.createIcons();

        try {
            await Promise.all([
                loadWeatherData(latVal, lonVal),
                loadRiskPrediction(latVal, lonVal),
                loadSensorData()
            ]);

            // initialize/start vibration chart updates now that we have coords
            startVibrationPolling();
        } catch (err) {
            console.error("Predict flow error:", err);
        } finally {
            predictBtn.disabled = false;
            predictBtn.innerHTML = originalHtml;
            lucide.createIcons();
        }
    });

    // Optional: show chosen coords in the small display
    [latInput, lonInput].forEach(input => input.addEventListener('input', updateCoordinatesDisplay));
}

function updateCoordinatesDisplay() {
    const lat = document.getElementById('latitude').value;
    const lon = document.getElementById('longitude').value;
    const display = document.getElementById('coordinates-display');
    const span = document.getElementById('current-coords');

    if (isCoordsValid(lat, lon)) {
        display.classList.remove('hidden');
        span.textContent = `${lat}, ${lon}`;
    } else {
        display.classList.add('hidden');
        span.textContent = '';
    }
}

function animateCards() {
    const cards = document.querySelectorAll('.card-animate');
    cards.forEach((card, idx) => {
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, idx * 80);
    });
}

// ===============================
// Chart.js Vibration Chart (empty until predict)
// ===============================
function initializeVibrationChart(empty = false) {
    const canvas = document.getElementById('vibrationChart');
    if (!canvas) {
        console.error("vibrationChart canvas not found");
        return;
    }
    const ctx = canvas.getContext('2d');

    vibrationChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: empty ? [] : timeLabels,
            datasets: [{
                label: 'Vibration (Hz)',
                data: empty ? [] : vibrationData,
                borderColor: 'rgba(34,197,94,1)',
                backgroundColor: 'rgba(34,197,94,0.15)',
                borderWidth: 2,
                tension: 0.35,
                pointRadius: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                x: {
                    title: { display: true, text: 'Time (s)' },
                    ticks: { color: '#555' },
                    grid: { color: 'rgba(200,200,200,0.08)' }
                },
                y: {
                    title: { display: true, text: 'Vibration (Hz)' },
                    min: 0,
                    max: 2,
                    ticks: { stepSize: 0.2, color: '#555' },
                    grid: { color: 'rgba(200,200,200,0.08)' }
                }
            },
            plugins: {
                legend: { display: true },
                tooltip: { enabled: true }
            }
        }
    });

    // keep empty until user clicks Predict
    if (empty) clearVibrationChart();
}

// Fetch-and-update vibration (will be polled only after valid coords)
async function fetchAndUpdateVibration() {
    if (!hasActiveCoords) return; // safety guard

    try {
        const res = await fetch(`${API_BASE_URL}/sensors/vibration`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const vibVal = Number(data.vibration ?? fallbackSensorData.vibration);
        // update small card
        document.getElementById('vibration').textContent = `${vibVal.toFixed(2)} Hz`;

        // add to chart
        addVibrationPoint(vibVal);
    } catch (err) {
        console.error("Fetch vibration error:", err);
        // add fallback value to indicate instrument still running (optional)
        addVibrationPoint(fallbackSensorData.vibration);
    }
}

function addVibrationPoint(value) {
    if (!vibrationChart) return;

    timeCounter += 5;
    timeLabels.push(`${timeCounter}s`);
    vibrationData.push(Number(value));

    if (timeLabels.length > 20) {
        timeLabels.shift();
        vibrationData.shift();
    }

    vibrationChart.data.labels = timeLabels;
    vibrationChart.data.datasets[0].data = vibrationData;
    vibrationChart.update();
}

// ===============================
// Notifications (simple toast)
// ===============================
function showWebAlert(message, level = 'info') {
    const existing = document.querySelector('.risk-alert');
    if (existing) existing.remove();

    const box = document.createElement('div');
    box.className = 'risk-alert';
    let bg = '#3498db';
    if (level === 'high') bg = '#e74c3c';
    else if (level === 'moderate') bg = '#f39c12';
    else if (level === 'low') bg = '#2ecc71';
    else if (level === 'warning') bg = '#f1c40f';

    Object.assign(box.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 18px',
        borderRadius: '8px',
        color: '#fff',
        backgroundColor: bg,
        fontWeight: '600',
        zIndex: 9999
    });
    box.innerText = message;
    document.body.appendChild(box);
    setTimeout(() => {
        box.style.opacity = '0';
        setTimeout(() => box.remove(), 400);
    }, 4500);
}

// Simple generic notification (non-blocking)
function showNotification(message, type = 'info') {
    const n = document.createElement('div');
    n.className = 'fixed top-4 right-4 p-3 rounded z-50';
    n.style.background = (type === 'success') ? '#e6fffa' : (type === 'error') ? '#ffebee' : '#fff7ed';
    n.style.border = '1px solid rgba(0,0,0,0.05)';
    n.textContent = message;
    document.body.appendChild(n);
    setTimeout(() => {
        n.style.opacity = 0;
        setTimeout(() => n.remove(), 350);
    }, 3000);
}
