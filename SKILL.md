# OpenList Skill

**Use this skill when the user wants to:**
- Manage files on an OpenList server
- List directories and files
- Upload, download, or delete files
- Search for files
- Manage storage providers
- Configure OpenList settings

## Overview

OpenList is a file list program that supports multiple storage providers (local, OneDrive, Google Drive, Aliyun, etc.). This skill provides direct API access to OpenList servers.

## Prerequisites

The user must provide:
1. **OpenList Server URL** (e.g., `https://demo.oplist.org`)
2. **Admin credentials** (username and password) for authenticated operations

Store these in `openlist-config.json` in the workspace root after first setup.

## Configuration

Create `openlist-config.json` in the workspace:

```json
{
  "server_url": "https://your-openlist-server.com",
  "username": "admin",
  "password": "your-password"
}
```

## Common Operations

### 1. Authentication

OpenList uses JWT token authentication. All authenticated requests require a token obtained from login.

```bash
# Login and get token
curl -X POST "${SERVER_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'

# Response:
# {
#   "code": 200,
#   "message": "success",
#   "data": {
#     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
#   }
# }
```

### 2. List Files/Directories

```bash
# List files in a directory
curl -X POST "${SERVER_URL}/api/fs/list" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/",
    "password": "",
    "page": 1,
    "per_page": 30,
    "refresh": false
  }'
```

### 3. Get File Info

```bash
# Get detailed file/directory information
curl -X POST "${SERVER_URL}/api/fs/get" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/file.txt",
    "password": ""
  }'
```

### 4. Search Files

```bash
# Search for files
curl -X POST "${SERVER_URL}/api/fs/search" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": "/",
    "keywords": "keyword",
    "scope": 0,
    "page": 1,
    "per_page": 30
  }'
```

### 5. Create Directory

```bash
# Create a new directory
curl -X POST "${SERVER_URL}/api/fs/mkdir" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/new-folder"
  }'
```

### 6. Rename File/Directory

```bash
# Rename file or directory
curl -X POST "${SERVER_URL}/api/fs/rename" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/old-name.txt",
    "name": "new-name.txt"
  }'
```

### 7. Delete File/Directory

```bash
# Delete file or directory
curl -X POST "${SERVER_URL}/api/fs/remove" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "names": ["file1.txt", "folder1"],
    "dir": "/path/to/parent"
  }'
```

### 8. Copy Files

```bash
# Copy files between paths
curl -X POST "${SERVER_URL}/api/fs/copy" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "src_dir": "/source",
    "dst_dir": "/destination",
    "names": ["file1.txt", "file2.txt"]
  }'
```

### 9. Move Files

```bash
# Move files between paths
curl -X POST "${SERVER_URL}/api/fs/move" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "src_dir": "/source",
    "dst_dir": "/destination",
    "names": ["file1.txt", "file2.txt"]
  }'
```

### 10. Upload File

```bash
# Upload a file (form-data)
curl -X PUT "${SERVER_URL}/api/fs/put" \
  -H "Authorization: ${TOKEN}" \
  -H "File-Path: $(echo -n '/path/to/upload/file.txt' | base64 -w 0)" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @local-file.txt
```

### 11. Get Storage List

```bash
# List all configured storages
curl -X GET "${SERVER_URL}/api/admin/storage/list" \
  -H "Authorization: ${TOKEN}"
```

### 12. Add Storage

```bash
# Add a new storage provider
curl -X POST "${SERVER_URL}/api/admin/storage/create" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "mount_path": "/local",
    "order": 0,
    "driver": "Local",
    "addition": "{\"root_folder_path\":\"/data\"}",
    "remark": "Local storage",
    "disabled": false,
    "enable_sign": false,
    "order_by": "name",
    "order_direction": "asc"
  }'
```

## Workflow Example

Here's a typical workflow for managing files:

```bash
# 1. Load config
SERVER_URL=$(jq -r '.server_url' openlist-config.json)
USERNAME=$(jq -r '.username' openlist-config.json)
PASSWORD=$(jq -r '.password' openlist-config.json)

# 2. Login and get token
TOKEN=$(curl -s -X POST "${SERVER_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}" \
  | jq -r '.data.token')

# 3. List root directory
curl -s -X POST "${SERVER_URL}/api/fs/list" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"path":"/","page":1,"per_page":30}' \
  | jq '.data.content[] | {name, size, is_dir, modified}'

# 4. Create a directory
curl -s -X POST "${SERVER_URL}/api/fs/mkdir" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"path":"/test-folder"}'

# 5. Upload a file
echo "Hello OpenList" > test.txt
FILE_PATH_B64=$(echo -n '/test-folder/test.txt' | base64 -w 0)
curl -X PUT "${SERVER_URL}/api/fs/put" \
  -H "Authorization: ${TOKEN}" \
  -H "File-Path: ${FILE_PATH_B64}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @test.txt
```

## API Endpoints Reference

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/2fa/generate` - Generate 2FA secret
- `POST /api/auth/2fa/verify` - Verify 2FA code

### File System Operations
- `POST /api/fs/list` - List directory contents
- `POST /api/fs/get` - Get file/directory info
- `POST /api/fs/search` - Search files
- `POST /api/fs/mkdir` - Create directory
- `POST /api/fs/rename` - Rename file/directory
- `POST /api/fs/remove` - Delete files/directories
- `POST /api/fs/copy` - Copy files
- `POST /api/fs/move` - Move files
- `PUT /api/fs/put` - Upload file
- `POST /api/fs/form` - Upload file (form-data)

### Admin Operations
- `GET /api/admin/storage/list` - List all storages
- `POST /api/admin/storage/create` - Add storage
- `POST /api/admin/storage/update` - Update storage
- `POST /api/admin/storage/delete` - Delete storage
- `GET /api/admin/user/list` - List users
- `POST /api/admin/user/create` - Create user
- `POST /api/admin/user/update` - Update user
- `POST /api/admin/user/delete` - Delete user
- `GET /api/admin/setting/list` - Get settings
- `POST /api/admin/setting/save` - Save settings

### Public Operations
- `GET /api/public/settings` - Get public settings
- `GET /api/public/ping` - Health check

## Error Handling

OpenList API returns responses in this format:

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

Common error codes:
- `200` - Success
- `400` - Bad request (invalid parameters)
- `401` - Unauthorized (invalid or missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found
- `500` - Internal server error

Always check the `code` field in responses and handle errors appropriately.

## Tips

1. **Token Expiration**: JWT tokens may expire. If you get 401 errors, re-authenticate to get a fresh token.

2. **Path Encoding**: For file uploads, the `File-Path` header must be base64-encoded.

3. **Pagination**: Use `page` and `per_page` parameters for large directory listings.

4. **Password Protection**: Some directories may be password-protected. Include the `password` field in requests when accessing protected paths.

5. **Refresh**: Set `refresh: true` in list requests to force a refresh from the storage backend (may be slow).

## Documentation

- API Documentation: https://fox.oplist.org
- Official Docs: https://doc.oplist.org
- GitHub: https://github.com/OpenListTeam/OpenList

## License

OpenList is licensed under AGPL-3.0. All API operations and code must comply with this license.

---

**Remember**: Always load `openlist-config.json` before making API calls, and handle authentication tokens securely. Store tokens temporarily during the session and don't persist them in files.
