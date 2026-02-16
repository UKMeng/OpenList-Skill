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

Store these in `openlist-config.json` in the workspace root. A template is provided at `assets/openlist-config.template.json`.

### System Dependencies

- Python 3.6+
- `requests` library:
  ```bash
  pip install requests
  ```

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

```bash
# Test connection
python scripts/openlist.py login

# List files
python scripts/openlist.py list /

# Upload file
python scripts/openlist.py upload ./local.txt /remote.txt

# Add offline download
python scripts/openlist.py offline-download "http://example.com/file.zip" /downloads aria2

# Get help
python scripts/openlist.py --help
```

## Core Operations

### Authentication

All operations require JWT token authentication. The helper script handles this automatically:

```bash
python scripts/openlist.py login
```

API: `POST /api/auth/login`

### File System Operations

#### List Directory
```bash
python scripts/openlist.py list [path] [--page N] [--per-page N]
```

API: `POST /api/fs/list`
- Returns: file list with name, size, is_dir, modified time

#### Search Files
```bash
python scripts/openlist.py search <keywords> [parent_path]
```

API: `POST /api/fs/search`

#### Create Directory
```bash
python scripts/openlist.py mkdir <path>
```

API: `POST /api/fs/mkdir`

#### Upload File
```bash
python scripts/openlist.py upload <local_file> <remote_path>
```

API: `PUT /api/fs/put`
- Remote path is base64-encoded in `File-Path` header (handled automatically)

#### Delete Files
```bash
python scripts/openlist.py delete <name> <parent_dir>
```

API: `POST /api/fs/remove`

#### Get File Info
```bash
python scripts/openlist.py info <path>
```

API: `POST /api/fs/get`

#### Rename File/Directory
```bash
python scripts/openlist.py rename <path> <new_name>
```

API: `POST /api/fs/rename`
- `path`: full path of the file/directory to rename
- `new_name`: new name (filename only, no path separators)

#### Move Files/Directories
```bash
python scripts/openlist.py move <src_dir> <dst_dir> <name1> [name2 ...]
```

API: `POST /api/fs/move`
- `src_dir`: source directory path
- `dst_dir`: destination directory path
- `names`: one or more file/directory names to move

#### Copy Files/Directories
```bash
python scripts/openlist.py copy <src_dir> <dst_dir> <name1> [name2 ...]
```

API: `POST /api/fs/copy`
- `src_dir`: source directory path
- `dst_dir`: destination directory path
- `names`: one or more file/directory names to copy

### Offline Download

OpenList supports offline downloads using various tools (aria2, qBittorrent, cloud services).

#### List Available Tools
```bash
python scripts/openlist.py offline-tools
```

API: `GET /api/public/offline_download_tools` (no auth required)

#### Add Download Task
```bash
python scripts/openlist.py offline-download <url> <path> [tool] [delete_policy]
```

API: `POST /api/fs/add_offline_download`

Supported tools: aria2, qBittorrent, Transmission, 115 Cloud, 115 Open, 123Pan, 123 Open, PikPak, Thunder, ThunderX, ThunderBrowser

Delete policies: `delete_on_upload_succeed`, `delete_on_upload_failed`, `delete_never`, `delete_always`

#### Manage Tasks
```bash
python scripts/openlist.py offline-list [--page N] [--per-page N]
python scripts/openlist.py offline-info <task_id>
python scripts/openlist.py offline-cancel <task_id>
python scripts/openlist.py offline-delete <task_id>
```

APIs:
- `GET /api/task/offline_download/undone` - List pending/running tasks
- `GET /api/task/offline_download/done` - List completed tasks
- `POST /api/task/offline_download/info?tid=<id>` - Get task details
- `POST /api/task/offline_download/cancel?tid=<id>` - Cancel task
- `POST /api/task/offline_download/delete?tid=<id>` - Delete task

### Storage Management

```bash
python scripts/openlist.py storages
```

API: `GET /api/admin/storage/list` (requires admin permissions)

## Response Format

All OpenList API responses follow this structure:

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

Common status codes: `200` Success, `401` Unauthorized, `403` Forbidden, `404` Not found

## Important Notes

- **Base64 encoding**: Upload file paths are base64-encoded automatically by the client
- **Token expiration**: Re-authenticate if you receive 401 errors
- **Config sources**: file (`openlist-config.json`), CLI flag (`--config`), or env var (`OPENLIST_CONFIG`)
- **Pagination**: Use `page` and `per_page` for large directory listings
- **Password-protected paths**: Include `"password": "..."` in requests when needed

## Additional Resources

- **Complete API Reference**: See `references/API_REFERENCE.md`
- **Usage Examples**: See `references/EXAMPLES.md` for workflow examples
- **Test Script**: Run `python scripts/test.py` to validate functionality

### External Documentation
- API Documentation: https://fox.oplist.org
- Official Docs: https://doc.oplist.org
- GitHub: https://github.com/OpenListTeam/OpenList
- Demo Server: https://demo.oplist.org (guest/guest)
