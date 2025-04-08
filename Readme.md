# MemorieDen

## Description

MemorieDen is a memory management system designed for AI applications that provides persistent storage and retrieval of conversational memories. The project implements a flexible memory architecture with text-based search capabilities, allowing AI agents and users to store, retrieve, and update conversational contexts, facts, and other text-based information.

The system features traditional text search using SQLite FTS5, making it powerful for context-aware AI applications, personal knowledge management, and systems that need to maintain conversation history.

## Features

- **Modern Web Interface** - Intuitive, responsive web UI for managing memories and users
  - Real-time memory creation and editing
  - Interactive search with highlighted results
  - Memory history viewing
  - User management interface
  - Resizable text areas for comfortable editing
  - Proper line break preservation in content
- **Memory Storage** - Store text-based memories with optional metadata
- **Memory Retrieval** - Efficient text search capabilities:
  - Full-text search with SQLite FTS5 for fast keyword searches
  - Filter by user or other metadata
  - Relevance scoring for search results
- **Memory History** - Track and retrieve the history of memory changes over time
- **User Management** - Organize memories by users
- **Rich Metadata** - Add arbitrary JSON metadata to memories for custom organization
- **API-First Design** - RESTful interface for easy integration

## Components

- **Server** - Flask implementation with full text search support
- **Web Interface** - Modern, responsive web interface built with Bootstrap
- **API Demo Client** - Command-line interface demonstrating API usage

## Technical Details

- Built with Python, SQLAlchemy, and Flask
- Uses SQLite for storage with FTS5 extension for full-text search
- Modern web interface using Bootstrap 5
- Lightweight and easy to deploy

## Getting Started

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/Coriana/MemorieDen.git
   cd MemorieDen
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Server

Start the Flask server:
```
cd Server
python app.py
```

Once started, open your web browser and navigate to:
```
http://localhost:5000
```

The web interface provides an intuitive way to:
- Create and manage users
- Add and edit memories
- Search through memories with highlighted results
- View memory history
- Add JSON metadata to memories

### API Reference Demo

The `client.py` script serves as a reference implementation demonstrating how to interact with the MemorieDen API programmatically:

```
python client.py
```

This demo client showcases:
- API endpoint usage patterns
- Request/response formats
- Error handling
- Authentication flow (when implemented)

## Use Cases

- **AI Agent Memory** - Provide long-term memory for chatbots and conversational agents
- **Personal Knowledge Management** - Store and retrieve personal notes with text search
- **Contextual AI Applications** - Add memory capabilities to any AI application
- **Customer Support Knowledge Base** - Store and search support interactions
- **Research Notes Archive** - Maintain searchable research notes with metadata
- **Meeting Minutes Repository** - Store and search meeting transcripts
- **Code Snippet Library** - Maintain searchable code examples with metadata

## Project Structure

```
MemorieDen/
├── requirements.txt         # Python dependencies
├── client.py               # API reference implementation
└── Server/                 # Flask implementation
    ├── app.py              # Flask API endpoints
    ├── models.py           # SQLAlchemy database models
    ├── database.py         # Database connection setup
    ├── initialize_db.py    # Database initialization
    ├── static/             # Web interface assets
    │   ├── script.js       # Frontend JavaScript
    │   └── style.css       # Custom styling
    └── templates/          # HTML templates
        └── index.html      # Main web interface
```

## API Reference

The API provides endpoints for memory and user management:

### Memory Endpoints
- `POST /memories/add` - Add a new memory
- `PUT /memories/update` - Update an existing memory
- `GET /memories/search` - Search memories by text
- `GET /memories/all` - Retrieve all memories
- `GET /memories/history/{memory_id}` - Get history of a memory

### User Endpoints
- `POST /users/add` - Add a new user
- `GET /users/search` - Search for users
- `GET /users/all` - List all users

See `client.py` for detailed examples of how to use these endpoints in your applications.

## Future Enhancements

- Semantic search using vector embeddings
- Memory importance scoring and prioritization
- Memory summarization capabilities
- Session-based memory organization
- User authentication and access control
- Real-time collaborative editing
- Export/import functionality

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- SQLite FTS5 for full-text search capabilities
- Bootstrap 5 for the web interface
- Flask for the backend framework