# OpenList API Reference

Complete API endpoint reference for OpenList REST API operations.

## Authentication

### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}

# Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 2FA Operations
- `POST /api/auth/2fa/generate` - Generate 2FA secret
- `POST /api/auth/2fa/verify` - Verify 2FA code

## File System Operations

### List Directory
```bash
POST /api/fs/list
Authorization: <token>
Content-Type: application/json

{
  "path": "/",
  "password": "",
  "page": 1,
  "per_page": 30,
  "refresh": false
}
```

### Get File/Directory Info
```bash
POST /api/fs/get
Authorization: <token>
Content-Type: application/json

{
  "path": "/path/to/file.txt",
  "password": ""
}
```

### Search Files
```bash
POST /api/fs/search
Authorization: <token>
Content-Type: application/json

{
  "parent": "/",
  "keywords": "keyword",
  "scope": 0,
  "page": 1,
  "per_page": 30
}
```

### Create Directory
```bash
POST /api/fs/mkdir
Authorization: <token>
Content-Type: application/json

{
  "path": "/new-folder"
}
```

### Rename File/Directory
```bash
POST /api/fs/rename
Authorization: <token>
Content-Type: application/json

{
  "path": "/old-name.txt",
  "name": "new-name.txt"
}
```

### Delete Files/Directories
```bash
POST /api/fs/remove
Authorization: <token>
Content-Type: application/json

{
  "names": ["file1.txt", "folder1"],
  "dir": "/path/to/parent"
}
```

### Copy Files
```bash
POST /api/fs/copy
Authorization: <token>
Content-Type: application/json

{
  "src_dir": "/source",
  "dst_dir": "/destination",
  "names": ["file1.txt", "file2.txt"]
}
```

### Move Files
```bash
POST /api/fs/move
Authorization: <token>
Content-Type: application/json

{
  "src_dir": "/source",
  "dst_dir": "/destination",
  "names": ["file1.txt", "file2.txt"]
}
```

### Upload File
```bash
PUT /api/fs/put
Authorization: <token>
File-Path: <base64_encoded_path>
Content-Type: application/octet-stream

<binary file content>
```

Note: File-Path must be base64-encoded:
```bash
echo -n '/path/to/upload/file.txt' | base64 -w 0
```

### Upload File (Form Data)
```bash
POST /api/fs/form
Authorization: <token>
Content-Type: multipart/form-data

# Form fields:
# - file: File content
# - path: Target directory path
```

## Offline Download Operations

### List Available Tools
```bash
GET /api/fs/offline_download/tools
Authorization: <token>

# Response:
{
  "code": 200,
  "data": ["aria2", "qBittorrent", "115 Cloud", "PikPak", ...]
}
```

### Add Offline Download Task
```bash
POST /api/fs/add_offline_download
Authorization: <token>
Content-Type: application/json

{
  "urls": ["http://example.com/file.zip", "magnet:?xt=..."],
  "path": "/downloads",
  "tool": "aria2",
  "delete_policy": "delete_on_upload_succeed"
}

# Response:
{
  "code": 200,
  "data": {
    "tasks": [
      {
        "id": "task_123",
        "name": "file.zip",
        "state": "pending",
        "status": "queued"
      }
    ]
  }
}
```

Supported tools:
- aria2
- qBittorrent
- Transmission
- 115 Cloud
- 115 Open
- 123Pan
- 123 Open
- PikPak
- Thunder
- ThunderX
- ThunderBrowser

Delete policies:
- delete_on_upload_succeed
- delete_on_upload_failed
- delete_never
- delete_always

### List Offline Download Tasks
```bash
GET /api/fs/offline_download/list?page=1&per_page=10
Authorization: <token>

# Response:
{
  "code": 200,
  "data": {
    "content": [
      {
        "id": "task_123",
        "name": "file.zip",
        "state": "running",
        "status": "downloading",
        "progress": 45.5,
        "total_bytes": 1024000,
        "error": null
      }
    ],
    "total": 1
  }
}
```

### Get Task Info
```bash
GET /api/fs/offline_download/info?tid=<task_id>
Authorization: <token>
```

### Cancel Task
```bash
POST /api/fs/offline_download/cancel?tid=<task_id>
Authorization: <token>
```

### Delete Task
```bash
POST /api/fs/offline_download/delete?tid=<task_id>
Authorization: <token>
```

## Admin Operations

### List Storages
```bash
GET /api/admin/storage/list
Authorization: <token>

# Response:
{
  "code": 200,
  "data": {
    "content": [
      {
        "id": 1,
        "mount_path": "/local",
        "driver": "Local",
        "disabled": false
      }
    ]
  }
}
```

### Create Storage
```bash
POST /api/admin/storage/create
Authorization: <token>
Content-Type: application/json

{
  "mount_path": "/local",
  "order": 0,
  "driver": "Local",
  "addition": "{\"root_folder_path\":\"/data\"}",
  "remark": "Local storage",
  "disabled": false,
  "enable_sign": false,
  "order_by": "name",
  "order_direction": "asc"
}
```

### Update Storage
```bash
POST /api/admin/storage/update
Authorization: <token>
Content-Type: application/json

{
  "id": 1,
  "mount_path": "/local",
  ...
}
```

### Delete Storage
```bash
POST /api/admin/storage/delete
Authorization: <token>
Content-Type: application/json

{
  "id": 1
}
```

### User Management
- `GET /api/admin/user/list` - List all users
- `POST /api/admin/user/create` - Create new user
- `POST /api/admin/user/update` - Update user
- `POST /api/admin/user/delete` - Delete user

### Settings Management
- `GET /api/admin/setting/list` - Get all settings
- `POST /api/admin/setting/save` - Save settings

## Public Operations

### Get Public Settings
```bash
GET /api/public/settings
```

### Health Check
```bash
GET /api/public/ping
```

## Response Format

All responses follow this structure:

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### Common Error Codes
- `200` - Success
- `400` - Bad request (invalid parameters)
- `401` - Unauthorized (invalid or missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found
- `500` - Internal server error

## Tips

1. **Token Management**: Tokens may expire. Re-authenticate on 401 errors.
2. **Pagination**: Use `page` and `per_page` for large listings.
3. **Base64 Encoding**: Upload file paths must be base64-encoded.
4. **Password Protection**: Include `password` field when accessing protected directories.
5. **Refresh**: Set `refresh: true` to force backend refresh (may be slow).
