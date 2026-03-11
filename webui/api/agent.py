"""
Agent 管理 API
"""
from flask import Blueprint, request, jsonify
from webui.session_manager import session_manager
from webui.websocket_handler import create_event_callback
import traceback

agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')


@agent_bp.route('/init', methods=['POST'])
def init_session():
    """初始化会话"""
    try:
        print(f"\n[API] 收到初始化会话请求")

        # 从请求中获取 socketio 实例（如果有）
        socketio = request.environ.get('socketio')
        event_callback = None

        print(f"[API] 正在创建会话...")
        # 创建会话
        session_id = session_manager.create_session(event_callback=event_callback)
        print(f"[API] 会话创建成功: {session_id}")

        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': '会话创建成功'
        })
    except Exception as e:
        print(f"[API] 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INIT_ERROR',
                'message': str(e),
                'details': traceback.format_exc()
            }
        }), 500


@agent_bp.route('/set-target', methods=['POST'])
def set_target():
    """设置目标 URL"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        target_url = data.get('target_url')

        if not session_id or not target_url:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PARAMS',
                    'message': '缺少必需参数'
                }
            }), 400

        success = session_manager.set_target(session_id, target_url)

        if success:
            return jsonify({
                'success': True,
                'message': f'目标已设置为: {target_url}'
            })
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SESSION_NOT_FOUND',
                    'message': '会话不存在'
                }
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SET_TARGET_ERROR',
                'message': str(e)
            }
        }), 500


@agent_bp.route('/step', methods=['POST'])
def execute_step():
    """执行一步分析"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user_input = data.get('user_input')
        auto_mode = data.get('auto_mode', False)

        if not session_id or not user_input:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PARAMS',
                    'message': '缺少必需参数'
                }
            }), 400

        agent = session_manager.get_agent(session_id)
        if not agent:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SESSION_NOT_FOUND',
                    'message': '会话不存在'
                }
            }), 404

        # 执行 Agent
        response = agent.run_step(user_input)

        # 获取状态信息
        state = agent.state_manager.current_state.value if hasattr(agent, 'state_manager') else 'UNKNOWN'
        progress = agent.state_manager.get_progress() if hasattr(agent, 'state_manager') else 0
        flags = agent.found_flags if hasattr(agent, 'found_flags') else []
        phases = [p.value for p in agent.phase_tracker.get_achieved_phases()] if hasattr(agent, 'phase_tracker') else []

        return jsonify({
            'success': True,
            'response': response,
            'state': state,
            'progress': progress,
            'flags': flags,
            'phases': phases,
            'flag_found': agent.flag_found if hasattr(agent, 'flag_found') else False
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'AGENT_ERROR',
                'message': str(e),
                'details': traceback.format_exc()
            }
        }), 500


@agent_bp.route('/status', methods=['GET'])
def get_status():
    """获取会话状态"""
    try:
        session_id = request.args.get('session_id')

        if not session_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PARAMS',
                    'message': '缺少 session_id 参数'
                }
            }), 400

        session_info = session_manager.get_session_info(session_id)

        if session_info:
            return jsonify({
                'success': True,
                **session_info
            })
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SESSION_NOT_FOUND',
                    'message': '会话不存在'
                }
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'STATUS_ERROR',
                'message': str(e)
            }
        }), 500


@agent_bp.route('/history', methods=['GET'])
def get_history():
    """获取对话历史"""
    try:
        session_id = request.args.get('session_id')

        if not session_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PARAMS',
                    'message': '缺少 session_id 参数'
                }
            }), 400

        agent = session_manager.get_agent(session_id)
        if not agent:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SESSION_NOT_FOUND',
                    'message': '会话不存在'
                }
            }), 404

        history = agent.history if hasattr(agent, 'history') else []

        return jsonify({
            'success': True,
            'messages': history
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'HISTORY_ERROR',
                'message': str(e)
            }
        }), 500


@agent_bp.route('/reset', methods=['POST'])
def reset_session():
    """重置会话"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PARAMS',
                    'message': '缺少 session_id 参数'
                }
            }), 400

        # 销毁旧会话并创建新会话
        session_manager.destroy_session(session_id)
        new_session_id = session_manager.create_session()

        return jsonify({
            'success': True,
            'session_id': new_session_id,
            'message': '会话已重置'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'RESET_ERROR',
                'message': str(e)
            }
        }), 500


@agent_bp.route('/destroy', methods=['DELETE'])
def destroy_session():
    """销毁会话"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PARAMS',
                    'message': '缺少 session_id 参数'
                }
            }), 400

        success = session_manager.destroy_session(session_id)

        if success:
            return jsonify({
                'success': True,
                'message': '会话已销毁'
            })
        else:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SESSION_NOT_FOUND',
                    'message': '会话不存在'
                }
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'DESTROY_ERROR',
                'message': str(e)
            }
        }), 500
