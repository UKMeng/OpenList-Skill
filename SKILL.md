---
name: openlist
description: Manage files on OpenList servers using their REST API. Use this skill when users want to interact with OpenList file servers for (1) listing directories and files, (2) uploading or downloading files, (3) searching for files, (4) managing storages and folders (create, delete, rename, copy, move), (5) adding offline download tasks (aria2, qBittorrent, cloud services), or (6) querying task status. OpenList is a file list program that supports multiple storage providers including local storage, cloud drives (OneDrive, Google Drive, Aliyun), and network protocols (WebDAV, FTP, SFTP, S3).
---

# OpenList Skill

Interact with OpenList servers using their REST API for comprehensive file management and offline downloads.

## Prerequisites

Users must provide:
1. **OpenList Server URL** (e.g., `https://demo.oplist.org`)
2. **Credentials** (username and password)

Store these in `openlist-config.json` in the workspace root.

## Quick Start

### Configuration Setup

Create `openlist-config.json`:

```json
{
  "server_url": "https://your-openlist-server.com",
  "username": "admin",
  "password": "your-password"
}
```

### Using the Helper Script

The `scripts/openlist.sh` helper script provides convenient access to all OpenList operations:

```bash
# Test connection
scripts/openlist.sh login

# List files
scripts/openlist.sh list /

# Upload file
scripts/openlist.sh upload ./local.txt /remote.txt

# Add offline download
scripts/openlist.sh offline-download "http://example.com/file.zip" /downloads aria2
```

Run `scripts/openlist.sh` without arguments to see all available commands.

## Core Operations

### Authentication

All operations require JWT token authentication. The helper script handles this automatically:

```bash
TOKEN=$(curl -s -X POST "${SERVER_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  | jq -r '.data.token')
```

Use the token in the `Authorization` header for all subsequent requests.

### File System Operations

#### List Directory
```bash
scripts/openlist.sh list [path] [page] [per_page]
```

API: `POST /api/fs/list`
- Path, pagination support (page, per_page)
- Returns: file list with name, size, is_dir, modified time

#### Search Files
```bash
scripts/openlist.sh search <keywords> [parent_path]
```

API: `POST /api/fs/search`
- Keywords, parent path, scope (0=current, 1=recursive)
- Pagination support

#### Create Directory
```bash
scripts/openlist.sh mkdir <path>
```

API: `POST /api/fs/mkdir`

#### Upload File
```bash
scripts/openlist.sh upload <local_file> <remote_path>
```

API: `PUT /api/fs/put`
- **Important**: Remote path must be base64-encoded in `File-Path` header
- Content sent as `application/octet-stream`

#### Delete Files
```bash
scripts/openlist.sh delete <name> <parent_dir>
```

API: `POST /api/fs/remove`
- Supports deleting multiple files via `names` array

#### Other Operations
- **Rename**: `POST /api/fs/rename` - Change file/folder name
- **Copy**: `POST /api/fs/copy` - Copy files between paths
- **Move**: `POST /api/fs/move` - Move files between paths
- **Get Info**: `POST /api/fs/get` - Get detailed file information

### Offline Download

OpenList supports offline downloads using various tools (aria2, qBittorrent, cloud services).

#### List Available Tools
```bash
scripts/openlist.sh offline-tools
```

API: `GET /api/fs/offline_download/tools`

Returns available download tools on the server.

#### Add Download Task
```bash
scripts/openlist.sh offline-download <url> <path> [tool] [delete_policy]
```

API: `POST /api/fs/add_offline_download`

Parameters:
- `urls`: Array of download URLs (HTTP, magnet links, torrents)
- `path`: Target directory path
- `tool`: Download tool name (default: aria2)
- `delete_policy`: When to delete source (default: delete_on_upload_succeed)

Supported tools:
- **Download clients**: aria2, qBittorrent, Transmission
- **Cloud services**: 115 Cloud, 115 Open, 123Pan, 123 Open, PikPak
- **Thunder series**: Thunder, ThunderX, ThunderBrowser

Delete policies:
- `delete_on_upload_succeed` - Delete after successful upload
- `delete_on_upload_failed` - Delete after failed upload
- `delete_never` - Never delete
- `delete_always` - Always delete

#### Manage Tasks
```bash
# List all tasks
scripts/openlist.sh offline-list [page] [per_page]

# Get task details
scripts/openlist.sh offline-info <task_id>

# Cancel running task
scripts/openlist.sh offline-cancel <task_id>

# Delete task record
scripts/openlist.sh offline-delete <task_id>
```

APIs:
- `GET /api/fs/offline_download/list` - List tasks with pagination
- `GET /api/fs/offline_download/info?tid=<id>` - Get task details
- `POST /api/fs/offline_download/cancel?tid=<id>` - Cancel task
- `POST /api/fs/offline_download/delete?tid=<id>` - Delete task

### Storage Management

```bash
scripts/openlist.sh storages
```

API: `GET /api/admin/storage/list`

Lists all configured storage providers (requires admin permissions).

## Response Format

All OpenList API responses follow this structure:

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

Common status codes:
- `200` - Success
- `400` - Bad request (invalid parameters)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found
- `500` - Internal server error

## Important Implementation Details

### Base64 Encoding for Uploads
File paths for uploads must be base64-encoded:
```bash
FILE_PATH_B64=$(echo -n '/path/to/file.txt' | base64 -w 0)
```

### Token Expiration
JWT tokens may expire. If you receive 401 errors, re-authenticate to get a fresh token.

### Pagination
Use `page` and `per_page` parameters for large directory listings to avoid performance issues.

### Password-Protected Directories
Include `"password": "..."` field in requests when accessing protected paths.

## Additional Resources

- **Complete API Reference**: See `references/API_REFERENCE.md` for detailed endpoint documentation with request/response examples
- **Usage Examples**: See `references/EXAMPLES.md` for complete workflow examples including batch downloads, monitoring, and sync operations
- **Installation Guide**: See `references/INSTALL.md` for setup instructions
- **Quick Reference**: See `references/README.md` for command overview
- **Test Script**: Run `scripts/test.sh` to validate the skill functionality

### External Documentation
- API Documentation: https://fox.oplist.org (interactive API docs)
- Official Docs: https://doc.oplist.org
- GitHub: https://github.com/OpenListTeam/OpenList
- Demo Server: https://demo.oplist.org (guest/guest)

## License

OpenList is licensed under AGPL-3.0. All API operations must comply with this license.
