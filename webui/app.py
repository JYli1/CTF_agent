"""
Flask Web 应用主入口
"""
from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from webui.api.agent import agent_bp
from webui.api.config import config_bp
from webui.api.rag import rag_bp
from webui.api.skills import skills_bp
from webui.websocket_handler import WebSocketHandler
from webui.session_manager import session_manager
import os
from threading import Thread
import time


def create_app():
    """创建 Flask 应用"""
    app = Flask(__name__,
                static_folder='static',
                static_url_path='')

    # 配置
    app.config['SECRET_KEY'] = 'ctf-agent-secret-key-change-in-production'

    # 启用 CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 注册蓝图
    app.register_blueprint(agent_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(rag_bp)
    app.register_blueprint(skills_bp)

    # 静态文件路由
    @app.route('/')
    def index():
        """主页"""
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        index_file = os.path.join(static_dir, 'index.html')

        if os.path.exists(index_file):
            return send_from_directory(static_dir, 'index.html')
        else:
            return '''
            <html>
            <head><title>CTF Agent Web UI</title></head>
            <body>
                <h1>CTF Agent Web UI</h1>
                <p>前端文件尚未部署。请将前端文件放置在 webui/static/ 目录下。</p>
                <h2>API 端点</h2>
                <ul>
                    <li>POST /api/agent/init - 初始化会话</li>
                    <li>POST /api/agent/set-target - 设置目标</li>
                    <li>POST /api/agent/step - 执行分析</li>
                    <li>GET /api/agent/status - 获取状态</li>
                    <li>GET /api/config/get - 获取配置</li>
                    <li>POST /api/rag/sync - 同步知识库</li>
                    <li>GET /api/skills/list - 列出技能</li>
                </ul>
            </body>
            </html>
            '''

    return app


def cleanup_sessions():
    """定期清理过期会话"""
    while True:
        time.sleep(300)  # 每 5 分钟清理一次
        session_manager.cleanup_expired()


def run_web_server(host='0.0.0.0', port=5000, debug=False):
    """
    启动 Web 服务器

    Args:
        host: 监听地址
        port: 监听端口
        debug: 是否启用调试模式
    """
    print(f"\n[启动] 正在初始化 Flask 应用...")
    app = create_app()
    print(f"[启动] Flask 应用创建完成")

    # 初始化 SocketIO
    print(f"[启动] 正在初始化 SocketIO...")
    socketio = SocketIO(app, cors_allowed_origins="*")
    print(f"[启动] SocketIO 初始化完成")

    print(f"[启动] SocketIO 初始化完成")

    # 注册 WebSocket 处理器
    print(f"[启动] 正在注册 WebSocket 处理器...")
    ws_handler = WebSocketHandler(socketio)
    print(f"[启动] WebSocket 处理器注册完成")

    # 启动会话清理线程
    print(f"[启动] 正在启动会话清理线程...")
    cleanup_thread = Thread(target=cleanup_sessions, daemon=True)
    cleanup_thread.start()
    print(f"[启动] 会话清理线程已启动")

    print(f"\n{'='*60}")
    print(f"CTF Agent Web UI 已启动")
    print(f"{'='*60}")
    print(f"访问地址: http://{host}:{port}")
    print(f"API 文档: http://{host}:{port}/api")
    print(f"{'='*60}\n")

    # 启动服务器
    print(f"[启动] 正在启动 Flask 服务器...")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    run_web_server(debug=True)
