"""
WebSocket 事件处理器
"""
from flask_socketio import emit, join_room, leave_room


class WebSocketHandler:
    """WebSocket 事件处理器"""

    def __init__(self, socketio):
        self.socketio = socketio
        self.register_handlers()

    def register_handlers(self):
        """注册 WebSocket 事件处理器"""

        @self.socketio.on('join')
        def handle_join(data):
            """客户端加入会话房间"""
            session_id = data.get('session_id')
            if session_id:
                join_room(session_id)
                emit('connected', {'message': f'已连接到会话 {session_id}'})

        @self.socketio.on('leave')
        def handle_leave(data):
            """客户端离开会话房间"""
            session_id = data.get('session_id')
            if session_id:
                leave_room(session_id)
                emit('disconnected', {'message': f'已断开会话 {session_id}'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            """客户端断开连接"""
            pass

    def broadcast_event(self, session_id: str, event_type: str, data: dict):
        """
        向指定会话广播事件

        Args:
            session_id: 会话 ID
            event_type: 事件类型
            data: 事件数据
        """
        self.socketio.emit(event_type, data, room=session_id)


def create_event_callback(socketio, session_id: str):
    """
    创建事件回调函数（用于 Agent）

    Args:
        socketio: SocketIO 实例
        session_id: 会话 ID

    Returns:
        回调函数
    """
    def callback(event_type: str, data: dict):
        """事件回调"""
        socketio.emit(event_type, data, room=session_id)

    return callback
