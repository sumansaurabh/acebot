# Interview Corvus Web API

Interview Corvus now includes a built-in web API server that provides all the core functionality through HTTP endpoints. Both the GUI application and web API can run together and share the same services.

## 🚀 Quick Start

### Starting the GUI with Web Server

1. **Launch the GUI Application:**
   ```bash
   cd interview-corvus
   poetry run python -m interview_corvus
   ```

2. **Enable Web Server:**
   - In the GUI, click the "Start Web Server" button
   - Or check "Start Web Server on Launch" in settings for automatic startup

3. **Access the API:**
   - **API Base URL:** `http://127.0.0.1:8000`
   - **Interactive Docs:** `http://127.0.0.1:8000/docs`
   - **OpenAPI Spec:** `http://127.0.0.1:8000/openapi.json`

### Standalone Web Server (Optional)

For headless operation without GUI:
```bash
poetry run python api_server.py
```

## 📡 API Endpoints

### Health & Status
- `GET /health` - Check API health and GUI connection status

### Screenshot Management
- `GET /screenshots` - List available screenshots
- `POST /screenshot/capture` - Trigger screenshot in GUI (requires GUI)
- `DELETE /screenshots` - Clear all screenshots

### Solution Generation
- `POST /solution` - Generate solution from base64-encoded images
- `POST /upload-solution` - Upload image files and generate solution

### Code Optimization
- `POST /optimize` - Optimize provided code

### Data Management
- `DELETE /history` - Reset chat history and screenshots

## 🔧 Usage Examples

### Using the Demo Client

Run the included demo client:
```bash
python client_demo.py
```

### Using curl

**Health Check:**
```bash
curl http://127.0.0.1:8000/health
```

**List Screenshots:**
```bash
curl http://127.0.0.1:8000/screenshots
```

**Upload and Solve:**
```bash
curl -X POST "http://127.0.0.1:8000/upload-solution" \
     -F "files=@problem.png" \
     -F "language=Python"
```

**Optimize Code:**
```bash
curl -X POST "http://127.0.0.1:8000/optimize" \
     -H "Content-Type: application/json" \
     -d '{
       "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
       "language": "Python"
     }'
```

### Using Python requests

```python
import requests
import base64

# Health check
response = requests.get("http://127.0.0.1:8000/health")
print(response.json())

# Upload image and get solution
with open("problem.png", "rb") as f:
    files = {"files": ("problem.png", f, "image/png")}
    data = {"language": "Python"}
    response = requests.post(
        "http://127.0.0.1:8000/upload-solution",
        files=files,
        data=data
    )
    print(response.json())

# Optimize code
code = """
def slow_function(n):
    result = []
    for i in range(n):
        result.append(i * 2)
    return result
"""

response = requests.post(
    "http://127.0.0.1:8000/optimize",
    json={"code": code, "language": "Python"}
)
print(response.json())
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

const API_BASE = 'http://127.0.0.1:8000';

// Health check
async function healthCheck() {
    try {
        const response = await axios.get(`${API_BASE}/health`);
        console.log(response.data);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Upload and solve
async function uploadAndSolve(imagePath, language = 'Python') {
    try {
        const formData = new FormData();
        formData.append('files', fs.createReadStream(imagePath));
        formData.append('language', language);
        
        const response = await axios.post(`${API_BASE}/upload-solution`, formData, {
            headers: formData.getHeaders()
        });
        
        console.log(response.data);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Optimize code
async function optimizeCode(code, language = 'Python') {
    try {
        const response = await axios.post(`${API_BASE}/optimize`, {
            code: code,
            language: language
        });
        
        console.log(response.data);
    } catch (error) {
        console.error('Error:', error.message);
    }
}
```

## 📊 API Response Format

All endpoints return JSON responses with the following structure:

### Success Response
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {
        // Response data here
    }
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error description",
    "details": "Additional error details"
}
```

### Solution Response
```json
{
    "success": true,
    "solution": {
        "problem_description": "Detected problem description",
        "algorithm": "Algorithm explanation", 
        "code": "Generated code solution",
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "explanation": "Detailed explanation"
    }
}
```

### Optimization Response
```json
{
    "success": true,
    "optimization": {
        "original_code": "Original code",
        "optimized_code": "Optimized code",
        "improvements": ["List of improvements"],
        "original_time_complexity": "O(n²)",
        "optimized_time_complexity": "O(n)",
        "performance_gain": "50% improvement"
    }
}
```

## 🔧 Configuration

### Web Server Settings

The web server can be configured through the GUI settings:

- **Auto-start:** Start web server when GUI launches
- **Port:** Default is 8000
- **Host:** Default is 127.0.0.1 (localhost)

### Environment Variables

- `CORVUS_API_PORT`: Override default port (8000)
- `CORVUS_API_HOST`: Override default host (127.0.0.1)

## 🔐 Security Considerations

- The API runs on localhost by default (127.0.0.1)
- No authentication is currently implemented
- CORS is enabled for browser access
- For production use, consider:
  - Adding authentication
  - Using HTTPS
  - Restricting CORS origins
  - Rate limiting

## 🚀 Integration Examples

### CI/CD Pipeline Integration

```yaml
# GitHub Actions example
name: Interview Problem Solver
on: [push]

jobs:
  solve-problems:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
          
      - name: Install Interview Corvus
        run: |
          pip install interview-corvus
          
      - name: Start API Server
        run: |
          interview-corvus-api &
          sleep 5
          
      - name: Solve Problems
        run: |
          curl -X POST "http://127.0.0.1:8000/upload-solution" \
               -F "files=@problems/problem1.png" \
               -F "language=Python" > solution1.json
```

### Web Integration

```html
<!DOCTYPE html>
<html>
<head>
    <title>Interview Corvus Web Interface</title>
</head>
<body>
    <div id="app">
        <h1>Interview Problem Solver</h1>
        
        <input type="file" id="imageInput" accept="image/*" multiple>
        <select id="languageSelect">
            <option value="Python">Python</option>
            <option value="JavaScript">JavaScript</option>
            <option value="Java">Java</option>
            <option value="C++">C++</option>
        </select>
        <button onclick="solveProblem()">Solve Problem</button>
        
        <div id="result"></div>
    </div>
    
    <script>
    async function solveProblem() {
        const fileInput = document.getElementById('imageInput');
        const languageSelect = document.getElementById('languageSelect');
        const resultDiv = document.getElementById('result');
        
        if (fileInput.files.length === 0) {
            alert('Please select an image file');
            return;
        }
        
        const formData = new FormData();
        for (let file of fileInput.files) {
            formData.append('files', file);
        }
        formData.append('language', languageSelect.value);
        
        try {
            const response = await fetch('http://127.0.0.1:8000/upload-solution', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                resultDiv.innerHTML = `
                    <h3>Solution:</h3>
                    <pre>${result.solution.code}</pre>
                    <p><strong>Time Complexity:</strong> ${result.solution.time_complexity}</p>
                    <p><strong>Explanation:</strong> ${result.solution.explanation}</p>
                `;
            } else {
                resultDiv.innerHTML = `<p>Error: ${result.error}</p>`;
            }
        } catch (error) {
            resultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
        }
    }
    </script>
</body>
</html>
```

## 🛠️ Development

### Running in Development Mode

```bash
# Start with auto-reload
uvicorn interview_corvus.api.web_server:app --reload --port 8000

# Or run the standalone server
python api_server.py
```

### Testing the API

```bash
# Run the demo client
python client_demo.py

# Test specific endpoints
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/docs
```

## 📖 API Documentation

Visit `http://127.0.0.1:8000/docs` when the server is running for interactive API documentation powered by Swagger UI.

The documentation includes:
- Detailed endpoint descriptions
- Request/response schemas
- Interactive testing interface
- Code examples in multiple languages

## 🤝 Contributing

When contributing to the web API:

1. Follow the existing code structure
2. Add appropriate error handling
3. Update this documentation
4. Test all endpoints thoroughly
5. Ensure GUI integration works properly

## 📝 License

Same as the main Interview Corvus project.
