# MemorieDen

## Description

MemorieDen is a memory management system designed for AI applications that provides persistent storage and retrieval of conversational memories. The project implements a flexible memory architecture with text-based search capabilities, allowing AI agents and users to store, retrieve, and update conversational contexts, facts, and other text-based information.

The system features traditional text search using SQLite FTS5, making it powerful for context-aware AI applications, personal knowledge management, and systems that need to maintain conversation history.

## Features

- **Memory Storage** - Store text-based memories with optional metadata
- **Memory Retrieval** - Efficient text search capabilities:
  - Full-text search with SQLite FTS5 for fast keyword searches
  - Filter by user or other metadata
- **Memory History** - Track and retrieve the history of memory changes over time
- **User Management** - Organize memories by users
- **Rich Metadata** - Add arbitrary JSON metadata to memories for custom organization
- **API-First Design** - RESTful interface for easy integration

## Components

- **Server** - Flask implementation with full text search support
- **Client** - Command-line interface for interacting with the memory system

## Technical Details

- Built with Python, SQLAlchemy, and Flask
- Uses SQLite for storage with FTS5 extension for full-text search
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

### Using the Client

The text-based client provides a simple interface to interact with the memory system:

```
python client.py
```

This will display a menu with the following options:
1. Add Memory
2. Update Memory
3. Search Memories
4. Retrieve All Memories 
5. Get Memory History
6. Add User
7. Search Users
8. List All Users
9. Exit

## Use Cases

- **AI Agent Memory** - Provide long-term memory for chatbots and conversational agents
- **Personal Knowledge Management** - Store and retrieve personal notes with text search
- **Contextual AI Applications** - Add memory capabilities to any AI application

## Project Structure

```
MemorieDen/
├── requirements.txt         # Python dependencies
├── client.py               # Command-line interface
└── Server/                 # Flask implementation
    ├── app.py              # Flask API endpoints
    ├── models.py           # SQLAlchemy database models
    ├── database.py         # Database connection setup
    └── initialize_db.py    # Database initialization
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

## Future Enhancements

- Semantic search using vector embeddings
- Memory importance scoring and prioritization
- Memory summarization capabilities
- Session-based memory organization
- Web-based user interface

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- SQLite FTS5 for full-text search capabilities