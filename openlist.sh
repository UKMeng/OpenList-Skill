#!/bin/bash
# OpenList API Helper Script
# This script provides convenient functions for OpenList operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Config file path
CONFIG_FILE="${OPENLIST_CONFIG:-openlist-config.json}"

# Check if config exists
check_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}Error: Config file not found at $CONFIG_FILE${NC}"
        echo "Please create it from the template:"
        echo "  cp .openclaw/skills/openlist/openlist-config.template.json openlist-config.json"
        echo "Then edit it with your server details."
        exit 1
    fi
}

# Load config
load_config() {
    check_config
    SERVER_URL=$(jq -r '.server_url' "$CONFIG_FILE")
    USERNAME=$(jq -r '.username' "$CONFIG_FILE")
    PASSWORD=$(jq -r '.password' "$CONFIG_FILE")
    
    if [ "$SERVER_URL" = "null" ] || [ "$USERNAME" = "null" ] || [ "$PASSWORD" = "null" ]; then
        echo -e "${RED}Error: Config file is incomplete${NC}"
        exit 1
    fi
}

# Login and get token
login() {
    load_config
    
    echo -e "${YELLOW}Logging in to $SERVER_URL...${NC}"
    
    RESPONSE=$(curl -s -X POST "${SERVER_URL}/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}")
    
    CODE=$(echo "$RESPONSE" | jq -r '.code')
    
    if [ "$CODE" != "200" ]; then
        echo -e "${RED}Login failed!${NC}"
        echo "$RESPONSE" | jq '.'
        exit 1
    fi
    
    TOKEN=$(echo "$RESPONSE" | jq -r '.data.token')
    
    if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
        echo -e "${RED}Failed to get token${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Login successful!${NC}"
    echo "$TOKEN"
}

# List directory
list_dir() {
    local path="${1:-/}"
    local page="${2:-1}"
    local per_page="${3:-30}"
    
    TOKEN=$(login)
    
    echo -e "${YELLOW}Listing: $path${NC}"
    
    curl -s -X POST "${SERVER_URL}/api/fs/list" \
        -H "Authorization: $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"path\":\"${path}\",\"page\":${page},\"per_page\":${per_page}}" \
        | jq '.data.content[] | {name, size, is_dir, modified}'
}

# Get file info
get_info() {
    local path="$1"
    
    if [ -z "$path" ]; then
        echo -e "${RED}Error: Path is required${NC}"
        exit 1
    fi
    
    TOKEN=$(login)
    
    curl -s -X POST "${SERVER_URL}/api/fs/get" \
        -H "Authorization: $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"path\":\"${path}\"}" \
        | jq '.'
}

# Search files
search() {
    local keywords="$1"
    local parent="${2:-/}"
    
    if [ -z "$keywords" ]; then
        echo -e "${RED}Error: Keywords are required${NC}"
        exit 1
    fi
    
    TOKEN=$(login)
    
    echo -e "${YELLOW}Searching for: $keywords in $parent${NC}"
    
    curl -s -X POST "${SERVER_URL}/api/fs/search" \
        -H "Authorization: $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"parent\":\"${parent}\",\"keywords\":\"${keywords}\",\"scope\":0,\"page\":1,\"per_page\":30}" \
        | jq '.data.content[] | {name, size, parent}'
}

# Create directory
mkdir_remote() {
    local path="$1"
    
    if [ -z "$path" ]; then
        echo -e "${RED}Error: Path is required${NC}"
        exit 1
    fi
    
    TOKEN=$(login)
    
    echo -e "${YELLOW}Creating directory: $path${NC}"
    
    RESPONSE=$(curl -s -X POST "${SERVER_URL}/api/fs/mkdir" \
        -H "Authorization: $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"path\":\"${path}\"}")
    
    CODE=$(echo "$RESPONSE" | jq -r '.code')
    
    if [ "$CODE" = "200" ]; then
        echo -e "${GREEN}Directory created successfully!${NC}"
    else
        echo -e "${RED}Failed to create directory${NC}"
        echo "$RESPONSE" | jq '.'
    fi
}

# Upload file
upload_file() {
    local local_file="$1"
    local remote_path="$2"
    
    if [ -z "$local_file" ] || [ -z "$remote_path" ]; then
        echo -e "${RED}Error: Both local file and remote path are required${NC}"
        echo "Usage: $0 upload <local_file> <remote_path>"
        exit 1
    fi
    
    if [ ! -f "$local_file" ]; then
        echo -e "${RED}Error: Local file not found: $local_file${NC}"
        exit 1
    fi
    
    TOKEN=$(login)
    
    FILE_PATH_B64=$(echo -n "$remote_path" | base64 -w 0)
    
    echo -e "${YELLOW}Uploading $local_file to $remote_path...${NC}"
    
    RESPONSE=$(curl -s -X PUT "${SERVER_URL}/api/fs/put" \
        -H "Authorization: $TOKEN" \
        -H "File-Path: $FILE_PATH_B64" \
        -H "Content-Type: application/octet-stream" \
        --data-binary "@${local_file}")
    
    CODE=$(echo "$RESPONSE" | jq -r '.code')
    
    if [ "$CODE" = "200" ]; then
        echo -e "${GREEN}File uploaded successfully!${NC}"
    else
        echo -e "${RED}Upload failed${NC}"
        echo "$RESPONSE" | jq '.'
    fi
}

# Delete file/directory
delete_remote() {
    local path="$1"
    local dir="$2"
    
    if [ -z "$path" ] || [ -z "$dir" ]; then
        echo -e "${RED}Error: Both path and parent directory are required${NC}"
        echo "Usage: $0 delete <file_or_dir_name> <parent_directory>"
        exit 1
    fi
    
    TOKEN=$(login)
    
    echo -e "${YELLOW}Deleting: $path in $dir${NC}"
    
    RESPONSE=$(curl -s -X POST "${SERVER_URL}/api/fs/remove" \
        -H "Authorization: $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"names\":[\"${path}\"],\"dir\":\"${dir}\"}")
    
    CODE=$(echo "$RESPONSE" | jq -r '.code')
    
    if [ "$CODE" = "200" ]; then
        echo -e "${GREEN}Deleted successfully!${NC}"
    else
        echo -e "${RED}Delete failed${NC}"
        echo "$RESPONSE" | jq '.'
    fi
}

# List storages
list_storages() {
    TOKEN=$(login)
    
    echo -e "${YELLOW}Listing storages...${NC}"
    
    curl -s -X GET "${SERVER_URL}/api/admin/storage/list" \
        -H "Authorization: $TOKEN" \
        | jq '.data.content[] | {id, mount_path, driver, disabled}'
}

# Show usage
usage() {
    echo "OpenList Helper Script"
    echo ""
    echo "Usage: $0 <command> [arguments]"
    echo ""
    echo "Commands:"
    echo "  login                          - Test login and get token"
    echo "  list [path] [page] [per_page]  - List directory contents"
    echo "  info <path>                    - Get file/directory info"
    echo "  search <keywords> [parent]     - Search files"
    echo "  mkdir <path>                   - Create directory"
    echo "  upload <local> <remote>        - Upload file"
    echo "  delete <name> <parent_dir>     - Delete file/directory"
    echo "  storages                       - List configured storages"
    echo ""
    echo "Environment variables:"
    echo "  OPENLIST_CONFIG - Path to config file (default: openlist-config.json)"
    echo ""
    echo "Examples:"
    echo "  $0 list /"
    echo "  $0 search 'document' /"
    echo "  $0 mkdir /test-folder"
    echo "  $0 upload ./file.txt /test-folder/file.txt"
    echo "  $0 delete file.txt /test-folder"
}

# Main
COMMAND="${1:-}"

case "$COMMAND" in
    login)
        login > /dev/null
        ;;
    list)
        list_dir "${2:-/}" "${3:-1}" "${4:-30}"
        ;;
    info)
        get_info "$2"
        ;;
    search)
        search "$2" "${3:-/}"
        ;;
    mkdir)
        mkdir_remote "$2"
        ;;
    upload)
        upload_file "$2" "$3"
        ;;
    delete)
        delete_remote "$2" "$3"
        ;;
    storages)
        list_storages
        ;;
    *)
        usage
        ;;
esac
