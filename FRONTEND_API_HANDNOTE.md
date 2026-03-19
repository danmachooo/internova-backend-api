# FRONTEND API Hand Note

Frontend-facing API reference for the current Django backend implementation.

Base URL: `/api/v1/`

Auth header:

```http
Authorization: Bearer <access_token>
```

Common conventions:

- All router-generated endpoints use a trailing slash.
- List endpoints are paginated unless noted otherwise.
- Default pagination query: `?page=<number>`
- Search is available only where listed.
- Ordering is available only where listed, via `?ordering=<field>` or `?ordering=-<field>`
- Error shape:

```json
{ "error": "..." }
```

```json
{ "errors": { "field_name": ["..."] } }
```

## How To Read This File

- `required` means frontend must send it on create for that endpoint
- `optional` means frontend may send it
- `read-only` means backend returns it but ignores client writes
- `write-only` means frontend may send it but backend will not return it
- `nullable` means `null` is accepted
- List endpoints usually return DRF paginated data:

```json
{
  "count": 123,
  "next": "http://localhost:8000/api/v1/resource/?page=2",
  "previous": null,
  "results": []
}
```

## Common Success And Error Patterns

### Common success codes

- `200 OK` for successful get, patch, custom actions, and logout
- `201 Created` for successful create routes
- `204 No Content` for successful delete routes

### Common validation error example

```json
{
  "errors": {
    "email": ["A user with this email already exists."]
  }
}
```

### Common permission error example

```json
{
  "error": "You do not have permission to perform this action."
}
```

### Common auth error example

```json
{
  "error": "Authentication credentials were not provided."
}
```

## Core Frontend Rules

- Always send the bearer token after login except on public routes
- Always keep trailing slashes in the URLs
- Do not send server-computed values like `hours`, `status`, `business_days`, `score`, or `assessment_score`
- Do not expect `company_account_password` back from the API
- Intern-facing assessment responses will never contain `correct_index`
- For file uploads like DAR, use `multipart/form-data`, not JSON
- For singleton configs like feature access and calendar settings, treat them as one object, not a collection

## Global List Queries

Use these only on list endpoints that actually support them.

- `page`
- `search`
- `ordering`

## Auth

### POST `/auth/login/`

- Auth: Public
- Path params: none
- Query params: none
- Body:

```json
{
  "email": "user@example.com",
  "password": "string"
}
```

- Success response example:

```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": "uuid",
    "name": "Jane Admin",
    "email": "user@example.com",
    "role": "staffadmin",
    "status": "active",
    "last_login_at": "2026-03-19T10:00:00+08:00",
    "is_active": true,
    "is_staff": false,
    "created_at": "2026-03-01T09:00:00+08:00",
    "updated_at": "2026-03-19T10:00:00+08:00"
  }
}
```

- Common errors:
  - invalid credentials
  - inactive account

### POST `/auth/refresh/`

- Auth: Public
- Path params: none
- Query params: none
- Body:

```json
{
  "refresh": "refresh_token"
}
```

- Success response example:

```json
{
  "access": "new_access_token"
}
```

### POST `/auth/logout/`

- Auth: Authenticated
- Path params: none
- Query params: none
- Body:

```json
{
  "refresh": "refresh_token"
}
```

- Success response example:

```json
{
  "message": "Logged out successfully."
}
```

### GET `/auth/me/`

- Auth: Authenticated
- Path params: none
- Query params: none
- Body: none

- Success response example:

```json
{
  "id": "uuid",
  "name": "Jane Admin",
  "email": "user@example.com",
  "role": "staffadmin",
  "status": "active",
  "last_login_at": "2026-03-19T10:00:00+08:00",
  "created_at": "2026-03-01T09:00:00+08:00",
  "updated_at": "2026-03-19T10:00:00+08:00"
}
```

### PATCH `/auth/me/`

- Auth: Authenticated
- Path params: none
- Query params: none
- Body: any of

```json
{
  "name": "string",
  "email": "user@example.com"
}
```

- Success response shape: same as `GET /auth/me/`

### POST `/auth/change-password/`

- Auth: Authenticated
- Path params: none
- Query params: none
- Body:

```json
{
  "old_password": "string",
  "new_password": "string"
}
```

- Success response example:

```json
{
  "message": "Password changed successfully."
}
```

## Admin Users

### GET `/admins/`

- Auth: SuperAdmin
- Path params: none
- Query params:
  - `page`
  - `role`
  - `status`
- Body: none

- Response shape:
  - paginated list of admin users

### POST `/admins/`

- Auth: SuperAdmin
- Path params: none
- Query params: none
- Body:

```json
{
  "name": "string",
  "email": "admin@example.com",
  "password": "string",
  "role": "superadmin | staffadmin",
  "status": "active | inactive"
}
```

- Field notes:
  - `name`: required
  - `email`: required
  - `password`: required, write-only
  - `role`: required
  - `status`: required

### GET `/admins/{id}/`

- Auth: SuperAdmin
- Path params:
  - `id`: admin user UUID
- Query params: none
- Body: none

### PATCH `/admins/{id}/`

- Auth: SuperAdmin
- Path params:
  - `id`: admin user UUID
- Query params: none
- Body: any subset of

```json
{
  "name": "string",
  "email": "admin@example.com",
  "password": "string",
  "role": "superadmin | staffadmin",
  "status": "active | inactive"
}
```

- Response shape:
  - full admin detail object

### DELETE `/admins/{id}/`

- Auth: SuperAdmin
- Path params:
  - `id`: admin user UUID
- Query params: none
- Body: none

## Batches

### GET `/batches/`

- Auth: Admin
- Path params: none
- Query params:
  - `page`
  - `status`
  - `search`
    - searches: `name`
  - `ordering`
    - allowed: `start_date`, `end_date`, `progress`, `created_at`
- Body: none

- Response shape:
  - paginated list of batch objects

### POST `/batches/`

- Auth: Admin
- Path params: none
- Query params: none
- Body:

```json
{
  "name": "Batch 2026-A",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "status": "active | completed",
  "progress": 0
}
```

- Common error:
  - `end_date` earlier than `start_date`

### GET `/batches/{id}/`

- Auth: Admin
- Path params:
  - `id`: batch UUID
- Query params: none
- Body: none

### PATCH `/batches/{id}/`

- Auth: Admin
- Path params:
  - `id`: batch UUID
- Query params: none
- Body: any subset of

```json
{
  "name": "Batch 2026-A",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "status": "active | completed",
  "progress": 50
}
```

### DELETE `/batches/{id}/`

- Auth: Admin
- Path params:
  - `id`: batch UUID
- Query params: none
- Body: none

### GET `/batches/{id}/interns/`

- Auth: Admin
- Path params:
  - `id`: batch UUID
- Query params: none
- Body: none

- Response example:

```json
[
  {
    "id": "uuid",
    "name": "Intern Name",
    "email": "intern@example.com"
  }
]
```

## Intern Roles

### GET `/intern-roles/`

- Auth: Public
- Path params: none
- Query params: none
- Body: none

- Response example:

```json
[
  { "value": "Developer", "label": "Developer" },
  { "value": "Quality Assurance", "label": "Quality Assurance" }
]
```

## Interns

### GET `/interns/`

- Auth: Admin
- Path params: none
- Query params:
  - `page`
  - `batch`
    - batch UUID
  - `role`
    - intern role string
  - `status`
    - user status
  - `assessment_completed`
    - `true | false`
  - `search`
    - searches: `user__name`, `user__email`, `school`, `github_username`
  - `ordering`
    - allowed: `created_at`, `required_hours`, `rendered_hours`, `user__name`
- Body: none

- Response shape:
  - paginated list of intern summary objects

### POST `/interns/`

- Auth: Admin
- Path params: none
- Query params: none
- Body:

```json
{
  "name": "string",
  "email": "intern@example.com",
  "password": "string",
  "status": "active | inactive",
  "batch": "batch_uuid_or_null",
  "school": "string",
  "intern_role": "Developer | Quality Assurance | Project Manager | Business Analyst | null",
  "phone": "string",
  "github_username": "string",
  "required_hours": "480.00",
  "start_date": "YYYY-MM-DD",
  "birthdate": "YYYY-MM-DD",
  "avatar": "uploaded file or existing file value",
  "company_account_email": "string",
  "company_account_password": "string",
  "assessment_required": true
}
```

- Field notes:
  - `name`, `email`, `password`, `school`, `phone`, `start_date`, `birthdate`: required
  - `password`: write-only
  - `batch`: optional, nullable
  - `github_username`: optional
  - `intern_role`: optional, nullable
  - `avatar`: optional
  - `company_account_password`: optional, write-only
  - `rendered_hours`, `assessment_completed_at`, `assessment_score`: read-only

- Important:
  - backend object id here is the `InternProfile` id, not the user id

### GET `/interns/{id}/`

- Auth: Admin or Self
- Path params:
  - `id`: intern profile UUID
- Query params: none
- Body: none

### PATCH `/interns/{id}/`

- Auth: Admin or Self
- Path params:
  - `id`: intern profile UUID
- Query params: none
- Body: any subset of the create fields above
- Notes:
  - `rendered_hours`, `assessment_completed_at`, and `assessment_score` are read-only
  - `company_account_password` is write-only and never returned

- Common error:
  - `birthdate` must be earlier than `start_date`

### DELETE `/interns/{id}/`

- Auth: Admin
- Path params:
  - `id`: intern profile UUID
- Query params: none
- Body: none

### GET `/interns/hours-breakdown/`

- Auth: Admin
- Path params: none
- Query params:
  - `batch_id` optional batch UUID
- Body: none
- Not paginated

- Response example:

```json
[
  {
    "id": "uuid",
    "name": "Intern Name",
    "email": "intern@example.com",
    "rendered_hours": "120.00",
    "required_hours": "480.00"
  }
]
```

### GET `/interns/{id}/attempts/`

- Auth: Admin
- Path params:
  - `id`: intern profile UUID
- Query params: none
- Body: none

- Response example:

```json
[
  {
    "assessment_id": "uuid",
    "assessment_title": "Backend Assessment",
    "score": "85.00",
    "completed": true,
    "completed_at": "2026-03-19T11:00:00+08:00",
    "created_at": "2026-03-19T10:30:00+08:00"
  }
]
```

## Registrations

### POST `/registrations/`

- Auth: Public
- Path params: none
- Query params: none
- Body:

```json
{
  "name": "string",
  "email": "intern@example.com",
  "password": "string",
  "github_username": "string",
  "school": "string",
  "phone": "string",
  "birthdate": "YYYY-MM-DD",
  "start_date": "YYYY-MM-DD",
  "required_hours": 480
}
```

- Field notes:
  - all fields shown above are expected on create except `github_username`, which is optional
  - password is write-only

### GET `/registrations/`

- Auth: Admin
- Path params: none
- Query params:
  - `page`
- Body: none

### GET `/registrations/{id}/`

- Auth: Admin
- Path params:
  - `id`: registration UUID
- Query params: none
- Body: none

### POST `/registrations/{id}/approve/`

- Auth: Admin
- Path params:
  - `id`: registration UUID
- Query params: none
- Body: none

- Response shape:
  - registration object with updated `status`, `decided_at`, and `intern_id`

### POST `/registrations/{id}/deny/`

- Auth: Admin
- Path params:
  - `id`: registration UUID
- Query params: none
- Body: none

- Response shape:
  - registration object with updated `status` and `decided_at`

## Attendance

### GET `/attendance/`

- Auth: Admin
- Path params: none
- Query params:
  - `page`
  - `intern`
    - intern user UUID
  - `date`
    - `YYYY-MM-DD`
  - `status`
  - `ordering`
    - allowed: `date`, `created_at`, `hours`
- Body: none

- Response shape:
  - paginated list of attendance records

### POST `/attendance/`

- Auth: Admin
- Path params: none
- Query params: none
- Body:

```json
{
  "intern": "intern_user_uuid",
  "date": "YYYY-MM-DD",
  "login_time": "HH:MM[:SS]",
  "logout_time": "HH:MM[:SS]"
}
```

- Important:
  - send the intern user id here, not the intern profile id
  - `hours` and `status` are computed by backend

### GET `/attendance/{id}/`

- Auth: Admin or Self
- Path params:
  - `id`: attendance record UUID
- Query params: none
- Body: none

### PATCH `/attendance/{id}/`

- Auth: Admin
- Path params:
  - `id`: attendance record UUID
- Query params: none
- Body: any subset of

```json
{
  "intern": "intern_user_uuid",
  "date": "YYYY-MM-DD",
  "login_time": "HH:MM[:SS]",
  "logout_time": "HH:MM[:SS]"
}
```

### POST `/attendance/clock-in/`

- Auth: Intern
- Path params: none
- Query params: none
- Body: none

- Success response example:

```json
{
  "message": "Clocked in successfully.",
  "record": {
    "id": "uuid",
    "intern": "intern_user_uuid",
    "date": "2026-03-19",
    "login_time": "08:59:00",
    "logout_time": null,
    "hours": "0.00",
    "status": "late",
    "created_at": "2026-03-19T08:59:00+08:00",
    "updated_at": "2026-03-19T08:59:00+08:00"
  }
}
```

- Common error:
  - already clocked in today

### POST `/attendance/clock-out/`

- Auth: Intern
- Path params: none
- Query params: none
- Body: none

- Success response shape:
  - same wrapper as clock-in with updated record

### GET `/attendance/summary/weekly/`

- Auth: Admin
- Path params: none
- Query params:
  - `week_start` optional `YYYY-MM-DD`
- Body: none
- Not paginated

- Common error:
  - invalid `week_start` format

### GET `/attendance/my/`

- Auth: Intern
- Path params: none
- Query params:
  - `page`
  - `intern`
  - `date`
  - `status`
  - `ordering`
- Body: none
- Notes:
  - `intern` is technically accepted by the filter backend, but the view still forces the current user only

## DAR

### GET `/dar/`

- Auth: Admin
- Path params: none
- Query params:
  - `page`
  - `ordering`
    - allowed: `date`, `created_at`, `upload_time`
- Body: none

### POST `/dar/`

- Auth: Intern
- Path params: none
- Query params: none
- Content type: `multipart/form-data`
- Body:
  - `date`: `YYYY-MM-DD`
  - `file`: PDF file only, max 10MB

- Common errors:
  - file is not PDF
  - file exceeds 10MB
  - DAR already exists for the intern/date

### GET `/dar/{id}/`

- Auth: Admin or Self
- Path params:
  - `id`: DAR UUID
- Query params: none
- Body: none

### DELETE `/dar/{id}/`

- Auth: Admin
- Path params:
  - `id`: DAR UUID
- Query params: none
- Body: none

### GET `/dar/missing/`

- Auth: Admin
- Path params: none
- Query params:
  - `date` optional `YYYY-MM-DD`
- Body: none
- Not paginated

- Response example:

```json
[
  {
    "intern_id": "uuid",
    "intern_name": "Intern Name",
    "intern_email": "intern@example.com",
    "date": "2026-03-19"
  }
]
```

### GET `/dar/my/`

- Auth: Intern
- Path params: none
- Query params:
  - `page`
  - `ordering`
- Body: none

## Assessments

### GET `/assessments/`

- Auth: Authenticated
- Path params: none
- Query params:
  - `page`
  - `is_published`
    - `true | false`
  - `search`
    - searches: `title`, `description`
  - `ordering`
    - allowed: `created_at`, `updated_at`, `published_at`, `title`
- Body: none
- Notes:
  - Intern users only receive published assessments
  - Intern responses never include `correct_index`

- Response shape:
  - paginated list of assessment objects with nested pages and questions

### POST `/assessments/`

- Auth: Admin
- Path params: none
- Query params: none
- Body:

```json
{
  "title": "string",
  "description": "string",
  "is_published": false
}
```

- Field notes:
  - `created_by`, `published_at`, `created_at`, `updated_at`: read-only

### GET `/assessments/{id}/`

- Auth: Authenticated
- Path params:
  - `id`: assessment UUID
- Query params: none
- Body: none

### PATCH `/assessments/{id}/`

- Auth: Admin
- Path params:
  - `id`: assessment UUID
- Query params: none
- Body: any subset of

```json
{
  "title": "string",
  "description": "string",
  "is_published": true
}
```

### DELETE `/assessments/{id}/`

- Auth: Admin
- Path params:
  - `id`: assessment UUID
- Query params: none
- Body: none

### POST `/assessments/{id}/publish/`

- Auth: Admin
- Path params:
  - `id`: assessment UUID
- Query params: none
- Body: none

### POST `/assessments/{id}/unpublish/`

- Auth: Admin
- Path params:
  - `id`: assessment UUID
- Query params: none
- Body: none

### GET `/assessments/{id}/pages/`

- Auth: Admin
- Path params:
  - `id`: assessment UUID
- Query params: none
- Body: none

### POST `/assessments/{id}/pages/`

- Auth: Admin
- Path params:
  - `id`: assessment UUID
- Query params: none
- Body:

```json
{
  "title": "string",
  "description": "string",
  "order": 0
}
```

- Response shape:
  - created page returned inside full page serializer format

### PATCH `/assessments/{assessment_id}/pages/{page_id}/`

- Auth: Admin
- Path params:
  - `assessment_id`: assessment UUID
  - `page_id`: page UUID
- Query params: none
- Body: any subset of

```json
{
  "title": "string",
  "description": "string",
  "order": 0
}
```

### DELETE `/assessments/{assessment_id}/pages/{page_id}/`

- Auth: Admin
- Path params:
  - `assessment_id`: assessment UUID
  - `page_id`: page UUID
- Query params: none
- Body: none

### POST `/assessments/{assessment_id}/pages/{page_id}/questions/`

- Auth: Admin
- Path params:
  - `assessment_id`: assessment UUID
  - `page_id`: page UUID
- Query params: none
- Body:

```json
{
  "prompt": "string",
  "choices": ["A", "B", "C", "D"],
  "correct_index": 0,
  "order": 0
}
```

- Important:
  - admin only
  - intern payloads never expose `correct_index`

### PATCH `/assessments/{assessment_id}/pages/{page_id}/questions/{q_id}/`

- Auth: Admin
- Path params:
  - `assessment_id`: assessment UUID
  - `page_id`: page UUID
  - `q_id`: question UUID
- Query params: none
- Body: any subset of

```json
{
  "prompt": "string",
  "choices": ["A", "B", "C", "D"],
  "correct_index": 0,
  "order": 0
}
```

### DELETE `/assessments/{assessment_id}/pages/{page_id}/questions/{q_id}/`

- Auth: Admin
- Path params:
  - `assessment_id`: assessment UUID
  - `page_id`: page UUID
  - `q_id`: question UUID
- Query params: none
- Body: none

## Attempts

### GET `/attempts/`

- Auth: Admin or Self
- Path params: none
- Query params:
  - `page`
  - `assessment`
    - assessment UUID
  - `completed`
    - `true | false`
  - `ordering`
    - allowed: `created_at`, `completed_at`, `score`
- Body: none

- Response shape:
  - paginated list of attempt objects

### POST `/attempts/`

- Auth: Intern
- Path params: none
- Query params: none
- Body:

```json
{
  "assessment": "assessment_uuid"
}
```

- Important:
  - backend uses current logged-in intern automatically
  - one attempt per intern per assessment only

- Common errors:
  - assessment is not published
  - already started this assessment

### GET `/attempts/{id}/`

- Auth: Admin or Self
- Path params:
  - `id`: attempt UUID
- Query params: none
- Body: none

### POST `/attempts/{id}/submit/`

- Auth: Intern
- Path params:
  - `id`: attempt UUID
- Query params: none
- Body:

```json
{
  "answers": [
    {
      "question_id": "question_uuid",
      "selected_index": 2
    }
  ]
}
```

- Important:
  - `score` must never be sent by frontend
  - backend computes score and completion server-side

## Calendar

### GET `/events/`

- Auth: Authenticated
- Path params: none
- Query params:
  - `page`
  - `ordering`
    - allowed: `date`, `time`, `created_at`
- Body: none
- Notes:
  - A `CalendarEventFilter` file exists, but the current view does not wire date/type filtering into the endpoint

- Response shape:
  - paginated list of event summary objects

### POST `/events/`

- Auth: Admin
- Path params: none
- Query params: none
- Body:

```json
{
  "title": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:MM[:SS]",
  "type": "meeting | presentation",
  "description": "string"
}
```

### GET `/events/{id}/`

- Auth: Authenticated
- Path params:
  - `id`: event UUID
- Query params: none
- Body: none

### PATCH `/events/{id}/`

- Auth: Admin
- Path params:
  - `id`: event UUID
- Query params: none
- Body: any subset of

```json
{
  "title": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:MM[:SS]",
  "type": "meeting | presentation",
  "description": "string"
}
```

### DELETE `/events/{id}/`

- Auth: Admin
- Path params:
  - `id`: event UUID
- Query params: none
- Body: none

### GET `/calendar/settings/`

- Auth: Admin
- Path params: none
- Query params: none
- Body: none

### PATCH `/calendar/settings/`

- Auth: Admin
- Path params: none
- Query params: none
- Body:

```json
{
  "weekend_days": [0, 6]
}
```

- Important:
  - values must be integers from `0` to `6`
  - backend stores JS-style weekday values where `0 = Sunday`

### POST `/calendar/holidays/`

- Auth: Admin
- Path params: none
- Query params: none
- Body:

```json
{
  "date": "YYYY-MM-DD",
  "name": "Holiday name"
}
```

### DELETE `/calendar/holidays/{id}/`

- Auth: Admin
- Path params:
  - `id`: holiday UUID
- Query params: none
- Body: none

## Leaves

### GET `/leaves/`

- Auth: Admin or Intern
- Path params: none
- Query params:
  - `page`
  - `type`
  - `status`
  - `from_date`
    - interpreted as `from_date >= value`
  - `to_date`
    - interpreted as `to_date <= value`
  - `ordering`
    - allowed: `created_at`, `from_date`, `to_date`, `business_days`
- Body: none

### POST `/leaves/`

- Auth: Intern
- Path params: none
- Query params: none
- Body:

```json
{
  "from_date": "YYYY-MM-DD",
  "to_date": "YYYY-MM-DD",
  "type": "sick | vacation | emergency | other",
  "reason": "string",
  "admin_note": "optional string"
}
```

- Important:
  - `business_days` is computed by backend
  - field names are exactly `from_date` and `to_date`

- Common error:
  - `to_date` earlier than `from_date`

### GET `/leaves/{id}/`

- Auth: Admin or Self
- Path params:
  - `id`: leave UUID
- Query params: none
- Body: none

### POST `/leaves/{id}/approve/`

- Auth: Admin
- Path params:
  - `id`: leave UUID
- Query params: none
- Body:

```json
{
  "admin_note": "optional string"
}
```

- Response shape:
  - leave detail object with updated decision fields

### POST `/leaves/{id}/deny/`

- Auth: Admin
- Path params:
  - `id`: leave UUID
- Query params: none
- Body:

```json
{
  "admin_note": "optional string"
}
```

- Response shape:
  - leave detail object with updated decision fields

## Projects

### GET `/projects/`

- Auth: Admin
- Path params: none
- Query params:
  - `page`
  - `ordering`
    - allowed: `name`, `status`, `start_date`, `end_date`, `created_at`
- Body: none

- Response shape:
  - paginated list of project summary objects

### POST `/projects/`

- Auth: Admin
- Path params: none
- Query params: none
- Body:

```json
{
  "name": "string",
  "description": "string",
  "status": "active | on_hold | completed",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD"
}
```

### GET `/projects/{id}/`

- Auth: Admin
- Path params:
  - `id`: project UUID
- Query params: none
- Body: none

### PATCH `/projects/{id}/`

- Auth: Admin
- Path params:
  - `id`: project UUID
- Query params: none
- Body: any subset of

```json
{
  "name": "string",
  "description": "string",
  "status": "active | on_hold | completed",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD"
}
```

### DELETE `/projects/{id}/`

- Auth: Admin
- Path params:
  - `id`: project UUID
- Query params: none
- Body: none

### POST `/projects/{id}/assign/`

- Auth: Admin
- Path params:
  - `id`: project UUID
- Query params: none
- Body:

```json
{
  "intern": "intern_user_uuid"
}
```

- Important:
  - send the intern user UUID, not intern profile UUID

### DELETE `/projects/{id}/assign/{intern_id}/`

- Auth: Admin
- Path params:
  - `id`: project UUID
  - `intern_id`: intern user UUID
- Query params: none
- Body: none

## Assets

### GET `/laptops/`

- Auth: Admin
- Path params: none
- Query params:
  - `page`
  - `ordering`
    - allowed: `brand`, `serial_no`, `status`, `created_at`
- Body: none

- Response shape:
  - paginated list of laptop summary objects

### POST `/laptops/`

- Auth: Admin
- Path params: none
- Query params: none
- Body:

```json
{
  "brand": "string",
  "serial_no": "string",
  "ip_address": "string",
  "assigned_to": "intern_user_uuid_or_null",
  "status": "assigned | available | issued",
  "accounts": "string"
}
```

### GET `/laptops/{id}/`

- Auth: Admin
- Path params:
  - `id`: laptop UUID
- Query params: none
- Body: none

### PATCH `/laptops/{id}/`

- Auth: Admin
- Path params:
  - `id`: laptop UUID
- Query params: none
- Body: any subset of

```json
{
  "brand": "string",
  "serial_no": "string",
  "ip_address": "string",
  "assigned_to": "intern_user_uuid_or_null",
  "status": "assigned | available | issued",
  "accounts": "string"
}
```

### DELETE `/laptops/{id}/`

- Auth: Admin
- Path params:
  - `id`: laptop UUID
- Query params: none
- Body: none

### GET `/laptop-issues/`

- Auth: Admin or Intern
- Path params: none
- Query params:
  - `page`
  - `ordering`
    - allowed: `created_at`, `status`, `resolved_at`
- Body: none

### POST `/laptop-issues/`

- Auth: Intern
- Path params: none
- Query params: none
- Body:

```json
{
  "laptop": "laptop_uuid",
  "description": "string"
}
```

- Important:
  - `status` and `admin_note` are backend-managed on create

### GET `/laptop-issues/{id}/`

- Auth: Admin or Self
- Path params:
  - `id`: issue report UUID
- Query params: none
- Body: none

### PATCH `/laptop-issues/{id}/`

- Auth: Admin
- Path params:
  - `id`: issue report UUID
- Query params: none
- Body:

```json
{
  "status": "open | in_progress | resolved",
  "admin_note": "string"
}
```

- Response shape:
  - full issue detail object including `resolved_by` and `resolved_at`

## Notifications

### GET `/notifications/`

- Auth: Authenticated
- Path params: none
- Query params:
  - `page`
  - `ordering`
    - allowed: `created_at`, `type`
- Body: none

- Response shape:
  - paginated list of notifications
- Returned fields:
  - `id`, `title`, `message`, `type`, `audience`, `read`, `created_at`

### POST `/notifications/`

- Auth: Admin
- Path params: none
- Query params: none
- Body:

```json
{
  "title": "string",
  "message": "string",
  "type": "info | warning | success | error",
  "audience": "all | admin | intern | intern:<uuid>"
}
```

- Important:
  - `read` is backend-generated per current user

### POST `/notifications/{id}/read/`

- Auth: Authenticated
- Path params:
  - `id`: notification UUID
- Query params: none
- Body: none

### DELETE `/notifications/{id}/`

- Auth: Admin
- Path params:
  - `id`: notification UUID
- Query params: none
- Body: none

## Feature Access

### GET `/feature-access/`

- Auth: SuperAdmin
- Path params: none
- Query params: none
- Body: none

### PATCH `/feature-access/`

- Auth: SuperAdmin
- Path params: none
- Query params: none
- Body:

```json
{
  "admin_features": {
    "dashboard": true,
    "batches": true,
    "interns": true,
    "dar": true,
    "assessments": true,
    "projects": true,
    "laptops": true,
    "calendar": true,
    "leaves": true,
    "notifications": true,
    "profile": true,
    "adminManagement": false,
    "featureAccess": false
  },
  "intern_features": {
    "dashboard": true,
    "attendance": true,
    "leave": true,
    "dar": true,
    "laptopIssue": true,
    "notifications": true,
    "profile": true
  }
}
```

- Notes:
  - The serializer requires complete objects for `admin_features` and `intern_features` when those keys are sent
  - Partial nested updates are not supported inside those objects

## Response Shape Notes By Resource

### User ids vs intern profile ids

- `interns` endpoints use the `InternProfile` UUID in the URL
- many other app payloads use the intern `User` UUID
- specifically:
  - `/interns/{id}/` uses intern profile id
  - attendance `intern` field uses user id
  - project assign `intern` field uses user id
  - laptop `assigned_to` uses user id
  - leave `intern` in responses is user id

This matters a lot on the frontend. Do not assume all intern-related ids are the same field.

### Read-only fields frontend should never send

- auth/admin users:
  - `id`, `last_login_at`, `is_active`, `is_staff`, `created_at`, `updated_at`
- interns:
  - `id`, `rendered_hours`, `assessment_completed_at`, `assessment_score`, `created_at`, `updated_at`
- attendance:
  - `id`, `hours`, `status`, `created_at`, `updated_at`
- leaves:
  - `id`, `business_days`, `status`, `decided_at`, `decided_by`, `created_at`, `updated_at`
- attempts:
  - `id`, `intern`, `score`, `completed`, `completed_at`, `created_at`, `updated_at`
- notifications:
  - `id`, `read`, `created_at`

### Write-only fields frontend can send but will not receive back

- `password`
- `company_account_password`

## Recommended Frontend Workflows

### Admin auth flow

1. `POST /auth/login/`
2. store `access` and `refresh`
3. use `GET /auth/me/` on app boot or refresh
4. use `POST /auth/refresh/` when access token expires
5. use `POST /auth/logout/` on sign out

### Intern registration flow

1. public user submits `POST /registrations/`
2. admin reviews `GET /registrations/`
3. admin calls `POST /registrations/{id}/approve/` or `POST /registrations/{id}/deny/`

### Assessment flow for intern

1. intern logs in
2. `GET /assessments/` to load published assessments
3. `POST /attempts/` with assessment id
4. render nested pages/questions from assessment detail
5. `POST /attempts/{id}/submit/` with selected answers
6. optionally refresh attempts with `GET /attempts/`

### Leave flow for intern/admin

1. intern submits `POST /leaves/`
2. intern/admin lists with `GET /leaves/`
3. admin approves or denies with `/approve/` or `/deny/`
4. frontend refreshes leave detail/list and notifications

### DAR upload flow

1. frontend builds `FormData`
2. append `date`
3. append PDF file as `file`
4. `POST /dar/` with multipart request

## Known Codebase Reality Checks

- `CalendarEventFilter` exists, but `/events/` currently does not expose `date` and `type` filtering in the view
- several apps define ordering but not explicit filter classes; do not assume every model field is queryable
- list response fields are often smaller than detail response fields, so frontend should not assume list and detail object shapes are identical
