# GitHub Markdown Downloader

A FastAPI server that allows users to download markdown files from GitHub repositories.

## Features

- Web interface for easy use
- API endpoints for programmatic access
- Downloads all markdown (.md) files from a GitHub repository
- Preserves the directory structure of the repository
- Creates a ZIP file for easy download
- Supports both public and private repositories (with token)
- Handles cleanup of temporary files automatically

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd github-md-downloader
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure GitHub token (to avoid API rate limits):
   ```bash
   # Copy the example .env file
   cp .env.example .env

   # Edit the .env file and add your GitHub token
   # Replace 'your_github_token_here' with your actual token
   ```

## Usage

### Starting the Server

Run the server with:

```bash
uvicorn github_md_downloader_server:app --reload --host 0.0.0.0 --port 8000
```

Then open your browser and navigate to `http://localhost:8000/` to access the web interface.

### API Endpoints

- `GET /`: Web interface
- `GET /api/info`: Basic API information
- `POST /download/`: Download markdown files from a GitHub repository
- `GET /download/{download_id}`: Download the ZIP file for a previously processed repository

### Using the API Programmatically

Example using curl:

```bash
curl -X POST "http://localhost:8000/download/" \
     -H "Content-Type: application/json" \
     -d '{"repo_url": "https://github.com/username/repository", "token": "your_github_token"}'
```

Example using Python requests:

```python
import requests

response = requests.post(
    "http://localhost:8000/download/",
    json={
        "repo_url": "https://github.com/username/repository",
        "token": "your_github_token"  # Optional, for private repositories
    }
)

data = response.json()
print(data)

# Download the ZIP file
if data["download_url"]:
    download_response = requests.get(f"http://localhost:8000{data['download_url']}")
    with open("markdown_files.zip", "wb") as f:
        f.write(download_response.content)
```

## API Documentation

FastAPI automatically generates API documentation. Access it at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT