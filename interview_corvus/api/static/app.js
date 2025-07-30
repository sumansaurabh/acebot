const API_BASE = '';
let bruteSolution = null;
let optimizedSolution = null;
let isWindowOpen = true; // Track toggle state, default is open

// Recording variables
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// File management variables
let availableFiles = {};
let selectedFileKeys = [];

// Load existing solutions from backend
async function loadExistingSolutions() {
    try {
        // Check if there are existing solutions in the backend
        const response = await fetch(`${API_BASE}/solution/current`);
        if (response.ok) {
            const result = await response.json();
            
            // Load brute solution if it exists
            if (result.brute_solution) {
                bruteSolution = result.brute_solution;
                displayBruteSolution(result.brute_solution);
                document.getElementById('optimizeBtn').disabled = false;
            }
            
            // Load optimized solution if it exists
            if (result.optimized_solution) {
                optimizedSolution = result.optimized_solution;
                displayOptimizedSolution(result.optimized_solution);
            }
        }
    } catch (error) {
        console.error('Failed to load existing solutions:', error);
    }
}

function updateStatus(message, type = 'info') {
    const statusBar = document.getElementById('statusBar');
    statusBar.textContent = message;
}

function showLoading(show = true) {
    const spinner = document.getElementById('loadingSpinner');
    spinner.style.display = show ? 'block' : 'none';
}

function updateLanguageDropdown() {
    fetch(`${API_BASE}/language`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const languageSelect = document.getElementById('languageSelect');
                // Clear existing options
                languageSelect.innerHTML = '';
                
                // Add available languages
                data.available_languages.forEach(lang => {
                    const option = document.createElement('option');
                    option.value = lang;
                    option.textContent = lang.charAt(0).toUpperCase() + lang.slice(1);
                    if (lang === data.current_language) {
                        option.selected = true;
                    }
                    languageSelect.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Failed to load language settings:', error);
        });
}

async function changeLanguage(language) {
    try {
        const response = await fetch(`${API_BASE}/language`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ language: language })
        });
        const result = await response.json();
        if (result.success) {
            updateStatus(`Language set to ${language}`);
        } else {
            updateStatus(`Error: ${result.message}`);
        }
    } catch (error) {
        updateStatus('Failed to change language');
    }
}

function updateScreenshotCount() {
    fetch(`${API_BASE}/screenshots`)
        .then(response => response.json())
        .then(data => {
            const count = data.screenshots ? data.screenshots.length : 0;
            document.getElementById('screenshotCount').textContent = count;
            // Enable/disable solve button based on screenshot availability
            document.getElementById('solveBtn').disabled = count === 0;
        })
        .catch(() => { 
            document.getElementById('screenshotCount').textContent = '0';
            document.getElementById('solveBtn').disabled = true;
        });
}

async function captureScreen() {
    updateStatus('Capturing...'); showLoading(true);
    try {
        // Get current count before capture
        const currentCount = parseInt(document.getElementById('screenshotCount').textContent);
        
        const response = await fetch(`${API_BASE}/screenshot/capture`, { method: 'POST' });
        const result = await response.json();
        if (response.ok) {
            updateStatus('Captured');
            // Immediately update count without waiting for API call
            const newCount = Math.min(currentCount + 1, 10); // Max 10 screenshots
            document.getElementById('screenshotCount').textContent = newCount;
            // Enable solve button if we have screenshots
            document.getElementById('solveBtn').disabled = newCount === 0;
        } else updateStatus('Error: ' + result.message);
    } catch (error) { updateStatus('Connection error'); }
    finally { showLoading(false); }
}

async function recordScreen() {
    if (isRecording) {
        // Stop recording
        stopRecording();
        return;
    }
    
    // Check if browser supports media recording
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        updateStatus('Recording not supported in this browser');
        return;
    }
    
    try {
        updateStatus('Starting recording...'); 
        showLoading(true);
        
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Create MediaRecorder
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        isRecording = true;
        
        // Update UI
        const recordBtn = document.getElementById('recordBtn');
        recordBtn.innerHTML = '<i class="fas fa-stop"></i>';
        recordBtn.style.background = '#ef4444';
        
        // Handle data collection
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        // Handle recording stop
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await processRecording(audioBlob);
        };
        
        // Start recording
        mediaRecorder.start();
        updateStatus('Recording... Click record button again to stop');
        showLoading(false);
        
    } catch (error) {
        updateStatus('Failed to start recording: ' + error.message);
        showLoading(false);
        console.error('Recording error:', error);
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Stop all audio tracks
        if (mediaRecorder.stream) {
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
        
        // Reset UI
        const recordBtn = document.getElementById('recordBtn');
        recordBtn.innerHTML = '<i class="fas fa-video"></i>';
        recordBtn.style.background = '#ec4899';
        
        updateStatus('Processing recording...');
        showLoading(true);
    }
}

async function processRecording(audioBlob) {
    try {
        // Convert blob to base64
        const base64Audio = await blobToBase64(audioBlob);
        
        // Send to server with selected files
        const response = await fetch(`${API_BASE}/recording/mobile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                audio_data: base64Audio.split(',')[1], // Remove data:audio/wav;base64, prefix
                recording_type: 'mobile',
                selected_file_keys: selectedFileKeys // Include selected file keys
            })
        });
        
        const result = await response.json();
        if (response.ok && result.success) {
            if (selectedFileKeys.length > 0) {
                updateStatus(`Recording received, analyzing ${selectedFileKeys.length} selected files...`);
            } else {
                updateStatus('Recording received, providing generic analysis...');
            }
            // Start streaming analysis
            await startRecordingAnalysisStream();
        } else {
            updateStatus('Error: ' + result.message);
            showLoading(false);
        }
    } catch (error) {
        updateStatus('Failed to process recording: ' + error.message);
        showLoading(false);
        console.error('Processing error:', error);
    }
}

async function startRecordingAnalysisStream() {
    try {
        // Clear previous results
        document.getElementById('resultsContainer').style.display = 'block';
        document.getElementById('bruteSection').style.display = 'block';
        
        if (selectedFileKeys.length > 0) {
            document.getElementById('bruteExplanation').innerHTML = '<div class="streaming-content">Analyzing selected files...</div>';
        } else {
            document.getElementById('bruteExplanation').innerHTML = '<div class="streaming-content">Providing generic analysis...</div>';
        }
        document.getElementById('bruteCode').textContent = '';
        
        // Start Server-Sent Events stream
        const eventSource = new EventSource(`${API_BASE}/recording/stream`);
        let accumulatedText = '';
        
        eventSource.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                
                if (data.error) {
                    updateStatus('Error: ' + data.error);
                    showLoading(false);
                    eventSource.close();
                    return;
                }
                
                if (data.status === 'starting_analysis') {
                    if (selectedFileKeys.length > 0) {
                        updateStatus('File analysis starting...');
                    } else {
                        updateStatus('Generic analysis starting...');
                    }
                    return;
                }
                
                if (data.chunk) {
                    // Append new chunk
                    accumulatedText += data.chunk;
                    
                    // Update display with streaming content
                    const explanationHtml = marked.parse(accumulatedText);
                    document.getElementById('bruteExplanation').innerHTML = explanationHtml;
                    
                    // Update status
                    if (selectedFileKeys.length > 0) {
                        updateStatus(`Analyzing files... (${data.total_length} characters)`);
                    } else {
                        updateStatus(`Providing analysis... (${data.total_length} characters)`);
                    }
                }
                
                if (data.status === 'completed') {
                    // Final update
                    const explanationHtml = marked.parse(data.complete_text);
                    document.getElementById('bruteExplanation').innerHTML = explanationHtml;
                    
                    if (selectedFileKeys.length > 0) {
                        updateStatus(`File analysis completed (${data.final_length} characters)`);
                    } else {
                        updateStatus(`Generic analysis completed (${data.final_length} characters)`);
                    }
                    showLoading(false);
                    eventSource.close();
                }
                
            } catch (parseError) {
                console.error('Failed to parse SSE data:', parseError);
            }
        };
        
        eventSource.onerror = function(event) {
            updateStatus('Stream connection error');
            showLoading(false);
            eventSource.close();
        };
        
        // Auto-close after 5 minutes
        setTimeout(() => {
            if (eventSource.readyState === EventSource.OPEN) {
                eventSource.close();
                updateStatus('Analysis timeout');
                showLoading(false);
            }
        }, 300000);
        
    } catch (error) {
        updateStatus('Failed to start analysis stream: ' + error.message);
        showLoading(false);
        console.error('Stream error:', error);
    }
}

function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

async function solveBrute() {
    updateStatus('Solving...'); showLoading(true);
    try {
        const languageSelect = document.getElementById('languageSelect');
        const selectedLanguage = languageSelect.value;
        
        const response = await fetch(`${API_BASE}/solution`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ language: selectedLanguage })
        });
        const result = await response.json();
        if (response.ok && result.solution) {
            bruteSolution = result.solution;
            displayBruteSolution(result.solution);
            updateStatus('Solved');
            document.getElementById('optimizeBtn').disabled = false;
        } else updateStatus('Error: ' + result.message);
    } catch (error) { updateStatus('Connection error'); }
    finally { showLoading(false); }
}

async function optimizeBest() {
    if (!bruteSolution) { updateStatus('Solve first'); return; }
    updateStatus('Optimizing...'); showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/optimize`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code: bruteSolution.code, language: bruteSolution.language })
        });
        const result = await response.json();
        if (response.ok && result.optimization) {
            optimizedSolution = result.optimization;
            displayOptimizedSolution(result.optimization);
            updateStatus('Optimized');
        } else updateStatus('Error: ' + result.message);
    } catch (error) { updateStatus('Connection error'); }
    finally { showLoading(false); }
}

async function clearScreenshots() {
    updateStatus('Clearing...'); showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/screenshots`, { method: 'DELETE' });
        const result = await response.json();
        if (response.ok && result.success) {
            updateStatus('Cleared');
            // Immediately update count
            document.getElementById('screenshotCount').textContent = '0';
            document.getElementById('solveBtn').disabled = true;
            document.getElementById('resultsContainer').style.display = 'none';
            document.getElementById('bruteSection').style.display = 'none';
            document.getElementById('optimizedSection').style.display = 'none';
            bruteSolution = null;
            optimizedSolution = null;
            document.getElementById('optimizeBtn').disabled = true;
        } else updateStatus('Error: ' + result.message);
    } catch (error) { updateStatus('Connection error'); }
    finally { showLoading(false); }
}

async function resetAll() {
    updateStatus('Resetting...'); showLoading(true);
    try {
        const response1 = await fetch(`${API_BASE}/screenshots`, { method: 'DELETE' });
        const response2 = await fetch(`${API_BASE}/history`, { method: 'DELETE' });
        const result1 = await response1.json();
        const result2 = await response2.json();
        if ((response1.ok && result1.success) && (response2.ok && result2.success)) {
            updateStatus('Reset');
            // Immediately update count
            document.getElementById('screenshotCount').textContent = '0';
            document.getElementById('solveBtn').disabled = true;
            document.getElementById('resultsContainer').style.display = 'none';
            document.getElementById('bruteSection').style.display = 'none';
            document.getElementById('optimizedSection').style.display = 'none';
            bruteSolution = null;
            optimizedSolution = null;
            document.getElementById('optimizeBtn').disabled = true;
        } else updateStatus('Error: ' + (result1.message || result2.message));
    } catch (error) { updateStatus('Connection error'); }
    finally { showLoading(false); }
}

function displayBruteSolution(solution) {
    document.getElementById('resultsContainer').style.display = 'block';
    document.getElementById('bruteSection').style.display = 'block';
    
    // Render markdown explanation
    const explanationHtml = marked.parse(solution.explanation || 'No explanation provided.');
    document.getElementById('bruteExplanation').innerHTML = explanationHtml;

    let edgeCasesHtml = '';
    if (solution.edge_cases && solution.edge_cases.length > 0) {
        edgeCasesHtml = '<h3>Edge Cases Handled:</h3><ul>';
        solution.edge_cases.forEach(edgeCase => {
            edgeCasesHtml += `<li>${edgeCase}</li>`;
        });
        edgeCasesHtml += '</ul>';
    } else {
        edgeCasesHtml = '<p>No specific edge cases handled.</p>';
    }
    document.getElementById('edgeCases').innerHTML = edgeCasesHtml;
    
    // Only show code and complexity for actual code solutions, not recording analysis
    if (solution.code && solution.source !== 'recording') {
        // Render syntax-highlighted code
        document.getElementById('bruteCode').textContent = solution.code;
        Prism.highlightElement(document.getElementById('bruteCode'));
        
        document.getElementById('bruteTimeComplexity').textContent = solution.time_complexity || '-';
        document.getElementById('bruteSpaceComplexity').textContent = solution.space_complexity || '-';
        
        // Show complexity info and enable optimize button
        const complexityInfo = document.querySelector('#bruteSection .complexity-info');
        if (complexityInfo) {
            complexityInfo.style.display = 'flex';
        }
        document.getElementById('optimizeBtn').disabled = false;
    } else {
        // Hide code and complexity for recording analysis
        document.getElementById('bruteCode').textContent = '';
        
        const complexityInfo = document.querySelector('#bruteSection .complexity-info');
        if (complexityInfo) {
            complexityInfo.style.display = 'none';
        }
        // Don't enable optimize for recording analysis
        document.getElementById('optimizeBtn').disabled = true;
    }
}

function displayOptimizedSolution(optimization) {
    document.getElementById('optimizedSection').style.display = 'block';
    
    // Render markdown explanation
    const explanationHtml = marked.parse(optimization.explanation || 'No optimization explanation provided.');
    document.getElementById('optimizedExplanation').innerHTML = explanationHtml;
    
    // Render syntax-highlighted optimized code
    document.getElementById('optimizedCode').textContent = optimization.optimized_code || '';
    Prism.highlightElement(document.getElementById('optimizedCode'));
    
    document.getElementById('optimizedTimeComplexity').textContent = optimization.optimized_time_complexity || '-';
    document.getElementById('optimizedSpaceComplexity').textContent = optimization.optimized_space_complexity || '-';
    let optimizedEdgeCasesHtml = '';
    if (optimization.optimized_edge_cases && optimization.optimized_edge_cases.length > 0) {
        optimizedEdgeCasesHtml = '<h3>Optimized Edge Cases Handled:</h3><ul>';
        optimization.optimized_edge_cases.forEach(edgeCase => {
            optimizedEdgeCasesHtml += `<li>${edgeCase}</li>`;
        });
        optimizedEdgeCasesHtml += '</ul>';
    } else {
        optimizedEdgeCasesHtml = '<p>No specific edge cases handled in optimization.</p>';
    }
    document.getElementById('optimizedEdgeCases').innerHTML = optimizedEdgeCasesHtml;
}

function toggleWindow() {
    fetch(`${API_BASE}/window/toggle`, { method: 'POST' })
        .then(() => {
            isWindowOpen = !isWindowOpen;
            const toggleBtn = document.getElementById('toggleBtn');
            toggleBtn.innerHTML = isWindowOpen ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
            updateStatus('Toggled');
        })
        .catch(() => updateStatus('Toggle failed'));
}

// File management functions
async function loadAvailableFiles() {
    try {
        const response = await fetch(`${API_BASE}/files/available`);
        const data = await response.json();
        if (data.success) {
            availableFiles = data.available_files || {};
            selectedFileKeys = Object.keys(availableFiles).filter(key => availableFiles[key].selected);
            renderAvailableFiles();
        }
    } catch (error) {
        console.error('Error loading available files:', error);
    }
}

function renderAvailableFiles() {
    const filesList = document.getElementById('availableFilesList');
    
    if (Object.keys(availableFiles).length === 0) {
        filesList.innerHTML = '<div class="file-selection-empty">No files available. Please upload files first using the desktop application.</div>';
        return;
    }

    filesList.innerHTML = Object.keys(availableFiles).map(fileKey => {
        const fileInfo = availableFiles[fileKey];
        const isSelected = selectedFileKeys.includes(fileKey);
        return `
            <div class="file-checkbox-item" onclick="toggleFileSelection('${fileKey}')">
                <input type="checkbox" ${isSelected ? 'checked' : ''} onchange="toggleFileSelection('${fileKey}')" onclick="event.stopPropagation()">
                <div class="file-name" title="${fileInfo.filename}">${fileInfo.filename}</div>
            </div>
        `;
    }).join('');
}

async function toggleFileSelection(fileKey) {
    try {
        const isCurrentlySelected = selectedFileKeys.includes(fileKey);
        const action = isCurrentlySelected ? 'remove' : 'add';
        
        const response = await fetch(`${API_BASE}/files/manage`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                file_key: fileKey,
                action: action
            })
        });
        
        const result = await response.json();
        if (result.success) {
            availableFiles = result.available_files || {};
            selectedFileKeys = Object.keys(availableFiles).filter(key => availableFiles[key].selected);
            renderAvailableFiles();
            updateStatus(result.message);
        } else {
            updateStatus(`Error: ${result.message}`);
        }
    } catch (error) {
        console.error('Error toggling file selection:', error);
        updateStatus('Error updating file selection');
    }
}

async function clearAllFiles() {
    if (selectedFileKeys.length === 0) return;
    
    if (!confirm('Are you sure you want to clear all file selections?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/files/manage`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                file_key: '',
                action: 'clear'
            })
        });
        
        const result = await response.json();
        if (result.success) {
            availableFiles = result.available_files || {};
            selectedFileKeys = [];
            renderAvailableFiles();
            updateStatus('All file selections cleared');
        }
    } catch (error) {
        console.error('Error clearing files:', error);
        updateStatus('Error clearing file selections');
    }
}

// Initialize on page load
window.addEventListener('load', () => {
    document.getElementById('solveBtn').disabled = true;
    document.getElementById('optimizeBtn').disabled = true;
    
    // Load existing solutions from backend
    loadExistingSolutions();
    
    // Initialize file management
    loadAvailableFiles();
    
    updateScreenshotCount();
    updateLanguageDropdown();
    updateStatus('Ready');
});

// Set up periodic updates
setInterval(updateScreenshotCount, 5000);
setInterval(updateLanguageDropdown, 10000); // Update language every 10 seconds
