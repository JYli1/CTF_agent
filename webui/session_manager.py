"""
会话管理器 - 管理多用户的 Agent 实例
"""
import uuid
import time
from typing import Dict, Optional
from threading import Lock
from src.core.agent import CTFAgent
from src.utils.reporter import Reporter


class SessionManager:
    """会话管理器"""

    def __init__(self, session_timeout: int = 1800):
        """
        初始化会话管理器

        Args:
            session_timeout: 会话超时时间（秒），默认 30 分钟
        """
        self.sessions: Dict[str, Dict] = {}
        self.lock = Lock()
        self.session_timeout = session_timeout

    def create_session(self, event_callback=None) -> str:
        """
        创建新会话

        Args:
            event_callback: 事件回调函数（用于 WebSocket 推送）

        Returns:
            session_id: 会话 ID
        """
        session_id = str(uuid.uuid4())
        print(f"[会话管理] 创建新会话: {session_id}")

        with self.lock:
            print(f"[会话管理] 正在初始化 Reporter...")
            reporter = Reporter()

            print(f"[会话管理] 正在初始化 CTFAgent（可能需要几秒钟）...")
            agent = CTFAgent(reporter=reporter, event_callback=event_callback)
            print(f"[会话管理] CTFAgent 初始化完成")

            self.sessions[session_id] = {
                'agent': agent,
                'reporter': reporter,
                'created_at': time.time(),
                'last_activity': time.time(),
                'target_url': None
            }

        print(f"[会话管理] 会话创建完成: {session_id}")
        return session_id

    def get_agent(self, session_id: str) -> Optional[CTFAgent]:
        """
        获取会话的 Agent 实例

        Args:
            session_id: 会话 ID

        Returns:
            CTFAgent 实例，如果会话不存在则返回 None
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if session:
                session['last_activity'] = time.time()
                return session['agent']
            return None

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """
        获取会话信息

        Args:
            session_id: 会话 ID

        Returns:
            会话信息字典，如果会话不存在则返回 None
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if session:
                session['last_activity'] = time.time()
                agent = session['agent']

                return {
                    'session_id': session_id,
                    'created_at': session['created_at'],
                    'last_activity': session['last_activity'],
                    'target_url': session['target_url'],
                    'state': agent.state_manager.current_state.value if hasattr(agent, 'state_manager') else 'INIT',
                    'progress': agent.state_manager.get_progress() if hasattr(agent, 'state_manager') else 0,
                    'flags_found': len(agent.found_flags) if hasattr(agent, 'found_flags') else 0
                }
            return None

    def set_target(self, session_id: str, target_url: str) -> bool:
        """
        设置会话的目标 URL

        Args:
            session_id: 会话 ID
            target_url: 目标 URL

        Returns:
            是否成功
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if session:
                session['target_url'] = target_url
                session['agent'].set_target(target_url)
                session['reporter'].start_session(target_url)
                return True
            return False

    def destroy_session(self, session_id: str) -> bool:
        """
        销毁会话

        Args:
            session_id: 会话 ID

        Returns:
            是否成功
        """
        with self.lock:
            session = self.sessions.pop(session_id, None)
            if session:
                try:
                    session['agent'].close()
                except:
                    pass
                return True
            return False

    def cleanup_expired(self):
        """清理过期会话"""
        current_time = time.time()
        expired_sessions = []

        with self.lock:
            for session_id, session in self.sessions.items():
                if current_time - session['last_activity'] > self.session_timeout:
                    expired_sessions.append(session_id)

        for session_id in expired_sessions:
            self.destroy_session(session_id)
            print(f"[会话管理] 清理过期会话: {session_id}")

    def get_all_sessions(self) -> list:
        """获取所有会话列表"""
        with self.lock:
            return [
                {
                    'session_id': sid,
                    'created_at': session['created_at'],
                    'last_activity': session['last_activity'],
                    'target_url': session['target_url']
                }
                for sid, session in self.sessions.items()
            ]


# 全局会话管理器实例
session_manager = SessionManager()
