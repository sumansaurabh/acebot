"""
HTML template for the AceBot web UI.
Contains the complete HTML/CSS/JS for the web interface.
"""


def get_main_ui_template() -> str:
    """Get the main web UI HTML template."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes, minimum-scale=1.0, maximum-scale=5.0">
    <title>🤖 AceBot</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet" />
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/4.3.0/marked.min.js"></script>
    <style>
        html, body { background: #fff; margin: 0; padding: 0; }
        body { font-family: system-ui, sans-serif; font-size: 15px; color: #222; }
        .main-content { max-width: 800px; margin: 0 auto; padding: 12px 0 0 0; }
        .action-buttons {
            display: flex;
            justify-content: center;
            gap: 6px;
            margin-bottom: 28px;
            flex-wrap: wrap;
            width: 100%;
            max-width: 800px;
        }
        .left-buttons {
            display: flex;
            gap: 8px;
        }
        .right-buttons {
            display: flex;
            gap: 8px;
        }
        .action-btn {
            padding: 8px;
            border: none;
            border-radius: 6px;
            font-size: 20px;
            cursor: pointer;
            min-height: 50px;
            flex: 1;
            transition: all 0.2s ease;
            box-shadow: 0 2px 6px rgba(0,0,0,0.12);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            max-width: 120px;
            aspect-ratio: 1;
        }
        .action-btn::after {
            content: attr(data-label);
            position: absolute;
            bottom: -16px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 9px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #6b7280;
            opacity: 0.8;
        }
        .capture-btn { background: #10b981; color: white; }
        .capture-btn:hover { background: #059669; transform: translateY(-2px); }
        .solve-btn { background: #3b82f6; color: white; }
        .solve-btn:hover { background: #2563eb; transform: translateY(-2px); }
        .optimize-btn { background: #f59e0b; color: white; }
        .optimize-btn:hover { background: #d97706; transform: translateY(-2px); }
        .toggle-btn { background: #8b5cf6; color: white; }
        .toggle-btn:hover { background: #7c3aed; transform: translateY(-2px); }
        .reset-btn { background: #6b7280; color: white; }
        .reset-btn:hover { background: #4b5563; transform: translateY(-2px); }
        .record-btn { background: #ec4899; color: white; }
        .record-btn:hover { background: #db2777; transform: translateY(-2px); }
        .action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .status-bar {
            font-size: 13px;
            margin-bottom: 10px;
            color: #666;
            min-height: 18px;
        }
        .info-bar {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin: 24px 0 20px 0;
            flex-wrap: wrap;
        }
        .language-selector {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .language-selector label {
            font-size: 12px;
            font-weight: 600;
            color: #6b7280;
            white-space: nowrap;
        }
        .language-selector select {
            padding: 4px 8px;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            font-size: 12px;
            background: white;
            color: #374151;
            cursor: pointer;
            min-width: 90px;
        }
        .screenshot-count {
            font-size: 12px;
            font-weight: 600;
            color: #3b82f6;
            background: #eff6ff;
            padding: 6px 12px;
            border-radius: 16px;
            white-space: nowrap;
        }
        .loading-spinner {
            display: none;
            width: 22px;
            height: 22px;
            border: 3px solid #eee;
            border-top: 3px solid #888;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 10px auto;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .results-container { margin-top: 12px; }
        .result-section { 
            background: #fafbfc; 
            border-radius: 8px; 
            padding: 16px; 
            border: 1px solid #e1e4e8; 
            margin-bottom: 16px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .section-header {
            font-size: 16px;
            font-weight: 600;
            color: #24292e;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e1e4e8;
        }
        .brute-header { border-bottom-color: #2196f3; }
        .optimized-header { border-bottom-color: #ff9800; }
        
        .explanation { 
            font-size: 14px; 
            line-height: 1.6;
            margin: 12px 0; 
            color: #24292e;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        .explanation h1, .explanation h2, .explanation h3 {
            color: #24292e;
            margin-top: 16px;
            margin-bottom: 8px;
            word-wrap: break-word;
        }
        .explanation h1 { font-size: 18px; }
        .explanation h2 { font-size: 16px; }
        .explanation h3 { font-size: 14px; }
        .explanation p { 
            margin: 8px 0; 
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        .explanation ul, .explanation ol { 
            margin: 8px 0 8px 20px; 
            padding-left: 0;
        }
        .explanation li { 
            margin: 4px 0; 
            word-wrap: break-word;
            overflow-wrap: break-word;
        }
        .explanation code {
            background: #f6f8fa;
            border: 1px solid #e1e4e8;
            border-radius: 3px;
            padding: 2px 4px;
            font-size: 13px;
            font-family: Monaco, "Cascadia Code", "Fira Code", monospace;
            word-break: break-all;
            white-space: pre-wrap;
        }
        .explanation blockquote {
            border-left: 4px solid #dfe2e5;
            padding-left: 16px;
            margin-left: 0;
            color: #6a737d;
            word-wrap: break-word;
        }
        
        .code-block { 
            background: #1e1e1e !important; 
            color: #d4d4d4 !important; 
            border-radius: 8px !important; 
            font-size: 13px; 
            padding: 16px !important; 
            overflow-x: auto; 
            margin: 12px 0 !important;
            border: 1px solid #3c3c3c !important;
            font-family: Monaco, "Cascadia Code", "Fira Code", "JetBrains Mono", Consolas, monospace !important;
        }
        .code-block code {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            color: inherit !important;
        }
        
        /* Prism.js syntax highlighting colors for dark background */
        .code-block .token.comment,
        .code-block .token.prolog,
        .code-block .token.doctype,
        .code-block .token.cdata {
            color: #6A9955;
            font-style: italic;
        }
        .code-block .token.namespace {
            opacity: 0.7;
        }
        .code-block .token.string,
        .code-block .token.attr-value {
            color: #CE9178;
        }
        .code-block .token.punctuation,
        .code-block .token.operator {
            color: #D4D4D4;
        }
        .code-block .token.entity,
        .code-block .token.url,
        .code-block .token.symbol,
        .code-block .token.number,
        .code-block .token.boolean,
        .code-block .token.variable,
        .code-block .token.constant,
        .code-block .token.property,
        .code-block .token.regex,
        .code-block .token.inserted {
            color: #B5CEA8;
        }
        .code-block .token.atrule,
        .code-block .token.keyword,
        .code-block .token.attr-name {
            color: #569CD6;
        }
        .code-block .token.function {
            color: #DCDCAA;
        }
        .code-block .token.deleted {
            color: #F44747;
        }
        .code-block .token.tag,
        .code-block .token.selector {
            color: #F44747;
        }
        .code-block .token.class-name {
            color: #4EC9B0;
        }
        .code-block .token.important,
        .code-block .token.bold {
            font-weight: bold;
        }
        .code-block .token.italic {
            font-style: italic;
        }
        
        .complexity-info { display: flex; gap: 10px; font-size: 12px; margin: 5px 0; }
        .complexity-item { background: #fff; border: 1px solid #eee; border-radius: 4px; padding: 3px 8px; }
        
        /* Streaming content styles */
        .streaming-content {
            background: linear-gradient(90deg, #f0f9ff, #e0f2fe, #f0f9ff);
            background-size: 200% 100%;
            animation: shimmer 2s ease-in-out infinite;
            padding: 8px 12px;
            border-radius: 4px;
            color: #0369a1;
            font-style: italic;
        }
        
        @keyframes shimmer {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        /* Recording button active state */
        .record-btn.recording {
            background: #ef4444 !important;
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        /* File Selection Section Styles */
        .file-selection-section {
            margin: 20px 0;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 16px;
            background: #fafafa;
        }
        
        .file-selection-section .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            font-weight: 600;
            font-size: 14px;
            color: #333;
        }
        
        .available-files-list {
            max-height: 200px;
            overflow-y: auto;
        }
        
        .file-checkbox-item {
            display: flex;
            align-items: center;
            padding: 8px 12px;
            margin-bottom: 4px;
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            font-size: 13px;
            cursor: pointer;
            transition: background 0.2s ease;
        }
        
        .file-checkbox-item:hover {
            background: #f0f8ff;
        }
        
        .file-checkbox-item input[type="checkbox"] {
            margin-right: 8px;
            cursor: pointer;
        }
        
        .file-checkbox-item .file-name {
            flex: 1;
            word-break: break-all;
            color: #333;
        }
        
        .file-selection-empty {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 20px;
        }
        
        .btn-small {
            padding: 4px 8px;
            font-size: 12px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            background: #dc3545;
            color: white;
            transition: background 0.2s ease;
        }
        
        .btn-small:hover {
            background: #c82333;
        }

        @media (max-width: 600px) {
            .main-content { padding: 8px 12px 0 12px; }
            .action-buttons { 
                gap: 4px; 
                margin-bottom: 24px; 
                padding: 0 4px;
            }
            .action-btn { 
                font-size: 18px; 
                min-height: 36px; 
                padding: 6px;
                max-width: none;
                flex: 1;
                aspect-ratio: 1;
            }
            .action-btn::after { font-size: 8px; bottom: -14px; }
            .info-bar { gap: 12px; margin: 20px 0 16px 0; }
            .language-selector label { font-size: 11px; }
            .language-selector select { font-size: 11px; padding: 3px 6px; min-width: 80px; }
            .screenshot-count { font-size: 11px; padding: 5px 10px; }
            
            /* Result sections mobile optimization */
            .result-section { 
                padding: 12px 8px; 
                margin-bottom: 12px;
                border-radius: 6px;
            }
            .section-header {
                font-size: 14px;
                margin-bottom: 8px;
                padding-bottom: 6px;
            }
            
            .explanation { 
                font-size: 12px; 
                line-height: 1.5;
                margin: 8px 0;
                padding: 0 4px;
            }
            .explanation h1 { 
                font-size: 15px; 
                margin-top: 12px;
                margin-bottom: 6px;
            }
            .explanation h2 { 
                font-size: 14px; 
                margin-top: 10px;
                margin-bottom: 5px;
            }
            .explanation h3 { 
                font-size: 13px; 
                margin-top: 8px;
                margin-bottom: 4px;
            }
            .explanation p {
                margin: 6px 0;
                text-align: left;
            }
            .explanation ul, .explanation ol { 
                margin: 6px 0 6px 12px; 
                padding-left: 0;
            }
            .explanation li {
                margin: 2px 0;
                padding-left: 0;
            }
            .explanation code { 
                font-size: 11px; 
                padding: 1px 3px;
                word-break: break-all;
                white-space: pre-wrap;
            }
            .explanation blockquote {
                padding-left: 8px;
                margin: 6px 0;
                font-size: 11px;
            }
            .code-block { 
                font-size: 11px; 
                padding: 8px !important; 
                margin: 8px 0 !important;
                overflow-x: auto;
                white-space: pre-wrap;
                word-break: break-all;
            }
            
            /* Mobile file selection styles */
            .file-selection-section { margin: 16px 0; padding: 12px 8px; }
            .file-checkbox-item { padding: 6px 8px; font-size: 12px; }
            .file-checkbox-item .file-name { font-size: 12px; }
            .btn-small { padding: 3px 6px; font-size: 11px; }
        }
    </style>
</head>
<body>
    <div class="main-content">
        <div class="action-buttons">
            <button class="action-btn capture-btn" onclick="captureScreen()" id="captureBtn" data-label="capture" title="Capture Screen"><i class="fas fa-camera"></i></button>
            <button class="action-btn solve-btn" onclick="solveBrute()" id="solveBtn" data-label="solve" title="Solve Problem"><i class="fas fa-brain"></i></button>
            <button class="action-btn optimize-btn" onclick="optimizeBest()" id="optimizeBtn" data-label="optimize" title="Optimize Solution"><i class="fas fa-bolt"></i></button>
            <button class="action-btn record-btn" onclick="recordScreen()" id="recordBtn" data-label="record" title="Record Screen"><i class="fas fa-video"></i></button>
            <button class="action-btn toggle-btn" onclick="toggleWindow()" id="toggleBtn" data-label="toggle" title="Toggle Window"><i class="fas fa-eye"></i></button>
            <button class="action-btn reset-btn" onclick="resetAll()" id="resetBtn" data-label="reset" title="Reset All"><i class="fas fa-redo"></i></button>
        </div>
        <div class="info-bar">
            <div class="language-selector">
                <label for="languageSelect">Language:</label>
                <select id="languageSelect" onchange="changeLanguage(this.value)">
                    <option value="python">Python</option>
                    <option value="java">Java</option>
                    <option value="javascript">JavaScript</option>
                    <option value="c++">C++</option>
                    <option value="c#">C#</option>
                    <option value="go">Go</option>
                    <option value="rust">Rust</option>
                    <option value="ruby">Ruby</option>
                    <option value="mcq">Mcq</option>
                </select>
            </div>
            <div class="screenshot-count"><i class="fas fa-camera"></i> <span id="screenshotCount">0</span> screenshots</div>
        </div>
        
        <!-- File Selection Section -->
        <div class="file-selection-section" id="fileSelectionSection">
            <div class="section-header">
                <i class="fas fa-file-alt"></i> Selected Files for Analysis
                <button class="btn-small" onclick="clearAllFiles()" title="Clear all selections"><i class="fas fa-times"></i></button>
            </div>
            <div class="available-files-list" id="availableFilesList">
                <!-- Dynamic file list will be populated here -->
            </div>
        </div>
        
        <div class="status-bar" id="statusBar">Ready</div>
        <div class="loading-spinner" id="loadingSpinner"></div>
        <div class="results-container" id="resultsContainer" style="display: none;">
            <div class="result-section" id="bruteSection" style="display: none;">
                <div class="section-header brute-header"><i class="fas fa-lightbulb"></i> Initial Solution</div>
                <div class="explanation" id="bruteExplanation"></div>
                <pre class="code-block language-python"><code id="bruteCode"></code></pre>
                <div class="complexity-info">
                    <div class="complexity-item"><i class="fas fa-clock"></i> Time: <span id="bruteTimeComplexity">-</span></div>
                    <div class="complexity-item"><i class="fas fa-memory"></i> Space: <span id="bruteSpaceComplexity">-</span></div>
                </div>
            </div>
            <div class="result-section" id="optimizedSection" style="display: none;">
                <div class="section-header optimized-header"><i class="fas fa-rocket"></i> Optimized Solution</div>
                <div class="explanation" id="optimizedExplanation"></div>
                <pre class="code-block language-python"><code id="optimizedCode"></code></pre>
                <div class="complexity-info">
                    <div class="complexity-item"><i class="fas fa-clock"></i> Time: <span id="optimizedTimeComplexity">-</span></div>
                    <div class="complexity-item"><i class="fas fa-memory"></i> Space: <span id="optimizedSpaceComplexity">-</span></div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
    <script>
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
        setInterval(updateScreenshotCount, 5000);
        setInterval(updateLanguageDropdown, 10000); // Update language every 10 seconds
    </script>
</body>
</html>
    """
