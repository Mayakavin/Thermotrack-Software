
// Initialize Charts
const chartOptions = { 
    responsive: true, 
    animation: false, 
    scales: { 
        y: { grid: { color: '#30363d' } }, 
        x: { display: false } 
    } 
};

const tempChart = new Chart(document.getElementById('tempChart'), { 
    type: 'line', 
    data: { labels: [], datasets: [{ label: 'Temp (°C)', data: [], borderColor: '#ff4444', tension: 0.4 }] }, 
    options: chartOptions 
});

const currChart = new Chart(document.getElementById('currChart'), { 
    type: 'line', 
    data: { labels: [], datasets: [{ label: 'Current (A)', data: [], borderColor: '#3399ff', tension: 0.4 }] }, 
    options: chartOptions 
});

async function updateDashboard() {
    try {
        const response = await fetch('/get_data');
        const data = await response.json();
        if (!data || data.length === 0) return;

        const latest = data[data.length - 1];

        // 1. Update Cards
        document.getElementById('temp-val').innerText = latest.temp.toFixed(1) + "°";
        document.getElementById('curr-val').innerText = latest.current.toFixed(2);
        document.getElementById('power-val').innerText = latest.power.toFixed(2);
        document.getElementById('health-val').innerText = (latest.health || 100) + "%";

        const sText = document.getElementById('status-text');
        sText.innerText = latest.status;
        sText.className = "value"; // Reset classes

        if (latest.status.includes("TRIP")) {
            sText.style.color = "#ff4444";
        } else if (latest.status.includes("HEALING")) {
            sText.style.color = "#ffa500";
            sText.classList.add("healing-pulse");
        } else {
            sText.style.color = "#00ff88";
        }

        // 2. Update Charts
        const recent = data.slice(-20);
        const labels = recent.map(d => d.timestamp.split(' ')[1]);
        tempChart.data.labels = labels;
        tempChart.data.datasets[0].data = recent.map(d => d.temp);
        tempChart.update();

        currChart.data.labels = labels;
        currChart.data.datasets[0].data = recent.map(d => d.current);
        currChart.update();

        // 3. Update Event Log Table
        const logBody = document.getElementById('event-log-body');
        logBody.innerHTML = ''; 
        data.slice(-100).reverse().forEach(row => {
            const tr = document.createElement('tr');
            const isAlert = row.status.includes("TRIP");
            tr.innerHTML = `
                <td class="small text-muted">${row.timestamp}</td>
                <td class="${isAlert ? 'text-danger fw-bold' : ''}">${row.status}</td>
            `;
            logBody.appendChild(tr);
        });

    } catch (err) { console.error("Update Error:", err); }
}

async function clearDatabase() {
    if (confirm("Clear logs?")) {
        await fetch('/clear_data', { method: 'POST' });
        location.reload();
    }
}

// Global scope for the clearDatabase function so the HTML button can find it
window.clearDatabase = clearDatabase;

setInterval(updateDashboard, 3000);
updateDashboard();