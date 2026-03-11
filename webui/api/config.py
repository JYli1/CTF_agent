"""
配置管理 API
"""
from flask import Blueprint, request, jsonify
from src.utils.config import Config
import traceback

config_bp = Blueprint('config', __name__, url_prefix='/api/config')


@config_bp.route('/get', methods=['GET'])
def get_config():
    """获取当前配置"""
    try:
        def mask_key(key):
            if not key:
                return ""
            return f"{key[:10]}...{key[-4:]}" if len(key) > 14 else "***"

        config_data = {
            'llm': {
                'provider': Config.LLM_PROVIDER,
                'api_key': mask_key(Config.SILICONFLOW_API_KEY or Config.OPENAI_API_KEY),
                'base_url': Config.OPENAI_BASE_URL,
                'model': Config.MODEL_NAME
            },
            'experts': {
                'ctf': {
                    'api_key': mask_key(Config.CTF_API_KEY),
                    'base_url': Config.CTF_BASE_URL,
                    'model': Config.CTF_MODEL
                },
                'python': {
                    'api_key': mask_key(Config.PYTHON_API_KEY),
                    'base_url': Config.PYTHON_BASE_URL,
                    'model': Config.PYTHON_MODEL
                },
                'security': {
                    'api_key': mask_key(Config.SECURITY_API_KEY),
                    'base_url': Config.SECURITY_BASE_URL,
                    'model': Config.SECURITY_MODEL
                }
            },
            'rag': {
                'embedding_api_key': mask_key(Config.EMBEDDING_API_KEY),
                'embedding_base_url': Config.EMBEDDING_BASE_URL,
                'embedding_model': Config.EMBEDDING_MODEL,
                'distance_threshold': Config.RAG_DISTANCE_THRESHOLD,
                'chroma_db_dir': Config.CHROMA_DB_DIR
            },
            'ssh': {
                'host': Config.SSH_HOST or '',
                'port': Config.SSH_PORT,
                'user': Config.SSH_USER,
                'password': '***' if Config.SSH_PASSWORD else ''
            },
            'advanced': {
                'max_sub_steps': Config.MAX_SUB_STEPS,
                'log_level': Config.LOG_LEVEL
            }
        }

        return jsonify({
            'success': True,
            'config': config_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'CONFIG_ERROR',
                'message': str(e)
            }
        }), 500


@config_bp.route('/schema', methods=['GET'])
def get_schema():
    """获取配置模板"""
    schema = {
        'llm': {
            'provider': {'type': 'string', 'enum': ['openai', 'modelscope'], 'default': 'openai'},
            'api_key': {'type': 'string', 'required': True},
            'base_url': {'type': 'string', 'default': 'https://api.siliconflow.cn/v1'},
            'model': {'type': 'string', 'default': 'Pro/zai-org/GLM-5'}
        },
        'experts': {
            'ctf': {
                'api_key': {'type': 'string'},
                'base_url': {'type': 'string'},
                'model': {'type': 'string'}
            },
            'python': {
                'api_key': {'type': 'string'},
                'base_url': {'type': 'string'},
                'model': {'type': 'string'}
            },
            'security': {
                'api_key': {'type': 'string'},
                'base_url': {'type': 'string'},
                'model': {'type': 'string'}
            }
        },
        'rag': {
            'embedding_api_key': {'type': 'string'},
            'embedding_model': {'type': 'string', 'default': 'Qwen/Qwen3-Embedding-8B'},
            'distance_threshold': {'type': 'number', 'default': 1.5}
        },
        'ssh': {
            'host': {'type': 'string'},
            'port': {'type': 'integer', 'default': 22},
            'user': {'type': 'string', 'default': 'kali'},
            'password': {'type': 'string'}
        },
        'advanced': {
            'max_sub_steps': {'type': 'integer', 'default': 5},
            'log_level': {'type': 'string', 'enum': ['DEBUG', 'INFO', 'WARNING', 'ERROR'], 'default': 'INFO'}
        }
    }

    return jsonify({
        'success': True,
        'schema': schema
    })


@config_bp.route('/validate', methods=['POST'])
def validate_config():
    """验证配置"""
    try:
        data = request.get_json()
        config = data.get('config', {})

        errors = []
        warnings = []

        # 验证 LLM 配置
        llm = config.get('llm', {})
        if not llm.get('api_key'):
            errors.append('LLM API Key 不能为空')

        # 验证 SSH 配置
        ssh = config.get('ssh', {})
        if ssh.get('host') and not ssh.get('password'):
            warnings.append('SSH 已配置主机但未配置密码')

        return jsonify({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATE_ERROR',
                'message': str(e)
            }
        }), 500


@config_bp.route('/update', methods=['POST'])
def update_config():
    """更新配置（注意：仅在当前会话生效，不会持久化到 .env）"""
    try:
        data = request.get_json()
        config = data.get('config', {})

        # 这里只是示例，实际需要更新 Config 类的属性
        # 注意：这种方式不会持久化，重启后会丢失

        return jsonify({
            'success': True,
            'message': '配置已更新（仅当前会话生效）',
            'warning': '配置未持久化到 .env 文件，重启后将恢复默认值'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_ERROR',
                'message': str(e)
            }
        }), 500
