from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)

from . import deps
from . import models as m
from .manager import MANAGERS, ChessManager, Mode

api_v1 = APIRouter(prefix='/api/v1', tags=['v1'])


@api_v1.websocket('/games/{chess_id}/ws')
async def game_ws(
    chess_id: str,
    ws: WebSocket,
    mode: Mode = 'json',
    user: m.User | None = Depends(deps.get_current_user),
):
    if chess_id in MANAGERS:
        manager = MANAGERS[chess_id]
    else:
        manager = ChessManager(chess_id)
        MANAGERS[chess_id] = manager

    await manager.connect(ws, user, mode)
    try:
        while True:
            data = await ws.receive_json()
            await manager.move(ws, user, data)
    except WebSocketDisconnect:
        await manager.disconnect(ws)
