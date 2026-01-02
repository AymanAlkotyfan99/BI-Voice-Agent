from django.db import models
from django.conf import settings
from django.utils import timezone
from workspace.models import Workspace


class VoiceReport(models.Model):
    """
    Voice-driven BI report with full audit trail.
    Links audio → transcription → SQL → visualization.
    """
    
    CHART_CHOICES = [
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('number', 'Number/KPI'),
        ('table', 'Table'),
    ]
    
    STATUS_CHOICES = [
        ('uploaded', 'Audio Uploaded'),
        ('transcribing', 'Transcribing'),
        ('transcribed', 'Transcribed'),
        ('generating_sql', 'Generating SQL'),
        ('sql_generated', 'SQL Generated'),
        ('pending_execution', 'Pending Execution'),
        ('executing', 'Executing Query'),
        ('executed', 'Executed'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Ownership & Workspace Isolation
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='voice_reports'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_reports'
    )
    
    # Audio
    audio_file = models.FileField(
        upload_to='workspaces/%Y/%m/%d/',
        help_text='Audio file path: /media/workspaces/{workspace_id}/audio/'
    )
    audio_duration = models.FloatField(null=True, blank=True, help_text='Duration in seconds')
    
    # Transcription
    transcription = models.TextField(blank=True, help_text='Whisper STT output')
    transcription_language = models.CharField(max_length=10, blank=True, default='en')
    
    # SQL Generation
    intent_json = models.JSONField(null=True, blank=True, help_text='Extracted intent from text')
    generated_sql = models.TextField(blank=True, help_text='Generated SQL query')
    final_sql = models.TextField(blank=True, help_text='Final SQL after validation/edits')
    sql_validated = models.BooleanField(default=False)
    sql_edited = models.BooleanField(default=False, help_text='Has SQL been manually edited')
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_reports',
        help_text='User who last edited the SQL'
    )
    
    # Execution
    query_result = models.JSONField(null=True, blank=True, help_text='Query execution result')
    execution_time_ms = models.IntegerField(null=True, blank=True)
    row_count = models.IntegerField(null=True, blank=True)
    
    # Visualization
    chart_type = models.CharField(max_length=20, choices=CHART_CHOICES, blank=True)
    chart_config = models.JSONField(null=True, blank=True, help_text='Chart configuration')
    
    # Metabase Integration
    metabase_question_id = models.IntegerField(null=True, blank=True)
    metabase_dashboard_id = models.IntegerField(null=True, blank=True)
    embed_url = models.TextField(blank=True, help_text='JWT-signed embed URL')
    
    # Status & Timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Report Metadata
    title = models.CharField(max_length=255, blank=True, help_text='Auto-generated or user-provided')
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'voice_reports'
        verbose_name = 'Voice Report'
        verbose_name_plural = 'Voice Reports'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'created_by']),
            models.Index(fields=['workspace', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title or f'Report #{self.id}'} - {self.workspace.name}"
    
    def can_edit_transcription(self, user):
        """Check if user can edit transcription."""
        return user.role in ['manager', 'analyst']
    
    def can_edit_sql(self, user):
        """Check if user can edit SQL."""
        return user.role == 'analyst'
    
    def can_delete(self, user):
        """Check if user can delete report."""
        return user.role == 'manager'


class SQLEditHistory(models.Model):
    """
    Track all SQL edits for audit purposes.
    """
    report = models.ForeignKey(
        VoiceReport,
        on_delete=models.CASCADE,
        related_name='sql_history'
    )
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    
    previous_sql = models.TextField()
    new_sql = models.TextField()
    
    validation_passed = models.BooleanField(default=False)
    validation_errors = models.JSONField(null=True, blank=True)
    
    edited_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'sql_edit_history'
        verbose_name = 'SQL Edit History'
        verbose_name_plural = 'SQL Edit Histories'
        ordering = ['-edited_at']
    
    def __str__(self):
        return f"SQL Edit for Report #{self.report.id} by {self.edited_by.email}"


class DashboardPage(models.Model):
    """
    Dashboard pages/tabs for organizing reports.
    """
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='dashboard_pages'
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    # Metabase Dashboard ID
    metabase_dashboard_id = models.IntegerField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'dashboard_pages'
        verbose_name = 'Dashboard Page'
        verbose_name_plural = 'Dashboard Pages'
        ordering = ['workspace', 'order']
        unique_together = [['workspace', 'name']]
    
    def __str__(self):
        return f"{self.name} - {self.workspace.name}"


class ReportPageAssignment(models.Model):
    """
    Many-to-many relationship between reports and dashboard pages.
    """
    report = models.ForeignKey(
        VoiceReport,
        on_delete=models.CASCADE,
        related_name='page_assignments'
    )
    page = models.ForeignKey(
        DashboardPage,
        on_delete=models.CASCADE,
        related_name='report_assignments'
    )
    order = models.IntegerField(default=0)
    
    added_at = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    
    class Meta:
        db_table = 'report_page_assignments'
        verbose_name = 'Report Page Assignment'
        verbose_name_plural = 'Report Page Assignments'
        ordering = ['page', 'order']
        unique_together = [['report', 'page']]
    
    def __str__(self):
        return f"{self.report} → {self.page}"

