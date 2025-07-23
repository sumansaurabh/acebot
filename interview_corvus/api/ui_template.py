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
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 6px;
            margin-bottom: 28px;
            max-width: 280px;
            margin-left: auto;
            margin-right: auto;
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
            min-height: 40px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 6px rgba(0,0,0,0.12);
            display: flex;
            align-items: center;
            justify-content: center;
            aspect-ratio: 1;
            position: relative;
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
        .clear-btn { background: #ef4444; color: white; }
        .clear-btn:hover { background: #dc2626; transform: translateY(-2px); }
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
        }
        .explanation h1, .explanation h2, .explanation h3 {
            color: #24292e;
            margin-top: 16px;
            margin-bottom: 8px;
        }
        .explanation h1 { font-size: 18px; }
        .explanation h2 { font-size: 16px; }
        .explanation h3 { font-size: 14px; }
        .explanation p { margin: 8px 0; }
        .explanation ul, .explanation ol { margin: 8px 0 8px 20px; }
        .explanation li { margin: 4px 0; }
        .explanation code {
            background: #f6f8fa;
            border: 1px solid #e1e4e8;
            border-radius: 3px;
            padding: 2px 4px;
            font-size: 13px;
            font-family: Monaco, "Cascadia Code", "Fira Code", monospace;
        }
        .explanation blockquote {
            border-left: 4px solid #dfe2e5;
            padding-left: 16px;
            margin-left: 0;
            color: #6a737d;
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
        @media (max-width: 600px) {
            .main-content { padding: 8px 16px 0 16px; }
            .action-buttons { gap: 4px; max-width: 240px; margin-bottom: 24px; }
            .action-btn { font-size: 18px; min-height: 36px; padding: 6px; }
            .action-btn::after { font-size: 8px; bottom: -14px; }
            .info-bar { gap: 12px; margin: 20px 0 16px 0; }
            .language-selector label { font-size: 11px; }
            .language-selector select { font-size: 11px; padding: 3px 6px; min-width: 80px; }
            .screenshot-count { font-size: 11px; padding: 5px 10px; }
            .explanation { font-size: 12px; }
            .explanation h1 { font-size: 15px; }
            .explanation h2 { font-size: 14px; }
            .explanation h3 { font-size: 13px; }
            .explanation code { font-size: 11px; }
            .code-block { font-size: 11px; padding: 10px !important; }
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
            <button class="action-btn clear-btn" onclick="clearScreenshots()" id="clearBtn" data-label="clear" title="Clear Screenshots"><i class="fas fa-trash"></i></button>
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
        let isWindowOpen = true; // Track toggle state, default is open
        
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
                .catch(() => { document.getElementById('screenshotCount').textContent = '0'; });
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
            updateStatus('Recording...'); showLoading(true);
            try {
                const response = await fetch(`${API_BASE}/screen/record`, { method: 'POST' });
                const result = await response.json();
                if (response.ok) {
                    updateStatus('Recording started');
                } else updateStatus('Error: ' + result.message);
            } catch (error) { updateStatus('Recording failed'); }
            finally { showLoading(false); }
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
            
            // Render syntax-highlighted code
            document.getElementById('bruteCode').textContent = solution.code || '';
            Prism.highlightElement(document.getElementById('bruteCode'));
            
            document.getElementById('bruteTimeComplexity').textContent = solution.time_complexity || '-';
            document.getElementById('bruteSpaceComplexity').textContent = solution.space_complexity || '-';
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
        window.addEventListener('load', () => {
            document.getElementById('solveBtn').disabled = true;
            document.getElementById('optimizeBtn').disabled = true;
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
