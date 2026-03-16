// frontend/script.js - WORKING VERSION

// Use the exact URL that worked in curl
const API_BASE = 'http://127.0.0.1:5000';

// Update clock
function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    
    const currentTime = document.getElementById('currentTime');
    if (currentTime) currentTime.textContent = timeStr;
    
    const timestamp = document.getElementById('timestamp');
    if (timestamp) timestamp.textContent = timeStr;
}

// Scroll progress
window.addEventListener('scroll', () => {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    
    const progressBar = document.getElementById('scrollProgress');
    if (progressBar) progressBar.style.width = scrolled + '%';
});

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateClock();
    setInterval(updateClock, 1000);
    checkConnection();
    loadArray();
    updateQuickScans();
});

// Check connection
async function checkConnection() {
    const statusDiv = document.getElementById('connectionStatus');
    if (!statusDiv) return;
    
    try {
        // Test the connection with a simple fetch
        const response = await fetch(API_BASE + '/');
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Connected to backend:', data);
            
            statusDiv.innerHTML = `
                <div class="status-dot" style="background: #4caf50;"></div>
                <span>CONNECTED TO DEEP SPACE NETWORK</span>
            `;
            return true;
        } else {
            throw new Error(`Status: ${response.status}`);
        }
    } catch (error) {
        console.error('Connection failed:', error);
        
        statusDiv.innerHTML = `
            <div class="status-dot" style="background: #f44336;"></div>
            <span>CONNECTION LOST - Using URL: ${API_BASE}</span>
        `;
        
        showError(`
            <strong>Cannot connect to backend!</strong><br>
            <small>Make sure backend is running at: <b>${API_BASE}</b></small><br>
            <small>You confirmed it works with curl, so this should work!</small>
        `);
        
        return false;
    }
}

// Load array
async function loadArray() {
    try {
        const response = await fetch(API_BASE + '/array');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📡 Array loaded:', data);
        
        if (data.array) {
            displayArray(data.array);
            updateArrayStats(data.array);
            updateInputRanges(data.size);
            
            const sizeInput = document.getElementById('arraySize');
            if (sizeInput) sizeInput.value = data.size;
            
            const activeCount = document.getElementById('activeCount');
            if (activeCount) activeCount.textContent = data.size;
            
            updateQuickScans(data.size);
        }
    } catch (error) {
        console.error('❌ Failed to load array:', error);
    }
}

// Display array
function displayArray(arr) {
    const container = document.querySelector('.array-grid');
    if (!container) return;
    
    container.innerHTML = '';
    
    arr.forEach((value, index) => {
        const item = document.createElement('div');
        item.className = 'array-item';
        item.id = `receiver-${index}`;
        item.onclick = () => quickQuery(index, index);
        
        item.innerHTML = `
            <div class="array-index">CH${index.toString().padStart(2, '0')}</div>
            <div class="array-value">${value.toFixed(2)}</div>
        `;
        container.appendChild(item);
    });
}

// Update array stats
function updateArrayStats(arr) {
    const peak = Math.max(...arr);
    const avg = arr.reduce((a, b) => a + b, 0) / arr.length;
    
    const peakEl = document.getElementById('peakValue');
    const avgEl = document.getElementById('avgValue');
    
    if (peakEl) peakEl.textContent = peak.toFixed(2);
    if (avgEl) avgEl.textContent = avg.toFixed(2);
}

// Update input ranges
function updateInputRanges(size) {
    const maxIndex = size - 1;
    
    const updateIndex = document.getElementById('updateIndex');
    const queryL = document.getElementById('queryL');
    const queryR = document.getElementById('queryR');
    
    if (updateIndex) updateIndex.max = maxIndex;
    if (queryL) queryL.max = maxIndex;
    if (queryR) queryR.max = maxIndex;
}

// Update quick scans
function updateQuickScans(size) {
    const container = document.getElementById('quickScans');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (size <= 3) {
        container.innerHTML = `
            <button class="scan-preset" onclick="quickQuery(0, ${size-1})">
                <span class="sector">FULL</span>
                <span class="range">[0-${size-1}]</span>
            </button>
        `;
        return;
    }
    
    const sectorSize = Math.floor(size / 3);
    
    const sectors = [
        { name: 'ALPHA', start: 0, end: sectorSize - 1 },
        { name: 'BETA', start: sectorSize, end: 2 * sectorSize - 1 },
        { name: 'GAMMA', start: 2 * sectorSize, end: size - 1 }
    ];
    
    sectors.forEach(sector => {
        const btn = document.createElement('button');
        btn.className = 'scan-preset';
        btn.onclick = () => quickQuery(sector.start, sector.end);
        btn.innerHTML = `
            <span class="sector">${sector.name}</span>
            <span class="range">[${sector.start}-${sector.end}]</span>
        `;
        container.appendChild(btn);
    });
    
    const fullBtn = document.createElement('button');
    fullBtn.className = 'scan-preset';
    fullBtn.onclick = () => quickQuery(0, size - 1);
    fullBtn.innerHTML = `
        <span class="sector">FULL</span>
        <span class="range">[0-${size-1}]</span>
    `;
    container.appendChild(fullBtn);
}

// Handle resize
async function handleResize() {
    const newSize = document.getElementById('arraySize')?.value;
    const defaultValue = document.getElementById('defaultValue')?.value;
    
    if (!newSize) {
        showError('Please enter array size');
        return;
    }
    
    try {
        const response = await fetch(API_BASE + '/resize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                size: parseInt(newSize),
                default_value: parseFloat(defaultValue || '0')
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            await loadArray();
            
            const resultsSection = document.getElementById('resultsSection');
            if (resultsSection) resultsSection.style.display = 'none';
            
            showMessage(`✓ Array resized to ${newSize} receivers`, 'success');
        } else {
            showError(data.error || 'Resize failed');
        }
    } catch (error) {
        showError('Failed to resize array');
    }
}

// Handle update
async function handleUpdate() {
    const index = document.getElementById('updateIndex')?.value;
    const value = document.getElementById('updateValue')?.value;
    
    const messageDiv = document.getElementById('updateMessage');
    if (messageDiv) {
        messageDiv.className = 'message';
        messageDiv.innerHTML = '';
    }
    
    if (!index || !value) {
        if (messageDiv) {
            messageDiv.className = 'message error';
            messageDiv.innerHTML = 'Please fill all fields';
        }
        return;
    }
    
    try {
        const response = await fetch(API_BASE + '/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                index: parseInt(index),
                value: parseFloat(value)
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (messageDiv) {
                messageDiv.className = 'message success';
                messageDiv.innerHTML = `✓ CH${index} updated to ${value} MHz`;
            }
            
            await loadArray();
            
            const resultsSection = document.getElementById('resultsSection');
            if (resultsSection) resultsSection.style.display = 'none';
            
            // Flash updated receiver
            const element = document.getElementById(`receiver-${index}`);
            if (element) {
                element.classList.add('glow');
                setTimeout(() => element.classList.remove('glow'), 2000);
            }
            
            setTimeout(() => {
                if (messageDiv) {
                    messageDiv.innerHTML = '';
                    messageDiv.className = 'message';
                }
            }, 3000);
            
        } else {
            if (messageDiv) {
                messageDiv.className = 'message error';
                messageDiv.innerHTML = `Error: ${data.error || 'Update failed'}`;
            }
        }
    } catch (error) {
        if (messageDiv) {
            messageDiv.className = 'message error';
            messageDiv.innerHTML = 'Connection lost';
        }
    }
}

// Handle query
async function handleQuery() {
    const L = document.getElementById('queryL')?.value;
    const R = document.getElementById('queryR')?.value;
    
    hideError();
    
    if (!L || !R) {
        showError('Please enter both L and R values');
        return;
    }
    
    // Remove old glow
    removeAllGlow();
    
    // Add glow to selected range
    for (let i = parseInt(L); i <= parseInt(R); i++) {
        const element = document.getElementById(`receiver-${i}`);
        if (element) element.classList.add('glow');
    }
    
    try {
        const response = await fetch(`${API_BASE}/query?L=${L}&R=${R}`);
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data, parseInt(L), parseInt(R));
        } else {
            showError(data.error || 'Query failed');
            removeAllGlow();
        }
    } catch (error) {
        showError('Failed to connect to server');
        removeAllGlow();
    }
}

// Quick query
async function quickQuery(L, R) {
    const queryL = document.getElementById('queryL');
    const queryR = document.getElementById('queryR');
    
    if (queryL) queryL.value = L;
    if (queryR) queryR.value = R;
    
    await handleQuery();
}

// Remove all glow
function removeAllGlow() {
    document.querySelectorAll('.array-item').forEach(item => {
        item.classList.remove('glow');
    });
}

// Display results
function displayResults(stats, L, R) {
    const minEl = document.getElementById('minValue');
    const maxEl = document.getElementById('maxValue');
    const meanEl = document.getElementById('meanValue');
    const varEl = document.getElementById('varianceValue');
    const rangeInfo = document.getElementById('rangeInfo');
    const resultsSection = document.getElementById('resultsSection');
    
    if (minEl) minEl.textContent = stats.min.toFixed(2);
    if (maxEl) maxEl.textContent = stats.max.toFixed(2);
    if (meanEl) meanEl.textContent = stats.mean.toFixed(2);
    if (varEl) varEl.textContent = stats.variance.toFixed(2);
    
    if (rangeInfo) {
        rangeInfo.innerHTML = `
            <i class="fas fa-satellite"></i>
            <span>SECTOR [${L}-${R}] • ${stats.length} RECEIVERS</span>
        `;
    }
    
    if (resultsSection) {
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Show message
function showMessage(text, type) {
    const msgDiv = document.getElementById('updateMessage');
    if (!msgDiv) return;
    
    msgDiv.className = `message ${type}`;
    msgDiv.innerHTML = text;
    
    setTimeout(() => {
        msgDiv.innerHTML = '';
        msgDiv.className = 'message';
    }, 3000);
}

// Show error
function showError(message) {
    const errorPanel = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    if (!errorPanel || !errorText) return;
    
    errorText.innerHTML = message;
    errorPanel.style.display = 'flex';
    
    // Auto hide after 8 seconds
    setTimeout(() => {
        errorPanel.style.display = 'none';
    }, 8000);
}

// Hide error
function hideError() {
    const errorPanel = document.getElementById('errorMessage');
    if (errorPanel) errorPanel.style.display = 'none';
}

// Auto-refresh array
setInterval(loadArray, 30000);