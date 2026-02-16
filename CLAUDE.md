# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **skill development project** for creating an OpenList API integration skill. The skill enables interaction with OpenList servers via their REST API. OpenList is a file list program supporting multiple storage providers (local storage, cloud drives, WebDAV, FTP, S3, etc.).

**Status**: Under active development. Functionality is not yet fully validated.

**Implementation**: Python-based CLI tool that wraps OpenList REST API calls.

## Reference Materials

The `reference/` directory contains upstream source code and documentation:

- **reference/OpenList/** - OpenList server source code (Go project)
  - Backend implementation reference
  - API endpoint definitions in `server/` directory
  - Driver implementations in `drivers/` directory
  - 29 subdirectories including cmd, internal, pkg, server

- **reference/OpenList-Docs/** - Official OpenList documentation (Valaxy-based site)
  - 127+ markdown documentation files
  - API documentation in `pages/api/`
  - Driver guides in `pages/guide/drivers/`
  - Configuration references in `pages/configuration/`
  - FAQ and troubleshooting in `pages/faq/`

**When developing**: Always check `reference/` for authoritative API behavior, error codes, and endpoint specifications before implementing or modifying functionality.

## Key Commands

### Development & Testing
```bash
# Run full test suite (requires openlist-config.json)
# WARNING: Tests create/delete temporary directories - ensure config points to test server
python3 scripts/test.py

# Individual test of each function
python3 scripts/openlist.py login     # Verify authentication works
python3 scripts/openlist.py list /    # Test directory listing
python3 scripts/openlist.py storages  # Test admin API access
```

### Using the Helper Script
```bash
# Test authentication
python3 scripts/openlist.py login

# List directory contents
python3 scripts/openlist.py list [path] [--page N] [--per-page N]

# Search for files
python3 scripts/openlist.py search <keywords> [parent_path]

# Create directory
python3 scripts/openlist.py mkdir <path>

# Upload file
python3 scripts/openlist.py upload <local_file> <remote_path>

# Delete file/directory
python3 scripts/openlist.py delete <name> <parent_dir>

# List storage providers
python3 scripts/openlist.py storages

# Get file info
python3 scripts/openlist.py info <path>

# Offline download operations
python3 scripts/openlist.py offline-tools                                          # List available tools
python3 scripts/openlist.py offline-download <url> <path> [tool] [delete_policy]   # Add download task
python3 scripts/openlist.py offline-list [--page N] [--per-page N]                 # List tasks
python3 scripts/openlist.py offline-info <task_id>                                 # Get task info
python3 scripts/openlist.py offline-cancel <task_id>                               # Cancel task
python3 scripts/openlist.py offline-delete <task_id>                               # Delete task

# View all commands
python3 scripts/openlist.py --help
```

## Architecture

### Project Status & Validation

**Current State**: Skill implementation is functional but not fully validated. Known areas needing verification:
- Error handling edge cases
- Large file upload behavior
- Pagination with 1000+ items
- All admin endpoints (user/storage management)
- 2FA authentication flow

**When implementing new features**: Test against a dedicated test server, not production.

### Configuration System
- Configuration is stored in `openlist-config.json` (workspace root, not in repo)
- Template provided as `assets/openlist-config.template.json`
- Config must contain: `server_url`, `username`, `password`
- Config path can be overridden via `--config` flag or `OPENLIST_CONFIG` environment variable
- Security: config file is gitignored to prevent credential leakage

### Authentication Flow
1. Load credentials from `openlist-config.json`
2. POST to `/api/auth/login` with username/password
3. Extract JWT token from response `data.token` field
4. Include token in `Authorization` header for all subsequent API calls
5. Tokens are session-based (not persisted), re-authenticate on each script run

### API Communication
- All API endpoints use JSON request/response format
- Base URL from config: `${SERVER_URL}/api/...`
- Response structure: `{"code": 200, "message": "success", "data": {...}}`
- Error handling: check `code` field (200=success, 401=unauthorized, 404=not found)

### File Upload Mechanism
- Uses PUT to `/api/fs/put` endpoint
- File path must be base64-encoded in `File-Path` header
- Content sent as `application/octet-stream` in request body
- Python: `base64.b64encode(path.encode('utf-8')).decode('ascii')`

### Helper Script Design (`scripts/openlist.py`)
- Python CLI tool using `argparse` for command routing
- `OpenListClient` class provides all API operations
- Color-coded output (RED/GREEN/YELLOW) for user feedback
- Config validation before any operation
- Automatic login token acquisition per operation
- Uses `requests` library for HTTP communication

### Test Script (`scripts/test.py`)
- Validates config existence and correctness
- Runs sequential tests: login → list → search → mkdir → upload → verify → cleanup
- Non-destructive: creates temporary test directory with timestamp
- Handles permission errors gracefully (some operations require admin)

## File Structure

- **scripts/openlist.py** - Main helper script, provides CLI wrapper around API
- **scripts/test.py** - Test suite, validates functionality end-to-end
- **SKILL.md** - API reference documentation, comprehensive endpoint guide
- **references/EXAMPLES.md** - Usage examples, workflow examples including backup/sync/monitoring
- **references/API_REFERENCE.md** - Detailed API endpoint documentation
- **assets/openlist-config.template.json** - Config template for users to copy
- **reference/** - Contains upstream OpenList source and docs (read-only reference)

## OpenList API Coverage

### File System Operations
- List directory: POST `/api/fs/list` (with pagination)
- Get file info: POST `/api/fs/get`
- Search: POST `/api/fs/search` (supports keyword + parent scope)
- Create directory: POST `/api/fs/mkdir`
- Rename: POST `/api/fs/rename`
- Delete: POST `/api/fs/remove` (supports multiple files via names array)
- Copy: POST `/api/fs/copy`
- Move: POST `/api/fs/move`
- Upload: PUT `/api/fs/put` (requires base64-encoded File-Path header)

### Offline Download Operations
- List available tools: GET `/api/public/offline_download_tools` (public, no auth)
- Add download task: POST `/api/fs/add_offline_download`
- List undone tasks: GET `/api/task/offline_download/undone`
- List done tasks: GET `/api/task/offline_download/done`
- Get task info: POST `/api/task/offline_download/info?tid=<task_id>`
- Cancel task: POST `/api/task/offline_download/cancel?tid=<task_id>`
- Delete task: POST `/api/task/offline_download/delete?tid=<task_id>`

### Supported Download Tools
- **aria2** - Aria2 download client
- **qBittorrent** - qBittorrent client
- **Transmission** - Transmission client
- **115 Cloud** - 115 cloud offline download
- **115 Open** - 115 Open platform
- **123Pan** - 123 Pan cloud service
- **123 Open** - 123 Open platform
- **PikPak** - PikPak cloud service
- **Thunder** - Thunder (Xunlei) download
- **ThunderX** - Thunder X
- **ThunderBrowser** - Thunder Browser

### Admin Operations
- List storages: GET `/api/admin/storage/list`
- Create storage: POST `/api/admin/storage/create`
- User management: `/api/admin/user/*`
- Settings: `/api/admin/setting/*`

### Authentication
- Login: POST `/api/auth/login`
- 2FA: POST `/api/auth/2fa/generate`, `/api/auth/2fa/verify`

## Important Implementation Details

### Base64 Encoding for File Paths
When uploading files, the remote path must be base64-encoded:
```python
import base64
file_path_b64 = base64.b64encode('/path/to/file.txt'.encode('utf-8')).decode('ascii')
```

### Error Response Handling
Always check the `code` field in responses:
```python
data = response.json()
if data.get('code') != 200:
    # Handle error
    print(data.get('message'))
```

### Token Management
- Tokens expire after some time (server-configured)
- Each script invocation gets a fresh token
- No token persistence between runs
- `OpenListClient` auto-acquires token on first API call

### Pagination
List operations support pagination:
- `page`: Page number (1-indexed)
- `per_page`: Items per page (default 30)
- Large directories should paginate results

### Password-Protected Directories
Some directories may require passwords:
- Include `"password": "..."` in request body when accessing protected paths
- Password field is optional for unprotected directories

## Dependencies

- Python 3.6+
- `requests` library - Install with `pip install requests`

## Known Issues & TODOs

As this is a work-in-progress skill, be aware of:

1. **Incomplete Testing**: Not all API endpoints have been validated
2. **Error Handling**: May not cover all edge cases (network timeouts, malformed responses)
3. **Large Files**: Upload/download of large files (>100MB) not tested
4. **Concurrent Operations**: No testing with multiple simultaneous operations
5. **Token Refresh**: Long-running scripts don't implement token refresh
6. **Binary Files**: Upload of binary files needs validation
7. **Special Characters**: File paths with special characters may need escaping

**When encountering issues**: Check `reference/OpenList/` source code for correct API behavior.

## Reference Documentation

**Primary API Reference** (live documentation with interactive testing):
- English: https://fox.oplist.org
- Chinese: https://fox.oplist.org.cn

**Local Reference Materials**:
- `reference/OpenList/` - Server source code (Go)
  - API handlers: `reference/OpenList/server/handles/`
  - File system operations: `reference/OpenList/server/handles/fs*.go`
  - Admin operations: `reference/OpenList/server/handles/admin*.go`
- `reference/OpenList-Docs/` - Official documentation (127+ pages)
  - API overview: `pages/api/`
  - Guides: `pages/guide/`
  - FAQ: `pages/faq/`

**External Resources**:
- Official Docs: https://doc.oplist.org
- GitHub: https://github.com/OpenListTeam/OpenList
- Demo Server: https://demo.oplist.org (username: guest, password: guest)
- License: AGPL-3.0

## Development Workflows

### Finding API Specifications
1. Check `reference/OpenList-Docs/pages/api/` for official API documentation
2. Look at `reference/OpenList/server/` for Go backend implementation
3. Reference examples in references/EXAMPLES.md for proven patterns
4. Test against demo server: https://demo.oplist.org (guest/guest)

### Adding New API Operations
1. **Research**: Find endpoint in reference documentation
   - Check `reference/OpenList-Docs/pages/api/apidocs.md` for API doc links
   - Look for similar operations in `reference/OpenList/server/` Go code
2. **Implement**: Add method to `OpenListClient` in `scripts/openlist.py` following existing patterns:
   ```python
   def operation_name(self, param: str) -> Dict:
       """Description of the operation"""
       try:
           response = requests.post(
               f"{self.server_url}/api/...",
               headers=self._get_headers(),
               json={"field": param},
               timeout=30
           )
           data = response.json()
           if data.get('code') == 200:
               print(Colors.green("Success"))
           else:
               print(Colors.red("Failed"))
               print(json.dumps(data, indent=2))
           return data
       except requests.RequestException as e:
           print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
           sys.exit(1)
   ```
3. **Add CLI subcommand**: Register the new command in the `main()` function's argparse setup
4. **Test**: Add test case to `scripts/test.py` if operation modifies state
5. **Document**: Update SKILL.md with endpoint details and examples

### Validating Existing Functionality
- Compare Python implementation against Go source in `reference/OpenList/server/`
- Check request/response formats match documentation
- Test error cases (invalid paths, missing auth, wrong permissions)
- Verify base64 encoding matches server expectations

### Testing Against Demo Server
Use demo server for testing without local OpenList installation:
```json
{
  "server_url": "https://demo.oplist.org",
  "username": "guest",
  "password": "guest"
}
```
**Note**: Demo server has limited write permissions. Some operations (mkdir, upload, delete, admin endpoints) may fail with 403.

### Common Development Tasks

**Verify API endpoint exists**:
```bash
# Search in Go source for handler
grep -r "api/fs/list" reference/OpenList/server/

# Check documentation
find reference/OpenList-Docs/pages -name "*.md" -exec grep -l "api/fs/list" {} \;
```

**Test new endpoint manually**:
```bash
python3 scripts/openlist.py login
# Then use the relevant command, e.g.:
python3 scripts/openlist.py list / --page 1 --per-page 10
```

**Check response format**:
```json
// All responses follow this structure
{
  "code": 200,           // HTTP-like status code
  "message": "success",  // Human-readable message
  "data": { ... }        // Actual response data
}
```
