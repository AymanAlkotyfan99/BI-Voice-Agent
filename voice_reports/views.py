"""
Voice Reports Views

API endpoints for voice-driven BI system.
Orchestrates Small Whisper, ClickHouse, and Metabase.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging
import os
import requests

from .models import VoiceReport, SQLEditHistory
from .services import (
    get_small_whisper_client,
    get_clickhouse_executor,
    SQLGuard,
    get_metabase_service,
    get_jwt_service
)
from users.permissions import IsManager, IsAnalyst, IsExecutive

logger = logging.getLogger(__name__)


def get_user_workspace(user):
    """
    Get the user's workspace based on their role.
    
    - Manager: Returns their owned workspace
    - Analyst/Executive: Returns workspace they're a member of
    """
    if user.role == 'manager':
        # Manager owns workspace
        workspace = user.owned_workspaces.first()
        return workspace
    else:
        # Analyst or Executive is a member
        membership = user.workspace_memberships.filter(status='active').first()
        if membership:
            return membership.workspace
        return None


class VoiceUploadView(APIView):
    """
    Upload audio file and get transcription + generated SQL from Small Whisper.
    
    Manager only.
    """
    permission_classes = [IsAuthenticated, IsManager]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try:
            # Validate audio file
            if 'audio' not in request.FILES:
                return Response(
                    {'success': False, 'error': 'No audio file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            audio_file = request.FILES['audio']
            workspace = get_user_workspace(request.user)
            
            if not workspace:
                return Response(
                    {'success': False, 'error': 'User must belong to a workspace'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save audio file
            audio_dir = f'media/workspaces/{workspace.id}/audio'
            os.makedirs(audio_dir, exist_ok=True)
            
            # Generate unique filename
            import uuid
            filename = f"{uuid.uuid4()}_{audio_file.name}"
            audio_path = os.path.join(audio_dir, filename)
            
            with open(audio_path, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)
            
            logger.info(f"Audio file saved: {audio_path}")
            
            # Call Small Whisper
            whisper_client = get_small_whisper_client()
            whisper_result = whisper_client.process_audio(audio_path)
            
            if not whisper_result['success']:
                return Response(
                    {
                        'success': False,
                        'error': f"Small Whisper error: {whisper_result.get('error')}"
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Create report record
            report = VoiceReport.objects.create(
                workspace=workspace,
                created_by=request.user,
                audio_file=audio_path,
                transcription=whisper_result['text'],
                intent_json=whisper_result.get('intent'),
                generated_sql=whisper_result['sql'],
                final_sql=whisper_result['sql'],  # Initially same
                status='pending_execution'
            )
            
            # TODO: Create history entry when ReportHistory model is added
            # ReportHistory.objects.create(
            #     report=report,
            #     action='created',
            #     performed_by=request.user,
            #     changes={
            #         'transcription': whisper_result['text'],
            #         'sql': whisper_result['sql']
            #     }
            # )
            
            logger.info(f"Voice report created: {report.id}")
            
            return Response({
                'success': True,
                'report_id': report.id,
                'transcription': whisper_result['text'],
                'intent': whisper_result.get('intent'),
                'sql': whisper_result['sql'],
                'message': 'Audio processed successfully. Ready to execute.'
            })
        
        except Exception as e:
            logger.error(f"Error in VoiceUploadView: {e}", exc_info=True)
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QueryExecuteView(APIView):
    """
    Execute SQL query on ClickHouse and create Metabase visualization.
    
    Manager and Analyst can execute.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, report_id):
        try:
            # Get report
            workspace = get_user_workspace(request.user)
            if not workspace:
                return Response(
                    {'success': False, 'error': 'User must belong to a workspace'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            report = get_object_or_404(
                VoiceReport,
                id=report_id,
                workspace=workspace
            )
            
            # Validate permissions
            if request.user.role not in ['manager', 'analyst']:
                return Response(
                    {'success': False, 'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get SQL (final_sql may be edited by analyst)
            sql_to_execute = report.final_sql
            
            # Validate SQL with SQL Guard
            guard = SQLGuard(
                workspace_database=os.getenv('CLICKHOUSE_DATABASE', 'etl')
            )
            
            is_valid, error_msg, clean_sql = guard.validate_and_sanitize(sql_to_execute)
            
            if not is_valid:
                report.status = 'failed'
                report.error_message = f"SQL validation failed: {error_msg}"
                report.save()
                
                return Response(
                    {'success': False, 'error': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            report.sql_validated = True
            report.final_sql = clean_sql
            report.save()
            
            # Execute on ClickHouse
            report.status = 'executing'
            report.save()
            
            try:
                executor = get_clickhouse_executor()
                query_result = executor.execute_query(clean_sql)
                
                if not query_result['success']:
                    report.status = 'failed'
                    report.error_message = query_result['error']
                    report.save()
                    
                    logger.error(f"ClickHouse query failed for report {report.id}: {query_result['error']}")
                    
                    # Return 502 Bad Gateway for external service failures
                    return Response(
                        {
                            'success': False,
                            'error': 'Query execution failed',
                            'details': query_result['error']
                        },
                        status=status.HTTP_502_BAD_GATEWAY
                    )
            except Exception as e:
                report.status = 'failed'
                report.error_message = f"ClickHouse connection error: {str(e)}"
                report.save()
                
                logger.error(f"ClickHouse connection error for report {report.id}: {e}", exc_info=True)
                
                # Return 502 for ClickHouse connectivity issues
                return Response(
                    {
                        'success': False,
                        'error': 'Cannot connect to data warehouse',
                        'details': str(e)
                    },
                    status=status.HTTP_502_BAD_GATEWAY
                )
            
            # Save query results
            report.query_result = query_result['rows']
            report.execution_time_ms = query_result['execution_time_ms']
            report.row_count = query_result['row_count']
            report.status = 'executed'
            report.save()
            
            # Infer chart type
            chart_type = self._infer_chart_type(
                query_result['columns'],
                query_result['rows'],
                report.intent_json
            )
            
            # Create Metabase question
            metabase = get_metabase_service()
            
            if not metabase.authenticate():
                logger.warning("Metabase authentication failed")
                return Response({
                    'success': True,
                    'report_id': report.id,
                    'row_count': query_result['row_count'],
                    'execution_time_ms': query_result['execution_time_ms'],
                    'chart_type': chart_type,
                    'warning': 'Query executed but Metabase unavailable'
                })
            
            # Create question in Metabase
            question_id = metabase.create_question(
                name=f"Voice Report #{report.id}: {report.transcription[:50]}",
                sql=clean_sql,
                visualization_settings={'display': chart_type}
            )
            
            if question_id:
                report.metabase_question_id = question_id
                
                # Enable embedding
                metabase.enable_question_embedding(question_id)
                
                # Get or create workspace dashboard
                dashboard_id = self._get_or_create_dashboard(
                    report.workspace,
                    metabase
                )
                
                if dashboard_id:
                    # Add to dashboard
                    metabase.add_question_to_dashboard(question_id, dashboard_id)
                    report.metabase_dashboard_id = dashboard_id
                
                # Generate embed URL
                jwt_service = get_jwt_service()
                embed_url = jwt_service.get_question_embed_url(
                    question_id=question_id,
                    workspace_id=report.workspace.id
                )
                
                report.embed_url = embed_url
            
            # TODO: Save chart inference when ChartInference model is added
            # ChartInference.objects.create(
            #     report=report,
            #     inferred_type=chart_type,
            #     column_analysis={
            #         'columns': query_result['columns'],
            #         'row_count': query_result['row_count']
            #     },
            #     confidence_score=0.85
            # )
            
            report.chart_type = chart_type
            report.status = 'completed'
            report.save()
            
            # TODO: Create history entry when ReportHistory model is added
            # ReportHistory.objects.create(
            #     report=report,
            #     action='executed',
            #     performed_by=request.user,
            #     changes={
            #         'row_count': query_result['row_count'],
            #         'execution_time_ms': query_result['execution_time_ms'],
            #         'chart_type': chart_type
            #     }
            # )
            
            logger.info(f"Report {report.id} executed successfully")
            
            return Response({
                'success': True,
                'report_id': report.id,
                'row_count': query_result['row_count'],
                'execution_time_ms': query_result['execution_time_ms'],
                'chart_type': chart_type,
                'embed_url': report.embed_url,
                'metabase_question_id': question_id
            })
        
        except Exception as e:
            logger.error(f"Error in QueryExecuteView: {e}", exc_info=True)
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _infer_chart_type(self, columns, rows, intent):
        """Infer appropriate chart type from data and intent."""
        if not rows:
            return 'table'
        
        num_columns = len(columns)
        
        # Single value -> number display
        if num_columns == 1 and len(rows) == 1:
            return 'scalar'
        
        # Two columns -> likely x/y chart
        if num_columns == 2:
            # Check if first column is date/time
            first_col_name = columns[0].lower()
            if any(term in first_col_name for term in ['date', 'time', 'year', 'month', 'day']):
                return 'line'
            else:
                return 'bar'
        
        # Multiple numeric columns -> bar chart
        if num_columns > 2:
            return 'bar'
        
        # Default
        return 'table'
    
    def _get_or_create_dashboard(self, workspace, metabase):
        """Get or create Metabase dashboard for workspace."""
        # Check if workspace already has a dashboard
        existing_report = VoiceReport.objects.filter(
            workspace=workspace,
            metabase_dashboard_id__isnull=False
        ).first()
        
        if existing_report:
            return existing_report.metabase_dashboard_id
        
        # Create new dashboard
        dashboard_id = metabase.create_dashboard(
            name=f"Workspace {workspace.id} - Voice Reports",
            description=f"Voice-driven reports for {workspace.name}"
        )
        
        return dashboard_id


class SQLEditView(APIView):
    """
    Edit SQL query (Analyst only).
    """
    permission_classes = [IsAuthenticated, IsAnalyst]
    
    def put(self, request, report_id):
        try:
            workspace = get_user_workspace(request.user)
            if not workspace:
                return Response(
                    {'success': False, 'error': 'User must belong to a workspace'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            report = get_object_or_404(
                VoiceReport,
                id=report_id,
                workspace=workspace
            )
            
            new_sql = request.data.get('sql')
            
            if not new_sql:
                return Response(
                    {'success': False, 'error': 'SQL is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate new SQL
            guard = SQLGuard(
                workspace_database=os.getenv('CLICKHOUSE_DATABASE', 'etl')
            )
            
            is_valid, error_msg, clean_sql = guard.validate_and_sanitize(new_sql)
            
            if not is_valid:
                return Response(
                    {'success': False, 'error': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save old SQL for history
            old_sql = report.final_sql
            
            # Update report
            report.final_sql = clean_sql
            report.sql_edited = True
            report.edited_by = request.user
            report.sql_validated = True
            report.status = 'pending_execution'  # Needs re-execution
            report.save()
            
            # TODO: Create history entry when ReportHistory model is added
            # ReportHistory.objects.create(
            #     report=report,
            #     action='sql_edited',
            #     performed_by=request.user,
            #     changes={
            #         'old_sql': old_sql,
            #         'new_sql': clean_sql
            #     }
            # )
            
            logger.info(f"Report {report.id} SQL edited by analyst {request.user.email}")
            
            return Response({
                'success': True,
                'report_id': report.id,
                'sql': clean_sql,
                'message': 'SQL updated successfully. Ready to re-execute.'
            })
        
        except Exception as e:
            logger.error(f"Error in SQLEditView: {e}", exc_info=True)
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReportListView(APIView):
    """
    List all reports for workspace.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            workspace = get_user_workspace(request.user)
            if not workspace:
                return Response(
                    {'success': False, 'error': 'User must belong to a workspace'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            reports = VoiceReport.objects.filter(
                workspace=workspace
            ).order_by('-created_at')
            
            # Filter by role
            if request.user.role == 'manager':
                # Manager sees only their own reports
                reports = reports.filter(created_by=request.user)
            # Analyst and Executive see all workspace reports
            
            data = []
            for report in reports:
                data.append({
                    'id': report.id,
                    'transcription': report.transcription,
                    'status': report.status,
                    'created_at': report.created_at,
                    'created_by': report.created_by.email,
                    'chart_type': report.chart_type,
                    'row_count': report.row_count,
                    'execution_time_ms': report.execution_time_ms,
                    'sql': report.final_sql,
                    'embed_url': report.embed_url,
                    'can_edit': request.user.role == 'analyst'
                })
            
            return Response({
                'success': True,
                'reports': data,
                'count': len(data)
            })
        
        except Exception as e:
            logger.error(f"Error in ReportListView: {e}", exc_info=True)
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReportDetailView(APIView):
    """
    Get detailed report information.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        try:
            workspace = get_user_workspace(request.user)
            if not workspace:
                return Response(
                    {'success': False, 'error': 'User must belong to a workspace'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            report = get_object_or_404(
                VoiceReport,
                id=report_id,
                workspace=workspace
            )
            
            # TODO: Get history when ReportHistory model is added
            # history = ReportHistory.objects.filter(report=report).order_by('-timestamp')
            # history_data = [{
            #     'action': h.action,
            #     'performed_by': h.performed_by.email,
            #     'timestamp': h.timestamp,
            #     'changes': h.changes
            # } for h in history]
            history_data = []  # Placeholder until ReportHistory is added
            
            return Response({
                'success': True,
                'report': {
                    'id': report.id,
                    'transcription': report.transcription,
                    'intent': report.intent_json,
                    'generated_sql': report.generated_sql,
                    'final_sql': report.final_sql,
                    'status': report.status,
                    'sql_validated': report.sql_validated,
                    'sql_edited': report.sql_edited,
                    'query_result': report.query_result,
                    'row_count': report.row_count,
                    'execution_time_ms': report.execution_time_ms,
                    'chart_type': report.chart_type,
                    'embed_url': report.embed_url,
                    'error_message': report.error_message,
                    'created_at': report.created_at,
                    'created_by': report.created_by.email,
                    'edited_by': report.edited_by.email if report.edited_by else None,
                    'history': history_data
                }
            })
        
        except Exception as e:
            logger.error(f"Error in ReportDetailView: {e}", exc_info=True)
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, report_id):
        """Delete report (Manager only)."""
        if request.user.role != 'manager':
            return Response(
                {'success': False, 'error': 'Only managers can delete reports'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            workspace = get_user_workspace(request.user)
            if not workspace:
                return Response(
                    {'success': False, 'error': 'User must belong to a workspace'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            report = get_object_or_404(
                VoiceReport,
                id=report_id,
                workspace=workspace,
                created_by=request.user  # Can only delete own reports
            )
            
            report.delete()
            
            logger.info(f"Report {report_id} deleted by {request.user.email}")
            
            return Response({
                'success': True,
                'message': 'Report deleted successfully'
            })
        
        except Exception as e:
            logger.error(f"Error deleting report: {e}", exc_info=True)
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WorkspaceDashboardView(APIView):
    """
    Get workspace dashboard for embedded viewing (Executive).
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            workspace = get_user_workspace(request.user)
            if not workspace:
                return Response(
                    {'success': False, 'error': 'User must belong to a workspace'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get dashboard ID from any report
            report = VoiceReport.objects.filter(
                workspace=workspace,
                metabase_dashboard_id__isnull=False
            ).first()
            
            if not report:
                return Response({
                    'success': False,
                    'error': 'No dashboard available yet. Create some reports first.'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Generate JWT embed URL for dashboard
            jwt_service = get_jwt_service()
            embed_url = jwt_service.get_dashboard_embed_url(
                dashboard_id=report.metabase_dashboard_id,
                workspace_id=workspace.id
            )
            
            return Response({
                'success': True,
                'dashboard_url': embed_url,
                'dashboard_id': report.metabase_dashboard_id
            })
        
        except Exception as e:
            logger.error(f"Error in WorkspaceDashboardView: {e}", exc_info=True)
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckView(APIView):
    """
    Health check for all services.
    """
    permission_classes = []  # Public endpoint
    
    def get(self, request):
        """Check connectivity to Small Whisper, ClickHouse, and Metabase."""
        health = {
            'small_whisper': False,
            'clickhouse': False,
            'metabase': False
        }
        
        # Check Small Whisper
        try:
            whisper_client = get_small_whisper_client()
            response = requests.get(f"{whisper_client.base_url}/health/", timeout=5)
            health['small_whisper'] = response.status_code == 200
        except:
            pass
        
        # Check ClickHouse
        try:
            executor = get_clickhouse_executor()
            health['clickhouse'] = executor.test_connection()
        except:
            pass
        
        # Check Metabase
        try:
            metabase = get_metabase_service()
            health['metabase'] = metabase.authenticate()
        except:
            pass
        
        all_healthy = all(health.values())
        
        return Response({
            'success': all_healthy,
            'services': health,
            'message': 'All services healthy' if all_healthy else 'Some services unavailable'
        }, status=status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE)

