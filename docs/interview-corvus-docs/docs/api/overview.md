---
sidebar_position: 1
---

# Web API Overview

Interview Corvus includes a built-in web API server that provides all core functionality through HTTP endpoints. Use it for automation, integration, or building custom interfaces.

## Quick Start

### Starting the Web Server

**From the GUI Application:**
1. Launch Interview Corvus
2. Click the **"Start Web Server"** button
3. Server starts on `http://127.0.0.1:8000`

**Auto-start on Launch:**
1. Open Settings
2. Navigate to Web Server tab
3. Check "Start Web Server on Launch"
4. Server starts automatically when app launches

**Standalone Mode (No GUI):**
```bash
cd interview-corvus
poetry run python api_server.py
```

### Verify Server is Running

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "gui_connected": true,
  "version": "0.2.3"
}
```

## API Documentation

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **OpenAPI JSON**: `http://127.0.0.1:8000/openapi.json`

The interactive docs include:
- All available endpoints
- Request/response schemas
- Try-it-out functionality
- Code examples in multiple languages

## Core Endpoints

### Health Check

Check server status and GUI connection:

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "gui_connected": true,
  "version": "0.2.3",
  "uptime_seconds": 3600
}
```

### Generate Solution

Upload image(s) and generate a coding solution:

```bash
POST /upload-solution
```

**Parameters:**
- `files`: Image file(s) (multipart/form-data)
- `language`: Programming language (Python, JavaScript, etc.)

**Example:**
```bash
curl -X POST "http://127.0.0.1:8000/upload-solution" \
     -F "files=@problem.png" \
     -F "language=Python"
```

**Response:**
```json
{
  "success": true,
  "solution": {
    "problem_description": "Find two numbers that sum to target",
    "algorithm": "Use hash map for O(n) lookup",
    "code": "def two_sum(nums, target):\n    ...",
    "time_complexity": "O(n)",
    "space_complexity": "O(n)",
    "explanation": "Detailed walkthrough..."
  }
}
```

### Optimize Code

Get optimization suggestions for existing code:

```bash
POST /optimize
```

**Request Body:**
```json
{
  "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
  "language": "Python"
}
```

**Response:**
```json
{
  "success": true,
  "optimization": {
    "original_code": "...",
    "optimized_code": "...",
    "improvements": [
      "Reduced time complexity from O(2^n) to O(n)",
      "Added memoization",
      "Improved space efficiency"
    ],
    "original_time_complexity": "O(2^n)",
    "optimized_time_complexity": "O(n)",
    "performance_gain": "Exponential improvement"
  }
}
```

### Screenshot Management

**List Screenshots:**
```bash
GET /screenshots
```

**Capture Screenshot (GUI required):**
```bash
POST /screenshot/capture
```

**Clear Screenshots:**
```bash
DELETE /screenshots
```

### History Management

**Reset History:**
```bash
DELETE /history
```

Clears all chat history and screenshots.

## Usage Examples

### Python Client

```python
import requests
import base64

API_BASE = "http://127.0.0.1:8000"

# Health check
def check_health():
    response = requests.get(f"{API_BASE}/health")
    return response.json()

# Upload and solve
def solve_problem(image_path, language="Python"):
    with open(image_path, "rb") as f:
        files = {"files": (image_path, f, "image/png")}
        data = {"language": language}
        response = requests.post(
            f"{API_BASE}/upload-solution",
            files=files,
            data=data
        )
    return response.json()

# Optimize code
def optimize_code(code, language="Python"):
    response = requests.post(
        f"{API_BASE}/optimize",
        json={"code": code, "language": language}
    )
    return response.json()

# Example usage
if __name__ == "__main__":
    # Check if server is running
    health = check_health()
    print(f"Server status: {health['status']}")

    # Solve a problem
    solution = solve_problem("problem.png", "Python")
    if solution["success"]:
        print("Solution:", solution["solution"]["code"])
        print("Complexity:", solution["solution"]["time_complexity"])

    # Optimize code
    code = """
    def find_max(arr):
        max_val = arr[0]
        for num in arr:
            if num > max_val:
                max_val = num
        return max_val
    """
    optimized = optimize_code(code, "Python")
    if optimized["success"]:
        print("Optimized:", optimized["optimization"]["optimized_code"])
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const API_BASE = 'http://127.0.0.1:8000';

// Health check
async function checkHealth() {
    const response = await axios.get(`${API_BASE}/health`);
    return response.data;
}

// Upload and solve
async function solveProblem(imagePath, language = 'Python') {
    const formData = new FormData();
    formData.append('files', fs.createReadStream(imagePath));
    formData.append('language', language);

    const response = await axios.post(
        `${API_BASE}/upload-solution`,
        formData,
        { headers: formData.getHeaders() }
    );

    return response.data;
}

// Optimize code
async function optimizeCode(code, language = 'Python') {
    const response = await axios.post(`${API_BASE}/optimize`, {
        code: code,
        language: language
    });

    return response.data;
}

// Example usage
(async () => {
    // Check health
    const health = await checkHealth();
    console.log('Server status:', health.status);

    // Solve problem
    const solution = await solveProblem('problem.png', 'JavaScript');
    if (solution.success) {
        console.log('Solution:', solution.solution.code);
    }
})();
```

### cURL Examples

**Solve a problem:**
```bash
curl -X POST "http://127.0.0.1:8000/upload-solution" \
     -F "files=@problem1.png" \
     -F "files=@problem2.png" \
     -F "language=Python"
```

**Optimize code:**
```bash
curl -X POST "http://127.0.0.1:8000/optimize" \
     -H "Content-Type: application/json" \
     -d '{
       "code": "def is_prime(n):\n    for i in range(2, n):\n        if n % i == 0:\n            return False\n    return True",
       "language": "Python"
     }'
```

**List screenshots:**
```bash
curl http://127.0.0.1:8000/screenshots
```

**Clear history:**
```bash
curl -X DELETE http://127.0.0.1:8000/history
```

## Configuration

### Server Settings

Configure in Settings → Web Server:

- **Port**: Default `8000`
- **Host**: Default `127.0.0.1` (localhost only)
- **Auto-start**: Start with application
- **CORS**: Enabled for browser access

### Environment Variables

Override defaults with environment variables:

```bash
# Port
export CORVUS_API_PORT=8080

# Host
export CORVUS_API_HOST=127.0.0.1

# Then start the server
poetry run python api_server.py
```

## Response Format

All endpoints return JSON with a consistent structure:

### Success Response

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error type",
  "details": "Detailed error message",
  "code": "ERROR_CODE"
}
```

## Error Handling

### Common Errors

**API Key Not Configured:**
```json
{
  "success": false,
  "error": "API key not configured",
  "details": "Please set your API key in the GUI settings"
}
```

**Invalid Image:**
```json
{
  "success": false,
  "error": "Invalid image file",
  "details": "File format not supported. Use PNG, JPG, or JPEG"
}
```

**Rate Limit Exceeded:**
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "details": "Please wait before making another request"
}
```

### Handling Errors in Code

```python
response = requests.post(url, ...)

if response.status_code == 200:
    data = response.json()
    if data.get("success"):
        # Handle success
        solution = data["solution"]
    else:
        # Handle API error
        print(f"Error: {data.get('error')}")
else:
    # Handle HTTP error
    print(f"HTTP Error: {response.status_code}")
```

## Rate Limiting

The API respects rate limits from:
- OpenAI API limits
- Anthropic API limits
- Local processing constraints

**Best Practices:**
- Space out requests
- Handle rate limit errors gracefully
- Use exponential backoff for retries
- Cache results when possible

## Security

### Current Security Model

- **Localhost only**: Default binding to `127.0.0.1`
- **No authentication**: Suitable for local use only
- **CORS enabled**: Allows browser access

### For Production Use

If exposing the API beyond localhost:

1. **Add authentication** (API keys, OAuth)
2. **Use HTTPS** (TLS/SSL)
3. **Restrict CORS** to specific origins
4. **Implement rate limiting**
5. **Add request validation**
6. **Monitor and log** access
7. **Use firewall rules**

:::warning
The default configuration is for LOCAL USE ONLY. Do not expose the API to the internet without proper security measures.
:::

## Advanced Usage

### Batch Processing

Process multiple problems efficiently:

```python
import concurrent.futures
import requests

def process_problem(problem_file):
    with open(problem_file, 'rb') as f:
        response = requests.post(
            'http://127.0.0.1:8000/upload-solution',
            files={'files': f},
            data={'language': 'Python'}
        )
    return response.json()

# Process in parallel
problems = ['p1.png', 'p2.png', 'p3.png']
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_problem, problems))
```

### Custom Integrations

Integrate with other tools:

- **IDE plugins**: Call API from editor
- **CI/CD pipelines**: Automated problem solving
- **Web interfaces**: Custom UI on top of API
- **Slack/Discord bots**: Team problem solving

## Next Steps

- Review the [Installation Guide](../installation.md)
- Learn about [Usage](../usage/getting-started.md)
- Explore [Customization Options](../customization/overview.md)
