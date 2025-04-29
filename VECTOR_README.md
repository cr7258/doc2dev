# Markdown Embedding and Vector Storage

This project provides tools to download Markdown files from GitHub repositories, embed them using DashScope embeddings, and store the vectors in OceanBase for semantic search.

## Prerequisites

1. Python 3.8 or higher
2. OceanBase database
3. DashScope API key

## Installation

1. Install the required dependencies:

```bash
uv add langchain-community langchain-oceanbase langchain-text-splitters python-dotenv
```

2. Set up environment variables:

Create a `.env` file with the following content:

```
DASHSCOPE_API_KEY=your_dashscope_api_key
GITHUB_TOKEN=your_github_token
```

## Usage

### 1. Download Markdown Files

Use the FastAPI server to download Markdown files from a GitHub repository:

```bash
python main.py
```

Then open your browser at http://localhost:8000 and enter the GitHub repository URL (e.g., https://github.com/cr7258/elasticsearch-mcp-server).

### 2. Embed and Store Documents

After downloading the Markdown files, use the `embed_and_store.py` script to embed them and store the vectors in OceanBase:

```bash
python embed_and_store.py elasticsearch-mcp-server_md_files --chunk-size 1000 --chunk-overlap 200 --table-name elasticsearch_docs --drop-old
```

Options:
- `--chunk-size`: Maximum size of each text chunk (default: 1000)
- `--chunk-overlap`: Overlap between chunks (default: 200)
- `--table-name`: Name of the table to store vectors (default: langchain_vector)
- `--drop-old`: Drop the existing table if it exists
- `--search`: Perform a search after embedding (optional)
- `--k`: Number of search results to return (default: 5)

### 3. Query the Vector Store

Use the `query_oceanbase.py` script to search for documents similar to a query:

```bash
python query_oceanbase.py "How to configure Elasticsearch?" --k 3 --table-name elasticsearch_docs
```

Options:
- `--k`: Number of results to return (default: 5)
- `--table-name`: Name of the table containing vectors (default: langchain_vector)
- `--filter-source`: Filter results by source (optional)

## OceanBase Configuration

The default OceanBase connection settings are:

```python
connection_args = {
    "host": "127.0.0.1",
    "port": "2881",
    "user": "root@test",
    "password": "admin",
    "db_name": "doc2dev",
}
```

You can modify these settings in the scripts if needed.

## Troubleshooting

### Dependency Conflicts

If you encounter dependency conflicts when installing `langchain-oceanbase`, try using the `--frozen` flag:

```bash
uv add langchain-oceanbase --frozen
```

Or install a specific version of numpy that's compatible:

```bash
uv add numpy==1.26.0
uv add langchain-oceanbase
```

### OceanBase Connection Issues

Make sure your OceanBase instance is running and accessible. You can test the connection using:

```python
import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=2881,
    user="root@test",
    password="admin",
    database="test"
)
print("Connection successful!")
conn.close()
```

## License

MIT
