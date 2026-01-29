# Classes Reference Documentation

Complete reference of all classes in the BI Voice Agent system.

---

## Table of Contents

1. [Backend - Main Django Application](#backend---main-django-application)
2. [Backend - Small Whisper (AI Module)](#backend---small-whisper-ai-module)
3. [ETL Pipeline Services](#etl-pipeline-services)
4. [Frontend Components](#frontend-components)

---

## Backend - Main Django Application

### User Management Module

#### Class: UserManager
**Location:** `users/models.py`  
**Responsibility:** Custom user manager for email-based authentication.

**Methods:**
- `create_user(email, password=None, **extra_fields) -> User`
  - Description: Creates and returns a regular user with an email and password.
  - Parameters:
    - `email` (str): User email address
    - `password` (str, optional): User password
    - `**extra_fields`: Additional user fields
  - Returns: User instance

- `create_superuser(email, password=None, **extra_fields) -> User`
  - Description: Creates and returns a superuser with an email and password.
  - Parameters:
    - `email` (str): User email address
    - `password` (str, optional): User password
    - `**extra_fields`: Additional user fields (sets is_staff=True, is_superuser=True)
  - Returns: User instance

#### Class: User
**Location:** `users/models.py`  
**Responsibility:** Custom User model with email as the unique identifier.

**Methods:**
- `__str__() -> str`
  - Description: String representation of user.
  - Returns: Formatted string with name and email

#### Class: SignUpView
**Location:** `users/views.py`  
**Responsibility:** API endpoint for user sign up.

**Methods:**
- `post(request) -> Response`
  - Description: Handle user sign up request with validation, user creation, workspace creation (if manager), and email verification.
  - Parameters:
    - `request`: Django request object with signup data
  - Returns: Response with user details and workspace info

#### Class: EmailVerificationView
**Location:** `users/views.py`  
**Responsibility:** API endpoint for email verification.

**Methods:**
- `get(request) -> Response`
  - Description: Handle email verification request using signed token.
  - Parameters:
    - `request`: Django request object with verification token in query params
  - Returns: Response with verification status

#### Class: LoginView
**Location:** `users/views.py`  
**Responsibility:** API endpoint for user login.

**Methods:**
- `post(request) -> Response`
  - Description: Handle user login with credential validation and JWT token generation.
  - Parameters:
    - `request`: Django request object with email and password
  - Returns: Response with JWT tokens and user/workspace info

#### Class: LogoutView
**Location:** `users/views.py`  
**Responsibility:** API endpoint for user logout.

**Methods:**
- `post(request) -> Response`
  - Description: Handle user logout by blacklisting refresh token.
  - Parameters:
    - `request`: Django request object with refresh token
  - Returns: Response with logout confirmation

#### Class: ProfileView
**Location:** `users/views.py`  
**Responsibility:** API endpoint for viewing and updating user profile.

**Methods:**
- `get(request) -> Response`
  - Description: Get authenticated user's profile.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with user profile data

- `put(request) -> Response`
  - Description: Update authenticated user's profile (name and/or email).
  - Parameters:
    - `request`: Django request object with update data
  - Returns: Response with updated user profile

#### Class: DeactivateAccountView
**Location:** `users/views.py`  
**Responsibility:** API endpoint for deactivating user account.

**Methods:**
- `delete(request) -> Response`
  - Description: Deactivate authenticated user's account and blacklist refresh token.
  - Parameters:
    - `request`: Django request object with refresh token
  - Returns: Response with deactivation confirmation

#### Class: SignUpSerializer
**Location:** `users/serializers.py`  
**Responsibility:** Serializer for user sign up with invitation support.

**Methods:**
- `validate_email(value) -> str`
  - Description: Validate that email is unique (normalized to lowercase).
  - Parameters:
    - `value` (str): Email address
  - Returns: Lowercase email string

- `validate_password(value) -> str`
  - Description: Validate password strength using Django's password validators.
  - Parameters:
    - `value` (str): Password string
  - Returns: Validated password

- `validate(attrs) -> dict`
  - Description: Validate signup data and handle invitation token.
  - Parameters:
    - `attrs` (dict): Serializer data
  - Returns: Validated data with invitation info if applicable

- `create(validated_data) -> dict`
  - Description: Create user and auto-create workspace if manager. Handle invitation signup.
  - Parameters:
    - `validated_data` (dict): Validated serializer data
  - Returns: Dict with user, workspace, and is_invited flag

#### Class: LoginSerializer
**Location:** `users/serializers.py`  
**Responsibility:** Serializer for user login with JWT token generation.

**Methods:**
- `validate(attrs) -> dict`
  - Description: Validate login credentials and generate JWT tokens.
  - Parameters:
    - `attrs` (dict): Email and password
  - Returns: Dict with tokens, user info, and workspace info

#### Class: LogoutSerializer
**Location:** `users/serializers.py`  
**Responsibility:** Serializer for user logout with JWT token blacklisting.

**Methods:**
- `validate_refresh(value) -> str`
  - Description: Validate that refresh token is provided.
  - Parameters:
    - `value` (str): Refresh token string
  - Returns: Validated token

- `save() -> None`
  - Description: Blacklist the refresh token.
  - Returns: None

#### Class: ProfileSerializer
**Location:** `users/serializers.py`  
**Responsibility:** Serializer for viewing user profile.

**Methods:**
- `get_workspace(obj) -> dict | None`
  - Description: Get workspace info based on user role.
  - Parameters:
    - `obj` (User): User instance
  - Returns: Workspace dict or None

#### Class: UpdateProfileSerializer
**Location:** `users/serializers.py`  
**Responsibility:** Serializer for updating user profile.

**Methods:**
- `validate_email(value) -> str`
  - Description: Validate that new email is unique.
  - Parameters:
    - `value` (str): Email address
  - Returns: Validated email

- `update(instance, validated_data) -> dict`
  - Description: Update user profile. Sets is_verified=False if email changes.
  - Parameters:
    - `instance` (User): User instance to update
    - `validated_data` (dict): Update data
  - Returns: Dict with updated user and email_changed flag

#### Class: DeactivateAccountSerializer
**Location:** `users/serializers.py`  
**Responsibility:** Serializer for deactivating user account.

**Methods:**
- `validate_refresh(value) -> str`
  - Description: Validate that refresh token is provided.
  - Parameters:
    - `value` (str): Refresh token
  - Returns: Validated token

- `save() -> User`
  - Description: Deactivate user account and blacklist refresh token.
  - Returns: Deactivated User instance

#### Class: IsManager
**Location:** `users/permissions.py`  
**Responsibility:** Permission class to allow only managers.

**Methods:**
- `has_permission(request, view) -> bool`
  - Description: Check if user is authenticated and has manager role.
  - Parameters:
    - `request`: Django request object
    - `view`: View instance
  - Returns: True if user is manager, False otherwise

#### Class: IsAnalyst
**Location:** `users/permissions.py`  
**Responsibility:** Permission class to allow only analysts.

**Methods:**
- `has_permission(request, view) -> bool`
  - Description: Check if user is authenticated and has analyst role.
  - Parameters:
    - `request`: Django request object
    - `view`: View instance
  - Returns: True if user is analyst, False otherwise

#### Class: IsExecutive
**Location:** `users/permissions.py`  
**Responsibility:** Permission class to allow only executives.

**Methods:**
- `has_permission(request, view) -> bool`
  - Description: Check if user is authenticated and has executive role.
  - Parameters:
    - `request`: Django request object
    - `view`: View instance
  - Returns: True if user is executive, False otherwise

#### Class: IsManagerOrAnalyst
**Location:** `users/permissions.py`  
**Responsibility:** Permission class to allow managers or analysts.

**Methods:**
- `has_permission(request, view) -> bool`
  - Description: Check if user is authenticated and has manager or analyst role.
  - Parameters:
    - `request`: Django request object
    - `view`: View instance
  - Returns: True if user is manager or analyst, False otherwise

---

### Workspace Management Module

#### Class: Workspace
**Location:** `workspace/models.py`  
**Responsibility:** Workspace model representing a manager's workspace.

**Methods:**
- `__str__() -> str`
  - Description: String representation of workspace.
  - Returns: Formatted string with name and owner email

#### Class: WorkspaceMember
**Location:** `workspace/models.py`  
**Responsibility:** Model representing workspace membership for Analysts and Executives.

**Methods:**
- `__str__() -> str`
  - Description: String representation of workspace member.
  - Returns: Formatted string with user email and workspace name

#### Class: Invitation
**Location:** `workspace/models.py`  
**Responsibility:** Model representing workspace invitations sent to new members.

**Methods:**
- `is_expired() -> bool`
  - Description: Check if invitation has expired (48 hours).
  - Returns: True if expired, False otherwise

- `save(*args, **kwargs) -> None`
  - Description: Set expiration date to 48 hours from creation if not set.
  - Returns: None

- `__str__() -> str`
  - Description: String representation of invitation.
  - Returns: Formatted string with invited email and workspace name

#### Class: WorkspaceUpdateView
**Location:** `workspace/views.py`  
**Responsibility:** API endpoint for updating workspace information.

**Methods:**
- `put(request) -> Response`
  - Description: Update workspace information (name and/or description). Only workspace owner can update.
  - Parameters:
    - `request`: Django request object with update data
  - Returns: Response with updated workspace info

#### Class: WorkspaceMembersView
**Location:** `workspace/views.py`  
**Responsibility:** API endpoint for viewing workspace members list.

**Methods:**
- `get(request) -> Response`
  - Description: Get list of all members in the user's workspace. Managers see all members, others see only active.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with members categorized by status

#### Class: InvitationView
**Location:** `workspace/views.py`  
**Responsibility:** API endpoint for inviting members to workspace.

**Methods:**
- `post(request) -> Response`
  - Description: Send workspace invitation to a new member. Creates WorkspaceMember placeholder and sends email.
  - Parameters:
    - `request`: Django request object with email and role
  - Returns: Response with invitation status

#### Class: RoleAssignmentView
**Location:** `workspace/views.py`  
**Responsibility:** API endpoint for assigning/updating member roles.

**Methods:**
- `put(request, id) -> Response`
  - Description: Update the role of a workspace member. Updates both User and WorkspaceMember models.
  - Parameters:
    - `request`: Django request object with new role
    - `id` (int): Member user ID
  - Returns: Response with updated member info

#### Class: MemberManageView
**Location:** `workspace/views.py`  
**Responsibility:** API endpoint for managing workspace members.

**Methods:**
- `get(request, id) -> Response`
  - Description: Get detailed information about a workspace member.
  - Parameters:
    - `request`: Django request object
    - `id` (int): Member user ID
  - Returns: Response with member details

- `put(request, id) -> Response`
  - Description: Update member status (active/pending).
  - Parameters:
    - `request`: Django request object with status
    - `id` (int): Member user ID
  - Returns: Response with updated member info

- `delete(request, id) -> Response`
  - Description: Remove member from workspace. Expires invitations and removes WorkspaceMember entry.
  - Parameters:
    - `request`: Django request object
    - `id` (int): Member user ID
  - Returns: Response with removal confirmation

#### Class: MemberSuspendView
**Location:** `workspace/views.py`  
**Responsibility:** API endpoint for suspending a member.

**Methods:**
- `put(request, id) -> Response`
  - Description: Suspend a workspace member. Sets is_active=False and updates WorkspaceMember status.
  - Parameters:
    - `request`: Django request object
    - `id` (int): Member user ID
  - Returns: Response with suspension confirmation

#### Class: MemberUnsuspendView
**Location:** `workspace/views.py`  
**Responsibility:** API endpoint for unsuspending a member.

**Methods:**
- `put(request, id) -> Response`
  - Description: Unsuspend a workspace member. Sets is_active=True and updates WorkspaceMember status.
  - Parameters:
    - `request`: Django request object
    - `id` (int): Member user ID
  - Returns: Response with unsuspension confirmation

#### Class: RemovePendingInvitationView
**Location:** `workspace/views.py`  
**Responsibility:** API endpoint for removing pending invitations.

**Methods:**
- `delete(request, email) -> Response`
  - Description: Remove a pending invitation by email. Expires invitations and removes WorkspaceMember entries.
  - Parameters:
    - `request`: Django request object
    - `email` (str): Invited email address
  - Returns: Response with removal confirmation

#### Class: AcceptInvitationView
**Location:** `workspace/views.py`  
**Responsibility:** API endpoint for accepting workspace invitation.

**Methods:**
- `get(request) -> Response`
  - Description: Accept workspace invitation using token. Auto-adds user to workspace if exists, or returns signup info.
  - Parameters:
    - `request`: Django request object with token in query params
  - Returns: Response with acceptance status or signup redirect info

#### Class: WorkspaceUpdateSerializer
**Location:** `workspace/serializers.py`  
**Responsibility:** Serializer for updating workspace information.

**Methods:**
- `validate(attrs) -> dict`
  - Description: Validate that user is the workspace owner.
  - Parameters:
    - `attrs` (dict): Serializer data
  - Returns: Validated data

- `update(instance, validated_data) -> Workspace`
  - Description: Update workspace name and/or description.
  - Parameters:
    - `instance` (Workspace): Workspace instance
    - `validated_data` (dict): Update data
  - Returns: Updated Workspace instance

#### Class: WorkspaceMemberSerializer
**Location:** `workspace/serializers.py`  
**Responsibility:** Serializer for workspace member information.

**Methods:**
- `get_status(obj) -> str`
  - Description: Determine member status based on user state (suspended/pending/active).
  - Parameters:
    - `obj` (WorkspaceMember): WorkspaceMember instance
  - Returns: Status string

#### Class: WorkspaceSerializer
**Location:** `workspace/serializers.py`  
**Responsibility:** Serializer for workspace basic information.

**Methods:** (ModelSerializer - standard Django REST Framework methods)

#### Class: InvitationSerializer
**Location:** `workspace/serializers.py`  
**Responsibility:** Serializer for workspace invitation.

**Methods:**
- `validate(attrs) -> dict`
  - Description: Validate invitation request. Checks for duplicate invitations and existing members.
  - Parameters:
    - `attrs` (dict): Email and role
  - Returns: Validated data with workspace

#### Class: RoleAssignmentSerializer
**Location:** `workspace/serializers.py`  
**Responsibility:** Serializer for assigning/updating member roles.

**Methods:**
- `validate(attrs) -> dict`
  - Description: Validate role assignment request. Ensures user is workspace owner and member exists.
  - Parameters:
    - `attrs` (dict): New role
  - Returns: Validated data with member and workspace

#### Class: MemberDetailSerializer
**Location:** `workspace/serializers.py`  
**Responsibility:** Serializer for member detail view.

**Methods:**
- `get_status(obj) -> str`
  - Description: Determine member status (suspended/pending/active).
  - Parameters:
    - `obj` (User): User instance
  - Returns: Status string

#### Class: MemberUpdateSerializer
**Location:** `workspace/serializers.py`  
**Responsibility:** Serializer for updating member status.

**Methods:**
- `validate(attrs) -> dict`
  - Description: Validate member update request.
  - Parameters:
    - `attrs` (dict): Status update data
  - Returns: Validated data with member and workspace

#### Class: MemberSuspendSerializer
**Location:** `workspace/serializers.py`  
**Responsibility:** Serializer for suspending a member.

**Methods:**
- `validate(attrs) -> dict`
  - Description: Validate member suspension request. Ensures user cannot suspend self or another manager.
  - Parameters:
    - `attrs` (dict): Empty dict (no input needed)
  - Returns: Validated data with member and workspace

#### Class: AcceptInvitationSerializer
**Location:** `workspace/serializers.py`  
**Responsibility:** Serializer for accepting workspace invitation.

**Methods:**
- `validate(attrs) -> dict`
  - Description: Validate invitation token by looking up in Invitation model.
  - Parameters:
    - `attrs` (dict): Token string
  - Returns: Validated data with invitation, workspace, user, and role info

---

### Voice Reports Module

#### Class: VoiceReport
**Location:** `voice_reports/models.py`  
**Responsibility:** Voice-driven BI report with full audit trail linking audio → transcription → SQL → visualization.

**Methods:**
- `can_edit_transcription(user) -> bool`
  - Description: Check if user can edit transcription.
  - Parameters:
    - `user` (User): User instance
  - Returns: True if user is manager or analyst

- `can_edit_sql(user) -> bool`
  - Description: Check if user can edit SQL.
  - Parameters:
    - `user` (User): User instance
  - Returns: True if user is analyst

- `can_delete(user) -> bool`
  - Description: Check if user can delete report.
  - Parameters:
    - `user` (User): User instance
  - Returns: True if user is manager

- `__str__() -> str`
  - Description: String representation of report.
  - Returns: Formatted string with title and workspace name

#### Class: SQLEditHistory
**Location:** `voice_reports/models.py`  
**Responsibility:** Track all SQL edits for audit purposes.

**Methods:**
- `__str__() -> str`
  - Description: String representation of SQL edit history entry.
  - Returns: Formatted string with report ID and editor email

#### Class: DashboardPage
**Location:** `voice_reports/models.py`  
**Responsibility:** Dashboard pages/tabs for organizing reports.

**Methods:**
- `__str__() -> str`
  - Description: String representation of dashboard page.
  - Returns: Formatted string with name and workspace name

#### Class: ReportPageAssignment
**Location:** `voice_reports/models.py`  
**Responsibility:** Many-to-many relationship between reports and dashboard pages.

**Methods:**
- `__str__() -> str`
  - Description: String representation of report page assignment.
  - Returns: Formatted string with report and page names

#### Class: VoiceUploadView
**Location:** `voice_reports/views.py`  
**Responsibility:** Upload audio file and get transcription + generated SQL from Small Whisper.

**Methods:**
- `post(request) -> Response`
  - Description: Handle audio upload, call Small Whisper service, create report record.
  - Parameters:
    - `request`: Django request object with audio file
  - Returns: Response with transcription, SQL, intent, and report ID

#### Class: QueryExecuteView
**Location:** `voice_reports/views.py`  
**Responsibility:** Execute SQL query on ClickHouse and create Metabase visualization.

**Methods:**
- `post(request, report_id) -> Response`
  - Description: Execute SQL query, validate with SQL Guard, execute on ClickHouse, create Metabase question/dashboard.
  - Parameters:
    - `request`: Django request object
    - `report_id` (int): Report ID
  - Returns: Response with query results, chart type, and embed URL

- `_infer_chart_type(columns, rows, intent) -> str`
  - Description: Infer appropriate chart type from data and intent.
  - Parameters:
    - `columns` (list): Column names
    - `rows` (list): Query result rows
    - `intent` (dict): Intent JSON
  - Returns: Chart type string

- `_get_or_create_dashboard(workspace, metabase) -> int | None`
  - Description: Get or create Metabase dashboard for workspace.
  - Parameters:
    - `workspace` (Workspace): Workspace instance
    - `metabase` (MetabaseService): Metabase service instance
  - Returns: Dashboard ID or None

#### Class: SQLEditView
**Location:** `voice_reports/views.py`  
**Responsibility:** Edit SQL query (Analyst only).

**Methods:**
- `put(request, report_id) -> Response`
  - Description: Edit SQL query with validation. Updates report and creates history entry.
  - Parameters:
    - `request`: Django request object with new SQL
    - `report_id` (int): Report ID
  - Returns: Response with updated SQL

#### Class: ReportListView
**Location:** `voice_reports/views.py`  
**Responsibility:** List all reports for workspace.

**Methods:**
- `get(request) -> Response`
  - Description: Get list of all reports for user's workspace. Filters by role.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with list of reports

#### Class: ReportDetailView
**Location:** `voice_reports/views.py`  
**Responsibility:** Get detailed report information.

**Methods:**
- `get(request, report_id) -> Response`
  - Description: Get detailed report information including SQL, results, and history.
  - Parameters:
    - `request`: Django request object
    - `report_id` (int): Report ID
  - Returns: Response with full report details

- `delete(request, report_id) -> Response`
  - Description: Delete report (Manager only).
  - Parameters:
    - `request`: Django request object
    - `report_id` (int): Report ID
  - Returns: Response with deletion confirmation

#### Class: WorkspaceDashboardView
**Location:** `voice_reports/views.py`  
**Responsibility:** Get workspace dashboard for embedded viewing (Executive).

**Methods:**
- `get(request) -> Response`
  - Description: Get workspace dashboard embed URL for Metabase.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with dashboard embed URL

#### Class: HealthCheckView
**Location:** `voice_reports/views.py`  
**Responsibility:** Health check for all services.

**Methods:**
- `get(request) -> Response`
  - Description: Check connectivity to Small Whisper, ClickHouse, and Metabase.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with health status of all services

#### Class: ClickHouseExecutor
**Location:** `voice_reports/services/clickhouse_executor.py`  
**Responsibility:** Execute SELECT queries on ClickHouse using HTTP protocol.

**Methods:**
- `__init__() -> None`
  - Description: Initialize ClickHouse executor with environment configuration.
  - Returns: None

- `execute_query(sql) -> dict`
  - Description: Execute SQL query on ClickHouse. Sanitizes results for JSON compatibility.
  - Parameters:
    - `sql` (str): SQL query (must be SELECT only)
  - Returns: Dict with success, rows, columns, row_count, execution_time_ms, error

- `test_connection() -> bool`
  - Description: Test ClickHouse connection.
  - Returns: True if connected, False otherwise

- `get_tables(database=None) -> list`
  - Description: Get list of tables in database.
  - Parameters:
    - `database` (str, optional): Database name
  - Returns: List of table names

- `get_table_schema(table_name, database=None) -> dict`
  - Description: Get schema for a table.
  - Parameters:
    - `table_name` (str): Table name
    - `database` (str, optional): Database name
  - Returns: Dict with schema information

#### Class: SmallWhisperClient
**Location:** `voice_reports/services/small_whisper_client.py`  
**Responsibility:** Client for calling Small Whisper service (stateless AI worker).

**Methods:**
- `__init__() -> None`
  - Description: Initialize client with Small Whisper endpoint.
  - Returns: None

- `check_health() -> bool`
  - Description: Check if Small Whisper service is reachable.
  - Returns: True if service is reachable, False otherwise

- `process_audio(audio_file) -> dict`
  - Description: Send audio to Small Whisper and get back transcription + reasoning + intent/SQL.
  - Parameters:
    - `audio_file`: Audio file (Django UploadedFile or file path)
  - Returns: Dict with success, text, reasoning, intent, sql, chart, question_type, error

#### Class: JWTEmbeddingService
**Location:** `voice_reports/services/jwt_embedding.py`  
**Responsibility:** JWT token generation for secure Metabase embedding.

**Methods:**
- `__init__() -> None`
  - Description: Initialize JWT service with secret key from environment.
  - Returns: None

- `generate_embed_token(resource, params=None, exp_minutes=10) -> str`
  - Description: Generate JWT token for embedding.
  - Parameters:
    - `resource` (dict): {'type': 'dashboard'|'question', 'id': int}
    - `params` (dict, optional): Optional parameters
    - `exp_minutes` (int): Token expiration in minutes
  - Returns: JWT token string

- `generate_dashboard_token(dashboard_id, params=None) -> str`
  - Description: Generate token specifically for dashboard embedding.
  - Parameters:
    - `dashboard_id` (int): Metabase dashboard ID
    - `params` (dict, optional): Optional dashboard parameters
  - Returns: JWT token string

- `generate_question_token(question_id, params=None) -> str`
  - Description: Generate token specifically for question embedding.
  - Parameters:
    - `question_id` (int): Metabase question ID
    - `params` (dict, optional): Optional question parameters
  - Returns: JWT token string

- `get_embed_url(resource_type, resource_id, params=None) -> str`
  - Description: Get full embed URL with JWT token.
  - Parameters:
    - `resource_type` (str): 'dashboard' or 'question'
    - `resource_id` (int): Resource ID
    - `params` (dict, optional): Optional parameters
  - Returns: Full embed URL with JWT token

- `get_dashboard_embed_url(dashboard_id, workspace_id=None) -> str`
  - Description: Get dashboard embed URL with workspace filtering.
  - Parameters:
    - `dashboard_id` (int): Metabase dashboard ID
    - `workspace_id` (int, optional): Workspace ID for filtering
  - Returns: Dashboard embed URL

- `get_question_embed_url(question_id, workspace_id=None) -> str`
  - Description: Get question embed URL with workspace filtering.
  - Parameters:
    - `question_id` (int): Metabase question ID
    - `workspace_id` (int, optional): Workspace ID for filtering
  - Returns: Question embed URL

- `verify_token(token) -> dict | None`
  - Description: Verify and decode JWT token.
  - Parameters:
    - `token` (str): JWT token string
  - Returns: Decoded payload or None if invalid

- `is_token_expired(token) -> bool`
  - Description: Check if token is expired.
  - Parameters:
    - `token` (str): JWT token string
  - Returns: True if expired or invalid

#### Class: MetabaseService
**Location:** `voice_reports/services/metabase_service.py`  
**Responsibility:** Metabase API integration service for creating questions and dashboards.

**Methods:**
- `__init__() -> None`
  - Description: Initialize Metabase service with environment configuration.
  - Returns: None

- `authenticate(username=None, password=None) -> bool`
  - Description: Authenticate with Metabase and get session token.
  - Parameters:
    - `username` (str, optional): Metabase admin username
    - `password` (str, optional): Metabase admin password
  - Returns: True if successful, False otherwise

- `_get_headers() -> dict`
  - Description: Get request headers with session token.
  - Returns: Dict with X-Metabase-Session and Content-Type headers

- `create_question(name, sql, description="", visualization_settings=None) -> int | None`
  - Description: Create a Metabase question (saved query).
  - Parameters:
    - `name` (str): Question name
    - `sql` (str): SQL query (native query)
    - `description` (str): Question description
    - `visualization_settings` (dict, optional): Chart configuration
  - Returns: Question ID or None if failed

- `create_dashboard(name, description="") -> int | None`
  - Description: Create a Metabase dashboard.
  - Parameters:
    - `name` (str): Dashboard name
    - `description` (str): Dashboard description
  - Returns: Dashboard ID or None if failed

- `add_question_to_dashboard(question_id, dashboard_id, row=0, col=0, size_x=6, size_y=4) -> bool`
  - Description: Add a question to a dashboard.
  - Parameters:
    - `question_id` (int): Question ID
    - `dashboard_id` (int): Dashboard ID
    - `row` (int): Row position
    - `col` (int): Column position
    - `size_x` (int): Width in grid units
    - `size_y` (int): Height in grid units
  - Returns: True if successful, False otherwise

- `get_dashboard(dashboard_id) -> dict | None`
  - Description: Get dashboard details.
  - Parameters:
    - `dashboard_id` (int): Dashboard ID
  - Returns: Dashboard data or None

- `delete_question(question_id) -> bool`
  - Description: Delete a question.
  - Parameters:
    - `question_id` (int): Question ID
  - Returns: True if successful, False otherwise

- `enable_dashboard_embedding(dashboard_id) -> bool`
  - Description: Enable embedding for a dashboard.
  - Parameters:
    - `dashboard_id` (int): Dashboard ID
  - Returns: True if successful, False otherwise

- `enable_question_embedding(question_id) -> bool`
  - Description: Enable embedding for a question.
  - Parameters:
    - `question_id` (int): Question ID
  - Returns: True if successful, False otherwise

#### Class: SQLGuard
**Location:** `voice_reports/services/sql_guard.py`  
**Responsibility:** Enforces read-only SQL execution and workspace isolation.

**Methods:**
- `__init__(workspace_database=None) -> None`
  - Description: Initialize SQL Guard.
  - Parameters:
    - `workspace_database` (str, optional): Database name for workspace isolation
  - Returns: None

- `validate_sql(sql) -> tuple`
  - Description: Validate SQL query for security and correctness.
  - Parameters:
    - `sql` (str): SQL query to validate
  - Returns: Tuple of (is_valid, error_message, validation_details)

- `sanitize_sql(sql) -> str`
  - Description: Sanitize SQL by removing comments and normalizing whitespace.
  - Parameters:
    - `sql` (str): SQL query
  - Returns: Sanitized SQL

- `enforce_workspace_database(sql) -> str`
  - Description: Ensure all table references use workspace database.
  - Parameters:
    - `sql` (str): SQL query
  - Returns: SQL with workspace database enforced

- `validate_and_sanitize(sql) -> tuple`
  - Description: Combined validation and sanitization.
  - Parameters:
    - `sql` (str): SQL query
  - Returns: Tuple of (is_valid, error_message, sanitized_sql)

#### Class: SQLGuardFactory
**Location:** `voice_reports/services/sql_guard.py`  
**Responsibility:** Factory for creating SQL Guards with workspace isolation.

**Methods:**
- `create_for_workspace(workspace) -> SQLGuard` (static)
  - Description: Create SQL Guard for specific workspace.
  - Parameters:
    - `workspace` (Workspace): Workspace model instance
  - Returns: Configured SQLGuard instance

- `create_default() -> SQLGuard` (static)
  - Description: Create SQL Guard with no workspace isolation.
  - Returns: SQLGuard instance

#### Class: WhisperIntegrationService
**Location:** `voice_reports/services/whisper_service.py`  
**Responsibility:** Integration service that calls existing Whisper STT model.

**Methods:**
- `__init__() -> None`
  - Description: Initialize Whisper integration by importing existing modules.
  - Returns: None

- `_setup_small_whisper_path() -> None`
  - Description: Add Small Whisper to Python path.
  - Returns: None

- `_import_whisper_components() -> None`
  - Description: Import existing Whisper model and components.
  - Returns: None

- `transcribe_audio(audio_file_path, language='en', task='transcribe') -> dict`
  - Description: Transcribe audio using existing Whisper model.
  - Parameters:
    - `audio_file_path` (str): Path to audio file
    - `language` (str): Language code
    - `task` (str): 'transcribe' or 'translate'
  - Returns: Dict with text, language, segments, duration

- `transcribe_from_django_file(django_file) -> dict`
  - Description: Transcribe audio from Django UploadedFile.
  - Parameters:
    - `django_file`: Django UploadedFile object
  - Returns: Transcription result dict

- `process_full_pipeline(text) -> dict`
  - Description: Process text through existing Text-to-SQL pipeline.
  - Parameters:
    - `text` (str): Transcribed text
  - Returns: Dict with reasoning and LLM output

---

### Database Management Module

#### Class: Database
**Location:** `database/models.py`  
**Responsibility:** Model representing a manager's uploaded database.

**Methods:**
- `get_preview_data() -> list`
  - Description: Returns preview data from ClickHouse (first 5 rows).
  - Returns: List of preview rows (TODO: implement ClickHouse query)

- `__str__() -> str`
  - Description: String representation of database.
  - Returns: Formatted string with filename and manager email

#### Class: DatabaseHealthCheckView
**Location:** `database/views.py`  
**Responsibility:** Health check endpoint to verify database module is loaded.

**Methods:**
- `get(request) -> Response`
  - Description: Health check for database module and ETL service connectivity.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with system status

#### Class: DatabaseUploadView
**Location:** `database/views.py`  
**Responsibility:** Handle database file upload for managers.

**Methods:**
- `post(request) -> Response`
  - Description: Upload database file with defensive error handling. Forwards to ETL service.
  - Parameters:
    - `request`: Django request object with file
  - Returns: Response with upload status and database record

#### Class: DatabaseDetailView
**Location:** `database/views.py`  
**Responsibility:** Handle database operations for the authenticated manager.

**Methods:**
- `get(request) -> Response`
  - Description: Get manager's database information. Automatically checks ClickHouse and updates status if processing.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with database information

- `_check_and_update_etl_status(database) -> bool`
  - Description: Check ClickHouse for table existence and data. Update database status, row count, and column count if ready.
  - Parameters:
    - `database` (Database): Database instance
  - Returns: True if status was updated, False otherwise

- `delete(request) -> Response`
  - Description: Delete manager's database. Cleans up ClickHouse and other resources.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with deletion confirmation

#### Class: DatabasePreviewView
**Location:** `database/views.py`  
**Responsibility:** Get preview data from the manager's database.

**Methods:**
- `get(request) -> Response`
  - Description: Get database preview (first 5 rows and schema information).
  - Parameters:
    - `request`: Django request object
  - Returns: Response with preview data and schema

#### Class: DatabaseStatusView
**Location:** `database/views.py`  
**Responsibility:** Update database status (called by ETL service after processing).

**Methods:**
- `put(request, database_id) -> Response`
  - Description: Update database ETL status and metadata.
  - Parameters:
    - `request`: Django request object with status data
    - `database_id` (int): Database ID
  - Returns: Response with update confirmation

#### Class: DatabaseSerializer
**Location:** `database/serializers.py`  
**Responsibility:** Serializer for Database model.

**Methods:** (ModelSerializer - standard Django REST Framework methods)

#### Class: DatabaseUploadResponseSerializer
**Location:** `database/serializers.py`  
**Responsibility:** Serializer for database upload response.

**Methods:** (Standard serializer methods)

#### Class: DatabasePreviewSerializer
**Location:** `database/serializers.py`  
**Responsibility:** Serializer for database preview data.

**Methods:** (Standard serializer methods)

#### Class: ClickHouseClient
**Location:** `database/utils.py`  
**Responsibility:** Client for interacting with ClickHouse database.

**Methods:**
- `__init__() -> None`
  - Description: Initialize ClickHouse client with settings.
  - Returns: None

- `execute_query(query) -> dict`
  - Description: Execute a query on ClickHouse.
  - Parameters:
    - `query` (str): SQL query
  - Returns: Dict with success and data

- `drop_table(database, table_name) -> dict`
  - Description: Drop a table from ClickHouse.
  - Parameters:
    - `database` (str): Database name
    - `table_name` (str): Table name
  - Returns: Dict with success status

- `get_table_preview(database, table_name, limit=5) -> dict`
  - Description: Get preview data from a ClickHouse table.
  - Parameters:
    - `database` (str): Database name
    - `table_name` (str): Table name
    - `limit` (int): Number of rows to return
  - Returns: Dict with success and rows

- `get_table_schema(database, table_name) -> dict`
  - Description: Get schema information for a table.
  - Parameters:
    - `database` (str): Database name
    - `table_name` (str): Table name
  - Returns: Dict with success and schema

- `get_table_count(database, table_name) -> dict`
  - Description: Get row count for a table.
  - Parameters:
    - `database` (str): Database name
    - `table_name` (str): Table name
  - Returns: Dict with success and count

- `table_exists(database, table_name) -> dict`
  - Description: Check if a table exists in ClickHouse.
  - Parameters:
    - `database` (str): Database name
    - `table_name` (str): Table name
  - Returns: Dict with success and exists boolean

- `get_all_tables(database='default') -> dict`
  - Description: Get list of all tables in a database.
  - Parameters:
    - `database` (str): Database name
  - Returns: Dict with success and tables list

---

## Backend - Small Whisper (AI Module)

### LLM Application Module

#### Class: Intent
**Location:** `Small Whisper/backend/shared/intent_schema.py`  
**Responsibility:** Pydantic model for structured intent representation.

**Fields:**
- `table` (str): Table name
- `metrics` (List[Metric]): List of metrics
- `dimensions` (List[str]): List of dimension columns
- `filters` (List[Filter]): List of filter conditions
- `order_by` (List[dict]): List of ordering specifications
- `limit` (Optional[int]): Result limit

#### Class: Metric
**Location:** `Small Whisper/backend/shared/intent_schema.py`  
**Responsibility:** Pydantic model for metric specification.

**Fields:**
- `column` (str): Column name
- `aggregation` (str): Aggregation function (SUM, AVG, COUNT, etc.)
- `alias` (Optional[str]): Alias for the metric

#### Class: Filter
**Location:** `Small Whisper/backend/shared/intent_schema.py`  
**Responsibility:** Pydantic model for filter condition.

**Fields:**
- `column` (str): Column name
- `operator` (str): Comparison operator
- `value` (str): Filter value

#### Class: QueryState
**Location:** `Small Whisper/backend/reasoning_app/states.py`  
**Responsibility:** TypedDict for reasoning graph state.

**Fields:**
- `text` (str): Input text
- `needs_sql` (bool): Whether SQL is needed
- `needs_chart` (bool): Whether chart is needed
- `question_type` (str): Question type (analytical/informational/error)
- `error` (Optional[str]): Error message if any

### Functions (Non-Class)

#### Function: call_llm
**Location:** `Small Whisper/backend/llm_app/llm_client.py`  
**Responsibility:** Call LLM via OpenRouter.

**Parameters:**
- `prompt` (str): The text prompt to send to the LLM

**Returns:**
- `str`: Raw text response from the LLM

**Raises:**
- `ValueError`: If OpenRouter API key is invalid or expired
- `RuntimeError`: For other API errors

#### Function: extract_intent
**Location:** `Small Whisper/backend/llm_app/intent_service.py`  
**Responsibility:** Extract structured intent from question using LLM.

**Parameters:**
- `question` (str): Natural language question

**Returns:**
- `dict`: Dict with error, intent, schema, matches_schema

#### Function: compile_sql
**Location:** `Small Whisper/backend/shared/sql_compiler.py`  
**Responsibility:** Compile intent into SQL with optional type casting.

**Parameters:**
- `intent` (dict): Structured intent with metrics, dimensions, filters, etc.
- `type_casting` (list, optional): List of type casting requirements from validation

**Returns:**
- `str`: Valid SQL query string

**Raises:**
- `ValueError`: If intent is invalid or SQL cannot be generated

#### Function: validate_intent_semantics
**Location:** `Small Whisper/backend/shared/intent_validator.py`  
**Responsibility:** Pass 1: Domain & Intent Validation with Intra-Domain Semantic Resolution.

**Parameters:**
- `intent` (dict): Extracted intent
- `question` (str): Original question
- `schema` (dict): Database schema

**Returns:**
- `dict`: Validation result with valid, issues, warnings

#### Function: validate_schema_and_types
**Location:** `Small Whisper/backend/shared/intent_validator.py`  
**Responsibility:** Pass 2: Schema & Type Validation with Type Repair.

**Parameters:**
- `intent` (dict): Extracted intent
- `schema` (dict): Database schema

**Returns:**
- `dict`: Validation result with valid, issues, type_casting

#### Function: validate_sql_executability
**Location:** `Small Whisper/backend/shared/intent_validator.py`  
**Responsibility:** Pass 3: SQL Executability Validation.

**Parameters:**
- `sql` (str): SQL query
- `intent` (dict): Structured intent
- `schema` (dict): Database schema

**Returns:**
- `dict`: Validation result with valid, issues, warnings

#### Function: perform_multi_pass_validation
**Location:** `Small Whisper/backend/shared/intent_validator.py`  
**Responsibility:** Perform all three validation passes and return comprehensive results.

**Parameters:**
- `intent` (dict): Extracted intent
- `sql` (str): SQL query
- `question` (str): Original question
- `schema` (dict): Database schema

**Returns:**
- `dict`: Comprehensive validation results with all passes

#### Function: process_question
**Location:** `Small Whisper/backend/shared/pipeline.py`  
**Responsibility:** Full analytical pipeline: Intent → SQL → Chart with strict multi-pass validation.

**Parameters:**
- `question` (str): Natural language question

**Returns:**
- `dict`: Dict with intent, sql, chart, confidence, validation

#### Function: process_after_whisper
**Location:** `Small Whisper/backend/shared/pipeline.py`  
**Responsibility:** Complete pipeline after Whisper transcription: Reasoning → Intent extraction → SQL + Chart.

**Parameters:**
- `text` (str): Transcribed text from Whisper

**Returns:**
- `tuple`: Tuple of (reasoning_result, llm_result)

#### Function: classify_question
**Location:** `Small Whisper/backend/reasoning_app/llm_intent_client.py`  
**Responsibility:** Classify whether a question needs SQL and chart generation.

**Parameters:**
- `question` (str): Natural language question

**Returns:**
- `dict`: Dict with needs_sql, needs_chart, question_type

#### Function: intent_llm_node
**Location:** `Small Whisper/backend/reasoning_app/nodes/intent_llm_node.py`  
**Responsibility:** LangGraph node for intent classification.

**Parameters:**
- `state` (QueryState): Graph state

**Returns:**
- `QueryState`: Updated state with classification results

#### Function: routing_node
**Location:** `Small Whisper/backend/reasoning_app/nodes/routing_node.py`  
**Responsibility:** Decide graph routing based on intent classification.

**Parameters:**
- `state` (QueryState): Graph state

**Returns:**
- `str`: Route name ('analytical', 'non_analytical', 'error')

#### Function: build_graph
**Location:** `Small Whisper/backend/reasoning_app/graph.py`  
**Responsibility:** Build LangGraph state graph for reasoning pipeline.

**Returns:**
- Compiled graph instance

#### Function: run_reasoning
**Location:** `Small Whisper/backend/reasoning_app/runner.py`  
**Responsibility:** Run reasoning graph on input text.

**Parameters:**
- `text` (str): Input text

**Returns:**
- `QueryState`: Final state after reasoning

---

## ETL Pipeline Services

### Connector Service

#### Class: UploadFileView
**Location:** `etl-final/connector-service/connector/etl_engine/views.py`  
**Responsibility:** Handle file upload for ETL pipeline.

**Methods:**
- `post(request) -> Response`
  - Description: Upload file and emit connection message to Kafka.
  - Parameters:
    - `request`: Django request object with file
  - Returns: Response with upload status

#### Class: ConnectDBView
**Location:** `etl-final/connector-service/connector/etl_engine/views.py`  
**Responsibility:** Handle database connection for ETL pipeline.

**Methods:**
- `post(request) -> Response`
  - Description: Connect to database and emit connection message to Kafka.
  - Parameters:
    - `request`: Django request object with database connection info
  - Returns: Response with connection status

### Detector Service

#### Class: RunDetectorView
**Location:** `etl-final/detector-service/detector/core/views.py`  
**Responsibility:** Trigger schema detection.

**Methods:**
- `post(request) -> Response`
  - Description: Run schema detection and emit schema message to Kafka.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with detection status

#### Class: SchemaExtractor
**Location:** `etl-final/detector-service/detector/core/schema_extractor.py`  
**Responsibility:** Extract schema from data source.

**Methods:**
- `extract_schema(source_type, source_info) -> dict`
  - Description: Extract schema from file or database.
  - Parameters:
    - `source_type` (str): 'file' or 'database'
    - `source_info` (dict): Source connection information
  - Returns: Dict with schema information

### Extractor Service

#### Class: RunExtractorView
**Location:** `etl-final/extractor-service/extractor/engine/views.py`  
**Responsibility:** Trigger row extraction.

**Methods:**
- `post(request) -> Response`
  - Description: Run row extraction and emit extracted rows to Kafka.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with extraction status

#### Class: ConnectionListener
**Location:** `etl-final/extractor-service/extractor/engine/kafka_listener.py`  
**Responsibility:** Kafka listener for connection messages.

**Methods:**
- `__init__() -> None`
  - Description: Initialize connection listener.
  - Returns: None

- `listen() -> Generator`
  - Description: Listen for connection messages and trigger extraction.
  - Returns: Generator yielding messages

#### Class: RowExtractor
**Location:** `etl-final/extractor-service/extractor/engine/row_extractor.py`  
**Responsibility:** Extract rows from data source.

**Methods:**
- `extract_rows(source_type, source_info) -> Generator`
  - Description: Extract rows from file or database.
  - Parameters:
    - `source_type` (str): 'file' or 'database'
    - `source_info` (dict): Source connection information
  - Returns: Generator yielding row dictionaries

#### Class: DBConnector
**Location:** `etl-final/extractor-service/extractor/engine/db_connector.py`  
**Responsibility:** Database connection handler.

**Methods:**
- `connect(db_type, host, port, user, password, database) -> connection`
  - Description: Connect to database.
  - Parameters:
    - `db_type` (str): Database type (MySQL, PostgreSQL, etc.)
    - `host` (str): Database host
    - `port` (int): Database port
    - `user` (str): Database user
    - `password` (str): Database password
    - `database` (str): Database name
  - Returns: Database connection object

### Transformer Service

#### Class: TestTransformView
**Location:** `etl-final/transformer-service/transformer/engine/views.py`  
**Responsibility:** Test transformation endpoint.

**Methods:**
- `post(request) -> Response`
  - Description: Test transformation logic.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with transformation test results

#### Class: RawRowListener
**Location:** `etl-final/transformer-service/transformer/engine/kafka_listener.py`  
**Responsibility:** Kafka listener for raw extracted rows.

**Methods:**
- `__init__() -> None`
  - Description: Initialize raw row listener.
  - Returns: None

- `listen() -> Generator`
  - Description: Listen for extracted rows, clean them, and emit to clean_rows_topic.
  - Returns: Generator yielding cleaned rows

#### Class: TransformerLogic
**Location:** `etl-final/transformer-service/transformer/engine/transformer_logic.py`  
**Responsibility:** High-level transformer logic for data cleaning.

**Methods:**
- `__init__() -> None`
  - Description: Initialize transformer logic with cleaning rules.
  - Returns: None

- `transform_row(row, schema) -> dict`
  - Description: Transform a single row using cleaning rules.
  - Parameters:
    - `row` (dict): Raw row data
    - `schema` (dict): Schema information
  - Returns: Cleaned row dictionary

- `transform_batch(rows, schema) -> list`
  - Description: Transform multiple rows in batch.
  - Parameters:
    - `rows` (list): List of raw row dictionaries
    - `schema` (dict): Schema information
  - Returns: List of cleaned row dictionaries

#### Class: CleaningRules
**Location:** `etl-final/transformer-service/transformer/engine/cleaning_rules.py`  
**Responsibility:** Data cleaning rules for transformation.

**Methods:**
- `__init__() -> None`
  - Description: Initialize cleaning rules.
  - Returns: None

- `clean_value(value, dtype) -> Any`
  - Description: Clean a single value based on data type.
  - Parameters:
    - `value`: Value to clean
    - `dtype` (str): Data type
  - Returns: Cleaned value

- `clean_row(row, schema) -> dict`
  - Description: Clean an entire row using all applicable rules.
  - Parameters:
    - `row` (dict): Row dictionary
    - `schema` (dict): Schema information
  - Returns: Cleaned row dictionary

### Loader Service

#### Class: TestLoaderView
**Location:** `etl-final/loader-service/loader/engine/views.py`  
**Responsibility:** Test loader endpoint.

**Methods:**
- `post(request) -> Response`
  - Description: Test loader logic.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with loader test results

#### Class: CleanRowListener
**Location:** `etl-final/loader-service/loader/engine/kafka_listener.py`  
**Responsibility:** Enhanced listener for clean_rows_topic with batch loading.

**Methods:**
- `__init__(batch_size=1000) -> None`
  - Description: Initialize listener with batch size.
  - Parameters:
    - `batch_size` (int): Batch size for inserts
  - Returns: None

- `listen() -> Generator`
  - Description: Listen for clean rows, batch them, and load into ClickHouse.
  - Returns: Generator yielding load status messages

#### Class: LoaderLogic
**Location:** `etl-final/loader-service/loader/engine/loader_logic.py`  
**Responsibility:** High-level loader logic for ClickHouse operations.

**Methods:**
- `__init__(config) -> None`
  - Description: Initialize loader logic using ClickHouse native protocol.
  - Parameters:
    - `config` (dict): Configuration dictionary with ClickHouse connection details
  - Returns: None

- `load_row(table, row) -> None`
  - Description: Load a single row into ClickHouse.
  - Parameters:
    - `table` (str): Table name
    - `row` (dict): Row dictionary
  - Returns: None

- `load_batch(table, rows, batch_size=1000) -> int`
  - Description: Load multiple rows in batch.
  - Parameters:
    - `table` (str): Table name
    - `rows` (list): List of row dictionaries
    - `batch_size` (int): Batch size for inserts
  - Returns: Number of rows successfully inserted

#### Class: ClickHouseClient
**Location:** `etl-final/loader-service/loader/engine/clickhouse_client.py`  
**Responsibility:** Enhanced ClickHouse client with batch insert support.

**Methods:**
- `__init__(host, port=9000, user="default", password="", database="default") -> None`
  - Description: Initialize ClickHouse client using NATIVE protocol (clickhouse_driver).
  - Parameters:
    - `host` (str): ClickHouse host
    - `port` (int): ClickHouse native protocol port (default: 9000)
    - `user` (str): Username
    - `password` (str): Password
    - `database` (str): Database name
  - Returns: None

- `insert_row(table, row) -> None`
  - Description: Insert a single row into ClickHouse.
  - Parameters:
    - `table` (str): Table name
    - `row` (dict): Row dictionary
  - Returns: None

- `insert_batch(table, rows, batch_size=1000) -> int`
  - Description: Insert multiple rows in batch for performance.
  - Parameters:
    - `table` (str): Table name
    - `rows` (list): List of row dictionaries
    - `batch_size` (int): Batch size
  - Returns: Number of rows successfully inserted

- `create_table_if_not_exists(table, schema) -> None`
  - Description: Create table if it doesn't exist.
  - Parameters:
    - `table` (str): Table name
    - `schema` (dict): Schema definition
  - Returns: None

### Metadata Service

#### Class: BaseLogView
**Location:** `etl-final/metadata-service/metadata/api/views.py`  
**Responsibility:** Base view for log retrieval.

**Methods:**
- `get(request) -> Response`
  - Description: Get logs from SurrealDB.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with logs

#### Class: ConnectionLogsView
**Location:** `etl-final/metadata-service/metadata/api/views.py`  
**Responsibility:** View for connection stage logs.

**Methods:**
- `get(request) -> Response`
  - Description: Get connection logs.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with connection logs

#### Class: SchemaLogsView
**Location:** `etl-final/metadata-service/metadata/api/views.py`  
**Responsibility:** View for schema extraction logs.

**Methods:**
- `get(request) -> Response`
  - Description: Get schema logs.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with schema logs

#### Class: ExtractLogsView
**Location:** `etl-final/metadata-service/metadata/api/views.py`  
**Responsibility:** View for extraction stage logs.

**Methods:**
- `get(request) -> Response`
  - Description: Get extraction logs.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with extraction logs

#### Class: TransformLogsView
**Location:** `etl-final/metadata-service/metadata/api/views.py`  
**Responsibility:** View for transformation stage logs.

**Methods:**
- `get(request) -> Response`
  - Description: Get transformation logs.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with transformation logs

#### Class: LoadLogsView
**Location:** `etl-final/metadata-service/metadata/api/views.py`  
**Responsibility:** View for loading stage logs.

**Methods:**
- `get(request) -> Response`
  - Description: Get loading logs.
  - Parameters:
    - `request`: Django request object
  - Returns: Response with loading logs

#### Class: MetadataListener
**Location:** `etl-final/metadata-service/metadata/api/kafka_listener.py`  
**Responsibility:** Kafka listener for metadata messages.

**Methods:**
- `__init__() -> None`
  - Description: Initialize metadata listener.
  - Returns: None

- `listen() -> Generator`
  - Description: Listen for metadata messages and store in SurrealDB.
  - Returns: Generator yielding metadata messages

#### Class: LogSerializer
**Location:** `etl-final/metadata-service/metadata/api/serializers.py`  
**Responsibility:** Serializer for log entries.

**Methods:** (Standard serializer methods)

### Shared ETL Utilities

#### Class: KafkaMessageConsumer
**Location:** `etl-final/shared/utils/kafka_consumer.py`  
**Responsibility:** Enhanced Kafka message consumer with validation and error handling.

**Methods:**
- `__init__(topic, consumer_group=None, validate_messages=True) -> None`
  - Description: Initialize Kafka consumer.
  - Parameters:
    - `topic` (str): Kafka topic name
    - `consumer_group` (str, optional): Consumer group ID
    - `validate_messages` (bool): Whether to validate message schemas
  - Returns: None

- `connect() -> None`
  - Description: Connect to Kafka with infinite retry.
  - Returns: None

- `_validate_message(message) -> tuple`
  - Description: Validate message schema based on topic.
  - Parameters:
    - `message` (dict): Message dictionary
  - Returns: Tuple of (is_valid, error_message)

- `listen() -> Generator`
  - Description: Listen for messages on topic.
  - Returns: Generator yielding validated messages

- `close() -> None`
  - Description: Close consumer connection.
  - Returns: None

#### Class: KafkaMessageProducer
**Location:** `etl-final/shared/utils/kafka_producer.py`  
**Responsibility:** Enhanced Kafka message producer with validation and error handling.

**Methods:**
- `__init__(validate_messages=True) -> None`
  - Description: Initialize Kafka producer.
  - Parameters:
    - `validate_messages` (bool): Whether to validate message schemas before sending
  - Returns: None

- `_validate_message(topic, message) -> tuple`
  - Description: Validate message schema based on topic.
  - Parameters:
    - `topic` (str): Kafka topic name
    - `message` (dict): Message dictionary
  - Returns: Tuple of (is_valid, error_message)

- `send(topic, message, validate=None) -> bool`
  - Description: Send message to Kafka topic with validation.
  - Parameters:
    - `topic` (str): Kafka topic name
    - `message` (dict): Message dictionary
    - `validate` (bool, optional): Override validation flag
  - Returns: True if sent successfully, False otherwise

- `flush() -> None`
  - Description: Flush all pending messages.
  - Returns: None

- `close() -> None`
  - Description: Close producer connection.
  - Returns: None

#### Class: SurrealClient
**Location:** `etl-final/shared/utils/surreal_client.py`  
**Responsibility:** Client for interacting with SurrealDB.

**Methods:**
- `__init__() -> None`
  - Description: Initialize SurrealDB client with environment configuration.
  - Returns: None

- `query(sql) -> dict | None`
  - Description: Execute SQL query on SurrealDB.
  - Parameters:
    - `sql` (str): SQL query string
  - Returns: Query result dict or None on error

- `insert(table, record) -> dict | None`
  - Description: Insert a record into SurrealDB table.
  - Parameters:
    - `table` (str): Table name
    - `record` (dict): Record dictionary
  - Returns: Insert result or None on error

#### Class: MessageValidator
**Location:** `etl-final/shared/utils/message_validator.py`  
**Responsibility:** Validates message schemas for each Kafka topic.

**Methods:**
- `validate_connection_message(message) -> tuple` (static)
  - Description: Validate connection_topic message structure.
  - Parameters:
    - `message` (dict): Message dictionary
  - Returns: Tuple of (is_valid, error_message)

- `validate_schema_message(message) -> tuple` (static)
  - Description: Validate schema_topic message structure.
  - Parameters:
    - `message` (dict): Message dictionary
  - Returns: Tuple of (is_valid, error_message)

- `validate_extracted_row_message(message) -> tuple` (static)
  - Description: Validate extracted_rows_topic message structure.
  - Parameters:
    - `message` (dict): Message dictionary
  - Returns: Tuple of (is_valid, error_message)

- `validate_clean_row_message(message) -> tuple` (static)
  - Description: Validate clean_rows_topic message structure.
  - Parameters:
    - `message` (dict): Message dictionary
  - Returns: Tuple of (is_valid, error_message)

- `validate_load_status_message(message) -> tuple` (static)
  - Description: Validate load_rows_topic message structure.
  - Parameters:
    - `message` (dict): Message dictionary
  - Returns: Tuple of (is_valid, error_message)

- `validate_metadata_message(message) -> tuple` (static)
  - Description: Validate metadata_topic message structure using MetadataSchema.
  - Parameters:
    - `message` (dict): Message dictionary
  - Returns: Tuple of (is_valid, error_message)

#### Class: MetadataSchema
**Location:** `etl-final/shared/utils/metadata_schema.py`  
**Responsibility:** Unified metadata model for ETL pipeline tracking.

**Methods:**
- `create_connection_metadata(source_type, source_id, connection_info, timestamp=None) -> dict` (static)
  - Description: Create metadata for connection stage.
  - Parameters:
    - `source_type` (str): "file" or "database"
    - `source_id` (str): Unique identifier for the source
    - `connection_info` (dict): Connection details
    - `timestamp` (datetime, optional): Timestamp
  - Returns: Standardized connection metadata dict

- `create_schema_metadata(source_id, schema, row_count, validation_results=None, timestamp=None) -> dict` (static)
  - Description: Create metadata for schema extraction stage.
  - Parameters:
    - `source_id` (str): Unique identifier for the source
    - `schema` (dict): Schema information
    - `row_count` (int): Number of rows extracted
    - `validation_results` (dict, optional): Schema validation results
    - `timestamp` (datetime, optional): Timestamp
  - Returns: Standardized schema metadata dict

- `create_extraction_metadata(source_id, rows_processed, rows_successful, rows_failed, errors=None, timestamp=None) -> dict` (static)
  - Description: Create metadata for row extraction stage.
  - Parameters:
    - `source_id` (str): Unique identifier for the source
    - `rows_processed` (int): Total rows processed
    - `rows_successful` (int): Successfully extracted rows
    - `rows_failed` (int): Failed extractions
    - `errors` (list, optional): List of error messages
    - `timestamp` (datetime, optional): Timestamp
  - Returns: Standardized extraction metadata dict

- `create_cleaning_metadata(source_id, rows_processed, rows_cleaned, rows_failed, cleaning_rules_applied, validation_warnings=None, timestamp=None) -> dict` (static)
  - Description: Create metadata for cleaning/transformation stage.
  - Parameters:
    - `source_id` (str): Unique identifier for the source
    - `rows_processed` (int): Total rows processed
    - `rows_cleaned` (int): Successfully cleaned rows
    - `rows_failed` (int): Failed cleanings
    - `cleaning_rules_applied` (list): List of cleaning rules used
    - `validation_warnings` (list, optional): Validation warnings
    - `timestamp` (datetime, optional): Timestamp
  - Returns: Standardized cleaning metadata dict

- `create_loading_metadata(source_id, table_name, rows_loaded, rows_failed, load_duration_ms=None, errors=None, timestamp=None) -> dict` (static)
  - Description: Create metadata for loading stage.
  - Parameters:
    - `source_id` (str): Unique identifier for the source
    - `table_name` (str): Target table name in ClickHouse
    - `rows_loaded` (int): Successfully loaded rows
    - `rows_failed` (int): Failed loads
    - `load_duration_ms` (int, optional): Load duration in milliseconds
    - `errors` (list, optional): List of error messages
    - `timestamp` (datetime, optional): Timestamp
  - Returns: Standardized loading metadata dict

- `validate_metadata(metadata) -> tuple` (static)
  - Description: Validate metadata structure.
  - Parameters:
    - `metadata` (dict): Metadata dict to validate
  - Returns: Tuple of (is_valid, error_message)

---

## Frontend Components

### React Functional Components

#### Component: App
**Location:** `frontend/src/App.jsx`  
**Responsibility:** Main application component with routing.

**Props:** None

**State:** None (uses React Router)

#### Component: PrivateRoute
**Location:** `frontend/src/App.jsx`  
**Responsibility:** Protected route component for authentication and role-based access.

**Props:**
- `children` (ReactNode): Child components to render
- `roles` (array, optional): Allowed roles

**Returns:** Navigate component or children based on authentication

#### Component: Dashboard
**Location:** `frontend/src/pages/dashboard/Dashboard.jsx`  
**Responsibility:** Main dashboard page showing reports and analytics.

**State:**
- `reports` (array): List of voice reports
- `isLoading` (bool): Loading state
- `dashboardUrl` (string): Metabase dashboard embed URL

**Methods:**
- `loadDashboardData()`: Load reports and dashboard URL

#### Component: VoiceReportManager
**Location:** `frontend/src/pages/voice-reports/VoiceReportManager.jsx`  
**Responsibility:** Manager interface for uploading audio and managing voice reports.

**State:**
- `currentReport` (object): Currently selected report
- `reports` (array): List of reports
- `isUploading` (bool): Upload in progress
- `isExecuting` (bool): Query execution in progress
- `uploadProgress` (number): Upload progress percentage
- `selectedFile` (File): Selected audio file
- `processingPhase` (string): Current processing phase

**Methods:**
- `loadReports()`: Load all reports for workspace
- `handleFileSelect(event)`: Handle file selection
- `handleUpload()`: Upload audio file and process

#### Component: SQLEditor
**Location:** `frontend/src/pages/voice-reports/SQLEditor.jsx`  
**Responsibility:** Analyst interface for editing SQL queries.

**State:**
- `reports` (array): List of reports
- `selectedReport` (object): Currently selected report
- `sql` (string): SQL query text
- `isSaving` (bool): Save in progress

**Methods:**
- `loadReports()`: Load reports
- `handleSQLChange(value)`: Handle SQL text changes
- `handleSave()`: Save edited SQL

#### Component: DashboardViewer
**Location:** `frontend/src/pages/voice-reports/DashboardViewer.jsx`  
**Responsibility:** Executive interface for viewing embedded Metabase dashboards.

**State:**
- `dashboardUrl` (string): Metabase dashboard embed URL
- `isLoading` (bool): Loading state

**Methods:**
- `loadDashboard()`: Load dashboard embed URL

#### Component: DatabaseManagement
**Location:** `frontend/src/pages/database/DatabaseManagement.jsx`  
**Responsibility:** Manager interface for uploading and managing databases.

**State:**
- `database` (object): Current database record
- `isUploading` (bool): Upload in progress
- `uploadProgress` (number): Upload progress
- `previewData` (object): Database preview data

**Methods:**
- `loadDatabase()`: Load current database
- `handleFileSelect(event)`: Handle file selection
- `handleUpload()`: Upload database file
- `loadPreview()`: Load database preview

#### Component: WorkspaceSettings
**Location:** `frontend/src/pages/workspace/WorkspaceSettings.jsx`  
**Responsibility:** Workspace settings management interface.

**State:**
- `workspace` (object): Workspace data
- `isSaving` (bool): Save in progress

**Methods:**
- `loadWorkspace()`: Load workspace data
- `handleUpdate(data)`: Update workspace settings

#### Component: MembersList
**Location:** `frontend/src/pages/workspace/MembersList.jsx`  
**Responsibility:** Workspace members list interface.

**State:**
- `members` (array): List of workspace members
- `pendingMembers` (array): Pending members
- `invitedMembers` (array): Invited members

**Methods:**
- `loadMembers()`: Load workspace members

#### Component: InviteMember
**Location:** `frontend/src/pages/workspace/InviteMember.jsx`  
**Responsibility:** Interface for inviting new members to workspace.

**State:**
- `email` (string): Invitee email
- `role` (string): Invitee role
- `isSending` (bool): Invitation sending in progress

**Methods:**
- `handleInvite()`: Send invitation

#### Component: AcceptInvite
**Location:** `frontend/src/pages/workspace/AcceptInvite.jsx`  
**Responsibility:** Interface for accepting workspace invitations.

**State:**
- `invitation` (object): Invitation data
- `isAccepting` (bool): Acceptance in progress

**Methods:**
- `loadInvitation(token)`: Load invitation by token
- `handleAccept()`: Accept invitation

#### Component: Login
**Location:** `frontend/src/pages/auth/Login.jsx`  
**Responsibility:** User login interface.

**State:**
- `email` (string): User email
- `password` (string): User password
- `isLoading` (bool): Login in progress

**Methods:**
- `handleLogin()`: Perform login

#### Component: Signup
**Location:** `frontend/src/pages/auth/Signup.jsx`  
**Responsibility:** User registration interface.

**State:**
- `name` (string): User name
- `email` (string): User email
- `password` (string): User password
- `role` (string): User role
- `invitationToken` (string): Invitation token if applicable
- `isLoading` (bool): Signup in progress

**Methods:**
- `handleSignup()`: Perform signup

#### Component: VerifyEmail
**Location:** `frontend/src/pages/auth/VerifyEmail.jsx`  
**Responsibility:** Email verification interface.

**State:**
- `token` (string): Verification token
- `isVerifying` (bool): Verification in progress

**Methods:**
- `handleVerify()`: Verify email

#### Component: Profile
**Location:** `frontend/src/pages/profile/Profile.jsx`  
**Responsibility:** User profile management interface.

**State:**
- `user` (object): User data
- `isSaving` (bool): Save in progress

**Methods:**
- `loadProfile()`: Load user profile
- `handleUpdate(data)`: Update profile

#### Component: DashboardLayout
**Location:** `frontend/src/layouts/DashboardLayout.jsx`  
**Responsibility:** Layout wrapper for authenticated dashboard pages.

**Props:**
- `children` (ReactNode): Child routes

**State:**
- `sidebarOpen` (bool): Sidebar open state

**Methods:**
- `toggleSidebar()`: Toggle sidebar visibility

#### Component: AuthLayout
**Location:** `frontend/src/layouts/AuthLayout.jsx`  
**Responsibility:** Layout wrapper for authentication pages.

**Props:**
- `children` (ReactNode): Child routes

### Reusable UI Components

#### Component: Button
**Location:** `frontend/src/components/Button.jsx`  
**Responsibility:** Reusable button component.

**Props:**
- `children` (ReactNode): Button content
- `onClick` (function): Click handler
- `variant` (string): Button variant (primary, secondary, etc.)
- `disabled` (bool): Disabled state
- `loading` (bool): Loading state

#### Component: Input
**Location:** `frontend/src/components/Input.jsx`  
**Responsibility:** Reusable input component.

**Props:**
- `type` (string): Input type
- `value` (string): Input value
- `onChange` (function): Change handler
- `placeholder` (string): Placeholder text
- `error` (string): Error message

#### Component: Card
**Location:** `frontend/src/components/Card.jsx`  
**Responsibility:** Reusable card component.

**Props:**
- `children` (ReactNode): Card content
- `title` (string): Card title
- `className` (string): Additional CSS classes

#### Component: Modal
**Location:** `frontend/src/components/Modal.jsx`  
**Responsibility:** Reusable modal component.

**Props:**
- `isOpen` (bool): Modal open state
- `onClose` (function): Close handler
- `title` (string): Modal title
- `children` (ReactNode): Modal content

#### Component: LoadingSpinner
**Location:** `frontend/src/components/LoadingSpinner.jsx`  
**Responsibility:** Loading spinner component.

**Props:**
- `size` (string): Spinner size
- `color` (string): Spinner color

#### Component: LoadingSkeleton
**Location:** `frontend/src/components/LoadingSkeleton.jsx`  
**Responsibility:** Loading skeleton component for content placeholders.

**Props:**
- `lines` (number): Number of skeleton lines
- `width` (string): Skeleton width

#### Component: ErrorAlert
**Location:** `frontend/src/components/ErrorAlert.jsx`  
**Responsibility:** Error alert component.

**Props:**
- `message` (string): Error message
- `onClose` (function): Close handler

#### Component: EmptyState
**Location:** `frontend/src/components/EmptyState.jsx`  
**Responsibility:** Empty state component.

**Props:**
- `title` (string): Empty state title
- `message` (string): Empty state message
- `action` (ReactNode): Optional action button

#### Component: Badge
**Location:** `frontend/src/components/Badge.jsx`  
**Responsibility:** Badge component for status indicators.

**Props:**
- `children` (ReactNode): Badge content
- `variant` (string): Badge variant (success, warning, error, etc.)

#### Component: Select
**Location:** `frontend/src/components/Select.jsx`  
**Responsibility:** Select dropdown component.

**Props:**
- `value` (string): Selected value
- `onChange` (function): Change handler
- `options` (array): Select options
- `placeholder` (string): Placeholder text

#### Component: ErrorBoundary
**Location:** `frontend/src/components/ErrorBoundary.jsx`  
**Responsibility:** React error boundary component.

**Props:**
- `children` (ReactNode): Child components

**State:**
- `hasError` (bool): Error state
- `error` (Error): Error object

**Methods:**
- `componentDidCatch(error, errorInfo)`: Catch React errors
- `static getDerivedStateFromError(error)`: Derive error state

#### Component: AnimatedPage
**Location:** `frontend/src/components/AnimatedPage.jsx`  
**Responsibility:** Page wrapper with animation support.

**Props:**
- `children` (ReactNode): Page content
- `className` (string): Additional CSS classes

#### Component: PageWrapper
**Location:** `frontend/src/components/PageWrapper.jsx`  
**Responsibility:** Page wrapper with consistent styling.

**Props:**
- `children` (ReactNode): Page content
- `title` (string): Page title

---

## Utility Functions

### Backend Utilities

#### Function: generate_verification_token
**Location:** `users/utils.py`  
**Parameters:**
- `user_id` (int): User ID

**Returns:**
- `str`: Signed verification token

#### Function: verify_email_token
**Location:** `users/utils.py`  
**Parameters:**
- `token` (str): Verification token
- `max_age` (int): Maximum age in seconds (default: 86400)

**Returns:**
- `tuple`: (success: bool, user_id: int or None, error_type: str or None)

#### Function: send_verification_email
**Location:** `users/utils.py`  
**Parameters:**
- `user_email` (str): Email address
- `user_name` (str): User name
- `token` (str): Verification token

**Returns:**
- `bool`: True if email sent successfully

#### Function: generate_invitation_token
**Location:** `users/utils.py`  
**Returns:**
- `str`: Unique token string (UUID-based)

#### Function: send_invitation_email
**Location:** `users/utils.py`  
**Parameters:**
- `invited_email` (str): Email address
- `inviter_name` (str): Inviter name
- `workspace_name` (str): Workspace name
- `token` (str): Invitation token
- `role` (str): Role (analyst/executive)

**Returns:**
- `bool`: True if email sent successfully

#### Function: validate_invitation_token
**Location:** `workspace/utils.py`  
**Parameters:**
- `token` (str): Invitation token string

**Returns:**
- `tuple`: (workspace, role, invited_email, invitation)

**Raises:**
- `serializers.ValidationError`: If token is invalid, expired, or already used

#### Function: sanitize_sql_for_http
**Location:** `voice_reports/services/clickhouse_executor.py`  
**Parameters:**
- `sql` (str): Raw SQL string

**Returns:**
- `str`: Clean SQL safe for HTTP execution

#### Function: sanitize_numeric_value
**Location:** `voice_reports/services/clickhouse_executor.py`  
**Parameters:**
- `value` (Any): Any value (numeric, string, None, etc.)

**Returns:**
- `Any`: Sanitized value (NaN/Infinity → 0, None → None)

#### Function: sanitize_query_results
**Location:** `voice_reports/services/clickhouse_executor.py`  
**Parameters:**
- `rows` (List[Dict]): List of dictionaries representing query result rows

**Returns:**
- `List[Dict]`: Sanitized list with all NaN/Infinity values replaced

#### Function: format_file_size
**Location:** `database/utils.py`  
**Parameters:**
- `size_bytes` (int): File size in bytes

**Returns:**
- `str`: Human-readable file size string

#### Function: cleanup_database
**Location:** `database/utils.py`  
**Parameters:**
- `database_instance` (Database): Database instance

**Returns:**
- `dict`: Cleanup results with status for each resource

---

## Admin Classes

### Django Admin Classes

#### Class: UserAdmin
**Location:** `users/admin.py`  
**Responsibility:** Django admin configuration for User model.

#### Class: WorkspaceAdmin
**Location:** `workspace/admin.py`  
**Responsibility:** Django admin configuration for Workspace model.

#### Class: WorkspaceMemberAdmin
**Location:** `workspace/admin.py`  
**Responsibility:** Django admin configuration for WorkspaceMember model.

#### Class: InvitationAdmin
**Location:** `workspace/admin.py`  
**Responsibility:** Django admin configuration for Invitation model.

#### Class: VoiceReportAdmin
**Location:** `voice_reports/admin.py`  
**Responsibility:** Django admin configuration for VoiceReport model.

#### Class: SQLEditHistoryAdmin
**Location:** `voice_reports/admin.py`  
**Responsibility:** Django admin configuration for SQLEditHistory model.

#### Class: DashboardPageAdmin
**Location:** `voice_reports/admin.py`  
**Responsibility:** Django admin configuration for DashboardPage model.

#### Class: ReportPageAssignmentAdmin
**Location:** `voice_reports/admin.py`  
**Responsibility:** Django admin configuration for ReportPageAssignment model.

#### Class: DatabaseAdmin
**Location:** `database/admin.py`  
**Responsibility:** Django admin configuration for Database model.

---

## App Configuration Classes

### Django App Config Classes

#### Class: UsersConfig
**Location:** `users/apps.py`  
**Responsibility:** Django app configuration for users app.

#### Class: WorkspaceConfig
**Location:** `workspace/apps.py`  
**Responsibility:** Django app configuration for workspace app.

#### Class: VoiceReportsConfig
**Location:** `voice_reports/apps.py`  
**Responsibility:** Django app configuration for voice_reports app.

#### Class: DatabaseConfig
**Location:** `database/apps.py`  
**Responsibility:** Django app configuration for database app.

#### Class: WhisperAppConfig
**Location:** `Small Whisper/backend/whisper_app/apps.py`  
**Responsibility:** Django app configuration for whisper_app.

#### Class: ReasoningAppConfig
**Location:** `Small Whisper/backend/reasoning_app/apps.py`  
**Responsibility:** Django app configuration for reasoning_app.

#### Class: LlmAppConfig
**Location:** `Small Whisper/backend/llm_app/apps.py`  
**Responsibility:** Django app configuration for llm_app.

#### Class: EngineConfig (Transformer)
**Location:** `etl-final/transformer-service/transformer/engine/apps.py`  
**Responsibility:** Django app configuration for transformer engine.

#### Class: EngineConfig (Loader)
**Location:** `etl-final/loader-service/loader/engine/apps.py`  
**Responsibility:** Django app configuration for loader engine.

#### Class: EngineConfig (Extractor)
**Location:** `etl-final/extractor-service/extractor/engine/apps.py`  
**Responsibility:** Django app configuration for extractor engine.

#### Class: CoreConfig
**Location:** `etl-final/detector-service/detector/core/apps.py`  
**Responsibility:** Django app configuration for detector core.

#### Class: EtlEngineConfig
**Location:** `etl-final/connector-service/connector/etl_engine/apps.py`  
**Responsibility:** Django app configuration for connector ETL engine.

#### Class: ApiConfig
**Location:** `etl-final/metadata-service/metadata/api/apps.py`  
**Responsibility:** Django app configuration for metadata API.

---

## Migration Classes

All Django migration classes follow the standard Django migration pattern:
- Inherit from `migrations.Migration`
- Define `dependencies` and `operations`
- Located in `*/migrations/*.py` files

These are auto-generated by Django and not documented individually.

---

## Summary

This documentation covers:
- **133+ Python classes** across backend, ETL, and AI modules
- **30+ React components** in the frontend
- **50+ utility functions** and helper methods
- **Complete method signatures** with parameters and return types
- **Admin configurations** for Django models
- **App configurations** for all Django apps

All classes are organized by module and include their file locations, responsibilities, and complete method documentation.
