# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **skill development project** for creating an OpenList API integration skill. The skill enables interaction with OpenList servers via their REST API. OpenList is a file list program supporting multiple storage providers (local storage, cloud drives, WebDAV, FTP, S3, etc.).

**Status**: Under active development. Functionality is not yet fully validated.

**Implementation**: Bash-based CLI tool that wraps OpenList REST API calls.

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
./test.sh

# Individual test of each function
./openlist.sh login     # Verify authentication works
./openlist.sh list /    # Test directory listing
./openlist.sh storages  # Test admin API access
```

### Using the Helper Script
```bash
# Test authentication
./openlist.sh login

# List directory contents
./openlist.sh list [path] [page] [per_page]

# Search for files
./openlist.sh search <keywords> [parent_path]

# Create directory
./openlist.sh mkdir <path>

# Upload file
./openlist.sh upload <local_file> <remote_path>

# Delete file/directory
./openlist.sh delete <name> <parent_dir>

# List storage providers
./openlist.sh storages

# Get file info
./openlist.sh info <path>

# Offline download operations
./openlist.sh offline-tools                                  # List available tools
./openlist.sh offline-download <url> <path> [tool] [policy] # Add download task
./openlist.sh offline-list [page] [per_page]                # List tasks
./openlist.sh offline-info <task_id>                         # Get task info
./openlist.sh offline-cancel <task_id>                       # Cancel task
./openlist.sh offline-delete <task_id>                       # Delete task
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
- Template provided as `openlist-config.template.json`
- Config must contain: `server_url`, `username`, `password`
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
- Example: `echo -n '/path/file.txt' | base64 -w 0`

### Helper Script Design (`openlist.sh`)
- Single bash script with function-based command routing
- Color-coded output (RED/GREEN/YELLOW) for user feedback
- Config validation before any operation
- Automatic login token acquisition per operation
- Uses `jq` for JSON parsing throughout

### Test Script (`test.sh`)
- Validates config existence and correctness
- Runs sequential tests: login → list → search → mkdir → upload → verify → cleanup
- Non-destructive: creates temporary test directory with timestamp
- Handles permission errors gracefully (some operations require admin)

## File Structure

- **openlist.sh** - Main helper script (290 lines), provides CLI wrapper around API
- **test.sh** - Test suite (132 lines), validates functionality end-to-end
- **SKILL.md** - API reference documentation (330 lines), comprehensive endpoint guide
- **EXAMPLES.md** - Usage examples (392 lines), 6 workflow examples including backup/sync/monitoring
- **README.md** - User-facing quick start guide
- **INSTALL.md** - Installation instructions for skill setup
- **openlist-config.template.json** - Config template for users to copy
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
- List available tools: GET `/api/fs/offline_download/tools`
- Add download task: POST `/api/fs/add_offline_download`
- List tasks: GET `/api/fs/offline_download/list` (with pagination)
- Get task info: GET `/api/fs/offline_download/info?tid=<task_id>`
- Cancel task: POST `/api/fs/offline_download/cancel?tid=<task_id>`
- Delete task: POST `/api/fs/offline_download/delete?tid=<task_id>`

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
```bash
FILE_PATH_B64=$(echo -n '/path/to/file.txt' | base64 -w 0)
curl -H "File-Path: ${FILE_PATH_B64}" ...
```
Note: Use `-w 0` flag to prevent line wrapping in base64 output.

### Error Response Handling
Always check the `code` field in responses:
```bash
CODE=$(echo "$RESPONSE" | jq -r '.code')
if [ "$CODE" != "200" ]; then
  # Handle error
fi
```

### Token Management
- Tokens expire after some time (server-configured)
- Each helper script invocation gets a fresh token
- No token persistence between runs
- For long-running operations, implement token refresh logic

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

Required system tools:
- `bash` - Shell script execution
- `curl` - HTTP API communication
- `jq` - JSON parsing and manipulation
- `base64` - File path encoding for uploads

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
3. Reference examples in EXAMPLES.md for proven curl patterns
4. Test against demo server: https://demo.oplist.org (guest/guest)

### Adding New API Operations
1. **Research**: Find endpoint in reference documentation
   - Check `reference/OpenList-Docs/pages/api/apidocs.md` for API doc links
   - Look for similar operations in `reference/OpenList/server/` Go code
2. **Implement**: Add function to openlist.sh following existing patterns:
   ```bash
   operation_name() {
       local param="$1"
       TOKEN=$(login)
       RESPONSE=$(curl -s -X POST "${SERVER_URL}/api/..." \
           -H "Authorization: $TOKEN" \
           -H "Content-Type: application/json" \
           -d "{\"field\":\"${param}\"}")
       CODE=$(echo "$RESPONSE" | jq -r '.code')
       if [ "$CODE" = "200" ]; then
           echo -e "${GREEN}Success${NC}"
       else
           echo -e "${RED}Failed${NC}"
           echo "$RESPONSE" | jq '.'
       fi
   }
   ```
3. **Test**: Add test case to test.sh if operation modifies state
4. **Document**: Update SKILL.md with endpoint details and examples

### Validating Existing Functionality
- Compare bash implementation against Go source in `reference/OpenList/server/`
- Check request/response formats match documentation
- Test error cases (invalid paths, missing auth, wrong permissions)
- Verify base64 encoding matches server expectations

### Debugging API Calls
Add `-v` flag to curl for verbose output:
```bash
curl -v -X POST "${SERVER_URL}/api/..." | jq '.'
```

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
# Use helper script login to get token
TOKEN=$(./openlist.sh login)

# Make raw API call
curl -s -X POST "https://demo.oplist.org/api/fs/list" \
  -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path":"/","page":1,"per_page":10}' | jq '.'
```

**Check response format**:
```bash
# All responses follow this structure
{
  "code": 200,           # HTTP-like status code
  "message": "success",  # Human-readable message
  "data": { ... }        # Actual response data
}
```
