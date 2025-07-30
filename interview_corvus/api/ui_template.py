"""
HTML template for the AceBot web UI.
Now serves static files for better maintainability.
"""

import os

def get_main_ui_template() -> str:
    """Get the main web UI HTML template."""
    # Path to the static HTML file
    static_dir = os.path.dirname(__file__)
    html_path = os.path.join(static_dir, 'static', 'index.html')
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to embedded HTML if static file not found
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AceBot</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet" />
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
    <link rel="stylesheet" href="/static/styles.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/marked/4.3.0/marked.min.js"></script>
</head>
<body>
    <div class="main-content">
        <h1>AceBot - Static files not found</h1>
        <p>Please ensure the static files are properly configured.</p>
    </div>
    <script src="/static/app.js"></script>
</body>
</html>
        """
