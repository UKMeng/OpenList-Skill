# OpenList Skill

This skill enables OpenClaw to interact with OpenList servers using their REST API.

## What is OpenList?

OpenList is a file list program that supports multiple storage providers:
- Local storage
- Cloud drives (OneDrive, Google Drive, Aliyun, etc.)
- Network protocols (WebDAV, FTP, SFTP, S3)
- And many more...

It's a fork of AList focused on long-term governance and transparency, licensed under AGPL-3.0.

## Files

- **SKILL.md** - Main skill documentation with API reference
- **openlist.sh** - Helper script for common operations
- **openlist-config.template.json** - Configuration template

## Quick Start

### 1. Create Configuration

Copy the template to your workspace root:

```bash
cp .openclaw/skills/openlist/openlist-config.template.json openlist-config.json
```

Edit `openlist-config.json` with your server details:

```json
{
  "server_url": "https://your-server.com",
  "username": "admin",
  "password": "your-password"
}
```

### 2. Test Connection

Use the helper script to test:

```bash
.openclaw/skills/openlist/openlist.sh login
```

### 3. List Files

```bash
.openclaw/skills/openlist/openlist.sh list /
```

## Usage Examples

### List Directory
```bash
.openclaw/skills/openlist/openlist.sh list /documents
```

### Search Files
```bash
.openclaw/skills/openlist/openlist.sh search "report" /
```

### Create Directory
```bash
.openclaw/skills/openlist/openlist.sh mkdir /new-folder
```

### Upload File
```bash
.openclaw/skills/openlist/openlist.sh upload ./local-file.txt /remote/path/file.txt
```

### Delete File
```bash
.openclaw/skills/openlist/openlist.sh delete file.txt /parent-directory
```

### List Storages
```bash
.openclaw/skills/openlist/openlist.sh storages
```

### Offline Download
```bash
# List available download tools
.openclaw/skills/openlist/openlist.sh offline-tools

# Add offline download task
.openclaw/skills/openlist/openlist.sh offline-download "http://example.com/file.zip" /downloads aria2

# List offline download tasks
.openclaw/skills/openlist/openlist.sh offline-list

# Get task information
.openclaw/skills/openlist/openlist.sh offline-info <task_id>

# Cancel a task
.openclaw/skills/openlist/openlist.sh offline-cancel <task_id>

# Delete a task
.openclaw/skills/openlist/openlist.sh offline-delete <task_id>
```

## API Operations Supported

- ✅ Authentication (login with JWT)
- ✅ List directory contents
- ✅ Get file/directory info
- ✅ Search files
- ✅ Create directories
- ✅ Upload files
- ✅ Delete files/directories
- ✅ Rename files/directories
- ✅ Copy files
- ✅ Move files
- ✅ List storage providers
- ✅ Offline download (Aria2, qBittorrent, cloud services)
- ✅ Offline download task management
- ✅ Admin operations (user/storage management)

## Direct API Access

You can also make direct API calls using curl. See SKILL.md for detailed API documentation.

Example:

```bash
# Load config
SERVER_URL=$(jq -r '.server_url' openlist-config.json)
USERNAME=$(jq -r '.username' openlist-config.json)
PASSWORD=$(jq -r '.password' openlist-config.json)

# Login
TOKEN=$(curl -s -X POST "${SERVER_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}" \
  | jq -r '.data.token')

# List files
curl -s -X POST "${SERVER_URL}/api/fs/list" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"path":"/","page":1,"per_page":30}' \
  | jq '.'
```

## Resources

- **API Documentation**: https://fox.oplist.org
- **Official Docs**: https://doc.oplist.org
- **GitHub**: https://github.com/OpenListTeam/OpenList
- **Demo**: https://demo.oplist.org

## License

OpenList is licensed under AGPL-3.0. All operations using this skill must comply with this license.

## Security Notes

1. Store credentials securely in `openlist-config.json`
2. Do not commit `openlist-config.json` to version control
3. JWT tokens are obtained per-session and not persisted
4. Always verify the server's SSL certificate in production

## Troubleshooting

### Config file not found
Make sure `openlist-config.json` exists in your workspace root.

### Login failed
Check your server URL, username, and password in the config file.

### 401 Unauthorized
Your token may have expired. Re-authenticate to get a fresh token.

### Connection refused
Verify the server URL is correct and the server is accessible.

## Contributing

Found a bug or want to add features? The OpenList project welcomes contributions!
