# Discord MCP Server with HTTP Interface

This project provides a Discord MCP (Multi-Client Protocol) server with both a Discord bot interface and an HTTP API for interacting with Discord.

## Features

- Discord bot functionality
- HTTP REST API for Discord operations
- WebSocket support for streaming responses
- Comprehensive Discord operations:
  - Send messages
  - Read messages
  - Get user information
  - List servers
  - Create text channels
  - Delete channels
  - Add/remove reactions

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your Discord bot token:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   ```

## Usage

### Running the Server

To run both the Discord bot and HTTP server:

```bash
python start_server.py
```

The HTTP server will start on `http://localhost:8080`.

### HTTP API Endpoints

#### Health Check
- `GET /health` - Check server health

#### Send Message
- `POST /send_message`
- Body: `{"channel_id": 123456789, "content": "Hello, world!"}`

#### Read Messages
- `POST /read_messages`
- Body: `{"channel_id": 123456789, "limit": 10}`

#### Get User Info
- `POST /get_user_info`
- Body: `{"user_id": 987654321}`

#### List Servers
- `POST /list_servers`
- Body: `{}`

#### Create Text Channel
- `POST /create_text_channel`
- Body: `{"server_id": 123456789, "name": "new-channel", "category_id": 987654321}`

#### Delete Channel
- `POST /delete_channel`
- Body: `{"channel_id": 123456789}`

#### Add Reaction
- `POST /add_reaction`
- Body: `{"channel_id": 123456789, "message_id": 456789123, "emoji": "👍"}`

#### Remove Reaction
- `POST /remove_reaction`
- Body: `{"channel_id": 123456789, "message_id": 456789123, "emoji": "👍"}`

### WebSocket Support

The server also supports WebSocket connections at `ws://localhost:8080/ws` for streaming responses.

To start with WebSocket support:
```bash
python http_mcp_server.py --websocket
```

## Architecture

- `main.py` - Contains the core DiscordMCP class with Discord operations
- `http_mcp_server.py` - Implements the HTTP API layer on top of DiscordMCP
- `start_server.py` - Starts both Discord bot and HTTP server together
- `test_http_mcp.py` - Basic test script for the HTTP server