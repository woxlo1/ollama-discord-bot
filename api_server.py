"""
FastAPI server to bridge Minecraft plugin and Discord Ollama Bot.
"""

import asyncio
import logging
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Minecraft-Ollama Bridge API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Data Models =====
class ChatRequest(BaseModel):
    player: str
    message: str
    use_memory: bool = True


class ChatResponse(BaseModel):
    player: str
    response: str
    success: bool


class BroadcastRequest(BaseModel):
    message: str
    channel_id: Optional[int] = None


class PlayerInfo(BaseModel):
    name: str
    uuid: str
    location: Dict[str, float]
    health: float
    gamemode: str


# ===== In-memory storage =====
class BridgeState:
    def __init__(self):
        self.discord_bot = None  # Will be injected
        self.active_connections: List[WebSocket] = []
        self.player_contexts: Dict[str, List[Dict]] = {}  # player -> conversation
        self.minecraft_players: Dict[str, PlayerInfo] = {}  # player -> info

    def add_connection(self, websocket: WebSocket):
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def remove_connection(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast_to_minecraft(self, message: dict):
        """Send message to all connected Minecraft servers."""
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to WebSocket: {e}")
                dead_connections.append(connection)

        # Clean up dead connections
        for conn in dead_connections:
            self.remove_connection(conn)


state = BridgeState()


# ===== REST Endpoints =====
@app.get("/")
async def root():
    return {
        "service": "Minecraft-Ollama Bridge",
        "version": "1.0.0",
        "connected_servers": len(state.active_connections),
        "tracked_players": len(state.minecraft_players),
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle chat from Minecraft player.
    """
    try:
        # This would integrate with your Ollama Bot
        # For now, we'll use a direct Ollama client
        from bot.ollama_client import OllamaClient
        from config import Config

        ollama = OllamaClient(
            host=Config.OLLAMA_HOST, model=Config.OLLAMA_MODEL, timeout=Config.REQUEST_TIMEOUT
        )

        # Add context if memory enabled
        if request.use_memory and request.player in state.player_contexts:
            context = state.player_contexts[request.player][-3:]  # Last 3 messages
            context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context])
            prompt = f"過去の会話:\n{context_str}\n\n新しい質問: {request.message}"
        else:
            prompt = request.message

        # Generate response
        response = await asyncio.to_thread(ollama.generate, prompt)

        # Save to memory
        if request.use_memory:
            if request.player not in state.player_contexts:
                state.player_contexts[request.player] = []

            state.player_contexts[request.player].append(
                {"role": "user", "content": request.message}
            )
            state.player_contexts[request.player].append({"role": "assistant", "content": response})

            # Keep only last 10 messages
            if len(state.player_contexts[request.player]) > 10:
                state.player_contexts[request.player] = state.player_contexts[request.player][-10:]

        return ChatResponse(player=request.player, response=response, success=True)

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/broadcast")
async def broadcast_to_discord(request: BroadcastRequest):
    """
    Broadcast a message from Minecraft to Discord.
    """
    # This would send to Discord bot
    logger.info(f"Broadcasting to Discord: {request.message}")

    # Send to all WebSocket clients
    await state.broadcast_to_minecraft({"type": "server_broadcast", "message": request.message})

    return {"success": True}


@app.post("/player/update")
async def update_player_info(player_info: PlayerInfo):
    """
    Update player information from Minecraft.
    """
    state.minecraft_players[player_info.name] = player_info
    logger.info(f"Updated player info: {player_info.name}")
    return {"success": True}


@app.get("/player/{player_name}")
async def get_player_info(player_name: str):
    """
    Get player information.
    """
    if player_name not in state.minecraft_players:
        raise HTTPException(status_code=404, detail="Player not found")

    return state.minecraft_players[player_name]


@app.delete("/memory/{player_name}")
async def clear_player_memory(player_name: str):
    """
    Clear conversation memory for a player.
    """
    if player_name in state.player_contexts:
        del state.player_contexts[player_name]

    return {"success": True, "message": f"Memory cleared for {player_name}"}


# ===== WebSocket for real-time communication =====
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for Minecraft plugin.
    """
    await websocket.accept()
    state.add_connection(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "chat":
                # Handle chat message
                player = data.get("player")
                message = data.get("message")

                # Generate response (same as REST)
                from bot.ollama_client import OllamaClient
                from config import Config

                ollama = OllamaClient(
                    host=Config.OLLAMA_HOST,
                    model=Config.OLLAMA_MODEL,
                    timeout=Config.REQUEST_TIMEOUT,
                )

                response = await asyncio.to_thread(ollama.generate, message)

                # Send back response
                await websocket.send_json(
                    {"type": "chat_response", "player": player, "response": response}
                )

            elif event_type == "player_join":
                logger.info(f"Player joined: {data.get('player')}")
                await state.broadcast_to_minecraft(
                    {"type": "player_event", "event": "join", "player": data.get("player")}
                )

            elif event_type == "player_leave":
                logger.info(f"Player left: {data.get('player')}")
                await state.broadcast_to_minecraft(
                    {"type": "player_event", "event": "leave", "player": data.get("player")}
                )

    except WebSocketDisconnect:
        state.remove_connection(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        state.remove_connection(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
