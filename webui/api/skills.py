"""
技能系统 API
"""
from flask import Blueprint, request, jsonify
from src.skills.registry import skill_registry
from webui.session_manager import session_manager
import traceback

skills_bp = Blueprint('skills', __name__, url_prefix='/api/skills')


@skills_bp.route('/list', methods=['GET'])
def list_skills():
    """列出所有技能"""
    try:
        category = request.args.get('category')

        skills = skill_registry.list_skills(category=category)

        # 转换为可序列化的格式
        skills_data = [
            {
                'id': skill.id,
                'name': skill.name,
                'category': skill.category.value if hasattr(skill.category, 'value') else str(skill.category),
                'description': skill.description,
                'difficulty': skill.difficulty,
                'prerequisites': skill.prerequisites,
                'tools_required': skill.tools_required
            }
            for skill in skills
        ]

        return jsonify({
            'success': True,
            'skills': skills_data,
            'count': len(skills_data)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SKILLS_LIST_ERROR',
                'message': str(e)
            }
        }), 500


@skills_bp.route('/info', methods=['GET'])
def get_skill_info():
    """获取技能详情"""
    try:
        skill_id = request.args.get('skill_id')

        if not skill_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PARAMS',
                    'message': '缺少 skill_id 参数'
                }
            }), 400

        skill = skill_registry.get_skill(skill_id)

        if not skill:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SKILL_NOT_FOUND',
                    'message': f'技能不存在: {skill_id}'
                }
            }), 404

        skill_data = {
            'id': skill.id,
            'name': skill.name,
            'category': skill.category.value if hasattr(skill.category, 'value') else str(skill.category),
            'description': skill.description,
            'difficulty': skill.difficulty,
            'prerequisites': skill.prerequisites,
            'tools_required': skill.tools_required
        }

        return jsonify({
            'success': True,
            'skill': skill_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SKILL_INFO_ERROR',
                'message': str(e)
            }
        }), 500


@skills_bp.route('/execute', methods=['POST'])
def execute_skill():
    """执行技能"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        skill_id = data.get('skill_id')
        context = data.get('context', {})

        if not session_id or not skill_id:
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

        # 执行技能
        result = agent.use_skill(skill_id, context)

        return jsonify({
            'success': True,
            'result': {
                'success': result.success if hasattr(result, 'success') else True,
                'message': result.message if hasattr(result, 'message') else str(result),
                'data': result.data if hasattr(result, 'data') else {},
                'commands': result.commands if hasattr(result, 'commands') else [],
                'findings': result.findings if hasattr(result, 'findings') else []
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SKILL_EXECUTE_ERROR',
                'message': str(e),
                'details': traceback.format_exc()
            }
        }), 500
