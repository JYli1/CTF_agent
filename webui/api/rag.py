"""
RAG 知识库 API
"""
from flask import Blueprint, request, jsonify
from src.rag.engine import RAGSystem
import traceback

rag_bp = Blueprint('rag', __name__, url_prefix='/api/rag')

# 全局 RAG 实例
rag_system = RAGSystem()


@rag_bp.route('/query', methods=['POST'])
def query_knowledge():
    """查询知识库"""
    try:
        data = request.get_json()
        query = data.get('query')
        n_results = data.get('n_results', 5)
        challenge_type = data.get('challenge_type')

        if not query:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_PARAMS',
                    'message': '缺少 query 参数'
                }
            }), 400

        documents = rag_system.query(
            query_text=query,
            n_results=n_results,
            challenge_type=challenge_type
        )

        return jsonify({
            'success': True,
            'documents': documents,
            'count': len(documents)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'RAG_QUERY_ERROR',
                'message': str(e),
                'details': traceback.format_exc()
            }
        }), 500


@rag_bp.route('/sync', methods=['POST'])
def sync_knowledge():
    """同步知识库"""
    try:
        data = request.get_json() or {}
        folder_path = data.get('folder_path', 'data/knowledge_base')

        report = rag_system.sync_folder(folder_path)

        return jsonify({
            'success': True,
            'report': report,
            'message': f"同步完成: 新增 {report['added']}, 删除 {report['deleted']}, 更新 {report['updated']}, 跳过 {report['skipped']}"
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'RAG_SYNC_ERROR',
                'message': str(e),
                'details': traceback.format_exc()
            }
        }), 500


@rag_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取知识库统计"""
    try:
        count = rag_system.count()
        sources = rag_system.list_sources()

        return jsonify({
            'success': True,
            'count': count,
            'sources': sources,
            'source_count': len(sources)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'RAG_STATS_ERROR',
                'message': str(e)
            }
        }), 500


@rag_bp.route('/list', methods=['GET'])
def list_documents():
    """列出文档"""
    try:
        limit = int(request.args.get('limit', 50))

        items = rag_system.list_all(limit=limit)

        return jsonify({
            'success': True,
            'items': items,
            'count': len(items)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'RAG_LIST_ERROR',
                'message': str(e)
            }
        }), 500
