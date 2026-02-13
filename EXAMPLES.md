# OpenList API Examples

This document provides practical examples of using the OpenList API through this skill.

## Example 1: Complete File Management Workflow

```bash
#!/bin/bash

# Setup
SERVER_URL=$(jq -r '.server_url' openlist-config.json)
USERNAME=$(jq -r '.username' openlist-config.json)
PASSWORD=$(jq -r '.password' openlist-config.json)

# 1. Login
echo "=== Logging in ==="
TOKEN=$(curl -s -X POST "${SERVER_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}" \
  | jq -r '.data.token')

echo "Token obtained: ${TOKEN:0:20}..."

# 2. List root directory
echo -e "\n=== Listing root directory ==="
curl -s -X POST "${SERVER_URL}/api/fs/list" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"path":"/","page":1,"per_page":10}' \
  | jq '.data.content[] | {name, is_dir, size, modified}'

# 3. Create a test directory
echo -e "\n=== Creating test directory ==="
curl -s -X POST "${SERVER_URL}/api/fs/mkdir" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"path":"/test-openclaw"}' \
  | jq '.'

# 4. Create a test file
echo -e "\n=== Creating test file ==="
echo "Hello from OpenClaw!" > /tmp/test-file.txt

FILE_PATH_B64=$(echo -n '/test-openclaw/hello.txt' | base64 -w 0)
curl -s -X PUT "${SERVER_URL}/api/fs/put" \
  -H "Authorization: ${TOKEN}" \
  -H "File-Path: ${FILE_PATH_B64}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/tmp/test-file.txt \
  | jq '.'

# 5. Verify the upload
echo -e "\n=== Listing test directory ==="
curl -s -X POST "${SERVER_URL}/api/fs/list" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"path":"/test-openclaw","page":1,"per_page":10}' \
  | jq '.data.content[] | {name, size}'

# 6. Get file info
echo -e "\n=== Getting file info ==="
curl -s -X POST "${SERVER_URL}/api/fs/get" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"path":"/test-openclaw/hello.txt"}' \
  | jq '.data | {name, size, modified, sign}'

# 7. Rename the file
echo -e "\n=== Renaming file ==="
curl -s -X POST "${SERVER_URL}/api/fs/rename" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"path":"/test-openclaw/hello.txt","name":"greeting.txt"}' \
  | jq '.'

# 8. Copy file to another location
echo -e "\n=== Copying file ==="
curl -s -X POST "${SERVER_URL}/api/fs/copy" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"src_dir":"/test-openclaw","dst_dir":"/","names":["greeting.txt"]}' \
  | jq '.'

# 9. Search for the file
echo -e "\n=== Searching for 'greeting' ==="
curl -s -X POST "${SERVER_URL}/api/fs/search" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"parent":"/","keywords":"greeting","scope":0}' \
  | jq '.data.content[] | {name, parent}'

# 10. Clean up - delete test files
echo -e "\n=== Cleaning up ==="
curl -s -X POST "${SERVER_URL}/api/fs/remove" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"names":["test-openclaw"],"dir":"/"}' \
  | jq '.'

curl -s -X POST "${SERVER_URL}/api/fs/remove" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"names":["greeting.txt"],"dir":"/"}' \
  | jq '.'

echo -e "\n=== Done! ==="
```

## Example 2: Backup Files from Server

```bash
#!/bin/bash

# Download all files from a directory to local

SERVER_URL=$(jq -r '.server_url' openlist-config.json)
USERNAME=$(jq -r '.username' openlist-config.json)
PASSWORD=$(jq -r '.password' openlist-config.json)
REMOTE_DIR="${1:-/documents}"
LOCAL_DIR="${2:-./backup}"

# Login
TOKEN=$(curl -s -X POST "${SERVER_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}" \
  | jq -r '.data.token')

# Create local directory
mkdir -p "$LOCAL_DIR"

# List files
FILES=$(curl -s -X POST "${SERVER_URL}/api/fs/list" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"path\":\"${REMOTE_DIR}\",\"page\":1,\"per_page\":100}" \
  | jq -r '.data.content[] | select(.is_dir == false) | .name')

# Download each file
for file in $FILES; do
  echo "Downloading: $file"
  
  # Get download URL
  SIGN=$(curl -s -X POST "${SERVER_URL}/api/fs/get" \
    -H "Authorization: ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"path\":\"${REMOTE_DIR}/${file}\"}" \
    | jq -r '.data.sign')
  
  # Download
  curl -s "${SERVER_URL}/d${REMOTE_DIR}/${file}?sign=${SIGN}" \
    -o "${LOCAL_DIR}/${file}"
done

echo "Backup complete! Files saved to: $LOCAL_DIR"
```

## Example 3: Upload Directory to Server

```bash
#!/bin/bash

# Upload all files from a local directory to OpenList

SERVER_URL=$(jq -r '.server_url' openlist-config.json)
USERNAME=$(jq -r '.username' openlist-config.json)
PASSWORD=$(jq -r '.password' openlist-config.json)
LOCAL_DIR="${1:-.}"
REMOTE_DIR="${2:-/uploads}"

# Login
TOKEN=$(curl -s -X POST "${SERVER_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}" \
  | jq -r '.data.token')

# Create remote directory if needed
curl -s -X POST "${SERVER_URL}/api/fs/mkdir" \
  -H "Authorization: ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"path\":\"${REMOTE_DIR}\"}" > /dev/null

# Upload each file
find "$LOCAL_DIR" -type f | while read -r file; do
  filename=$(basename "$file")
  echo "Uploading: $filename"
  
  FILE_PATH_B64=$(echo -n "${REMOTE_DIR}/${filename}" | base64 -w 0)
  
  curl -s -X PUT "${SERVER_URL}/api/fs/put" \
    -H "Authorization: ${TOKEN}" \
    -H "File-Path: ${FILE_PATH_B64}" \
    -H "Content-Type: application/octet-stream" \
    --data-binary "@${file}" \
    | jq -r '.message'
done

echo "Upload complete!"
```

## Example 4: Sync Files Between Two OpenList Servers

```bash
#!/bin/bash

# Sync files from one OpenList server to another

SOURCE_SERVER="https://source.example.com"
SOURCE_USER="admin"
SOURCE_PASS="password1"
SOURCE_PATH="/documents"

DEST_SERVER="https://dest.example.com"
DEST_USER="admin"
DEST_PASS="password2"
DEST_PATH="/backup"

# Login to source
SOURCE_TOKEN=$(curl -s -X POST "${SOURCE_SERVER}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${SOURCE_USER}\",\"password\":\"${SOURCE_PASS}\"}" \
  | jq -r '.data.token')

# Login to destination
DEST_TOKEN=$(curl -s -X POST "${DEST_SERVER}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${DEST_USER}\",\"password\":\"${DEST_PASS}\"}" \
  | jq -r '.data.token')

# Create destination directory
curl -s -X POST "${DEST_SERVER}/api/fs/mkdir" \
  -H "Authorization: ${DEST_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"path\":\"${DEST_PATH}\"}" > /dev/null

# List source files
FILES=$(curl -s -X POST "${SOURCE_SERVER}/api/fs/list" \
  -H "Authorization: ${SOURCE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"path\":\"${SOURCE_PATH}\",\"page\":1,\"per_page\":100}" \
  | jq -r '.data.content[] | select(.is_dir == false) | .name')

# Sync each file
for file in $FILES; do
  echo "Syncing: $file"
  
  # Get source download URL
  SIGN=$(curl -s -X POST "${SOURCE_SERVER}/api/fs/get" \
    -H "Authorization: ${SOURCE_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"path\":\"${SOURCE_PATH}/${file}\"}" \
    | jq -r '.data.sign')
  
  # Download from source and upload to destination
  FILE_PATH_B64=$(echo -n "${DEST_PATH}/${file}" | base64 -w 0)
  
  curl -s "${SOURCE_SERVER}/d${SOURCE_PATH}/${file}?sign=${SIGN}" | \
    curl -s -X PUT "${DEST_SERVER}/api/fs/put" \
      -H "Authorization: ${DEST_TOKEN}" \
      -H "File-Path: ${FILE_PATH_B64}" \
      -H "Content-Type: application/octet-stream" \
      --data-binary @- \
      | jq -r '.message'
done

echo "Sync complete!"
```

## Example 5: Monitor Directory Changes

```bash
#!/bin/bash

# Monitor a directory for changes and log them

SERVER_URL=$(jq -r '.server_url' openlist-config.json)
USERNAME=$(jq -r '.username' openlist-config.json)
PASSWORD=$(jq -r '.password' openlist-config.json)
WATCH_DIR="${1:-/}"

STATE_FILE="/tmp/openlist-monitor-state.json"

# Login
get_token() {
  curl -s -X POST "${SERVER_URL}/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}" \
    | jq -r '.data.token'
}

# Get current state
get_state() {
  local token="$1"
  curl -s -X POST "${SERVER_URL}/api/fs/list" \
    -H "Authorization: ${token}" \
    -H "Content-Type: application/json" \
    -d "{\"path\":\"${WATCH_DIR}\",\"page\":1,\"per_page\":100}" \
    | jq '.data.content | map({name, size, modified}) | sort_by(.name)'
}

# Initialize
TOKEN=$(get_token)
echo "Starting monitor for: $WATCH_DIR"
get_state "$TOKEN" > "$STATE_FILE"

# Monitor loop
while true; do
  sleep 30
  
  TOKEN=$(get_token)
  CURRENT_STATE=$(get_state "$TOKEN")
  
  # Compare
  DIFF=$(diff -u "$STATE_FILE" <(echo "$CURRENT_STATE"))
  
  if [ -n "$DIFF" ]; then
    echo "=== Changes detected at $(date) ==="
    echo "$DIFF"
    echo "$CURRENT_STATE" > "$STATE_FILE"
  fi
done
```

## Example 6: Generate Storage Report

```bash
#!/bin/bash

# Generate a report of all files and storage usage

SERVER_URL=$(jq -r '.server_url' openlist-config.json)
USERNAME=$(jq -r '.username' openlist-config.json)
PASSWORD=$(jq -r '.password' openlist-config.json)

# Login
TOKEN=$(curl -s -X POST "${SERVER_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}" \
  | jq -r '.data.token')

# Get storages
echo "=== OpenList Storage Report ==="
echo "Generated: $(date)"
echo ""

STORAGES=$(curl -s -X GET "${SERVER_URL}/api/admin/storage/list" \
  -H "Authorization: ${TOKEN}" \
  | jq -r '.data.content[] | @json')

echo "$STORAGES" | while read -r storage; do
  MOUNT=$(echo "$storage" | jq -r '.mount_path')
  DRIVER=$(echo "$storage" | jq -r '.driver')
  DISABLED=$(echo "$storage" | jq -r '.disabled')
  
  echo "Storage: $MOUNT"
  echo "Driver: $DRIVER"
  echo "Status: $([ "$DISABLED" = "false" ] && echo "Enabled" || echo "Disabled")"
  
  # Count files and calculate total size
  STATS=$(curl -s -X POST "${SERVER_URL}/api/fs/list" \
    -H "Authorization: ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"path\":\"${MOUNT}\",\"page\":1,\"per_page\":1000,\"refresh\":false}" \
    | jq '.data.content | {
      total: length,
      files: map(select(.is_dir == false)) | length,
      dirs: map(select(.is_dir == true)) | length,
      size: map(select(.is_dir == false) | .size) | add
    }')
  
  echo "$STATS" | jq -r '"  Total items: \(.total)\n  Files: \(.files)\n  Directories: \(.dirs)\n  Total size: \(.size) bytes"'
  echo ""
done

echo "=== End of Report ==="
```

## Tips for Using These Examples

1. **Save scripts**: Save these examples as `.sh` files and make them executable with `chmod +x`

2. **Error handling**: Add proper error checking for production use

3. **Token refresh**: For long-running scripts, implement token refresh logic

4. **Rate limiting**: Be mindful of API rate limits and add delays between requests

5. **Logging**: Add logging to track operations and debug issues

6. **Backup before delete**: Always verify before running destructive operations

7. **Test on demo**: Test scripts on the demo server first: https://demo.oplist.org
