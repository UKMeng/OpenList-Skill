#!/usr/bin/env python3
"""
OpenList API Helper Script
Python-based CLI tool for interacting with OpenList servers
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import requests
except ImportError:
    print("Error: requests library is required. Install it with:")
    print("  pip install requests")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

    @staticmethod
    def red(text: str) -> str:
        return f"{Colors.RED}{text}{Colors.NC}"

    @staticmethod
    def green(text: str) -> str:
        return f"{Colors.GREEN}{text}{Colors.NC}"

    @staticmethod
    def yellow(text: str) -> str:
        return f"{Colors.YELLOW}{text}{Colors.NC}"

    @staticmethod
    def blue(text: str) -> str:
        return f"{Colors.BLUE}{text}{Colors.NC}"


class OpenListClient:
    """OpenList API client"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the OpenList client

        Args:
            config_path: Path to config file (default: openlist-config.json)
        """
        self.config_path = config_path or os.environ.get(
            'OPENLIST_CONFIG', 'openlist-config.json'
        )
        self.config = self._load_config()
        self.server_url = self.config['server_url'].rstrip('/')
        self.username = self.config['username']
        self.password = self.config['password']
        self.token: Optional[str] = None

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_file = Path(self.config_path)

        if not config_file.exists():
            print(Colors.red(f"Error: Config file not found at {self.config_path}"))
            print("Please create it from the template:")
            print("  cp assets/openlist-config.template.json openlist-config.json")
            print("Then edit it with your server details.")
            sys.exit(1)

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            print(Colors.red(f"Error: Invalid JSON in config file: {e}"))
            sys.exit(1)

        # Validate required fields
        required_fields = ['server_url', 'username', 'password']
        for field in required_fields:
            if field not in config or not config[field]:
                print(Colors.red(f"Error: Missing required field '{field}' in config"))
                sys.exit(1)

        return config

    def login(self) -> str:
        """
        Authenticate with the server and get a JWT token

        Returns:
            JWT authentication token
        """
        print(Colors.yellow(f"Logging in to {self.server_url}..."), file=sys.stderr)

        try:
            response = requests.post(
                f"{self.server_url}/api/auth/login",
                json={
                    "username": self.username,
                    "password": self.password
                },
                timeout=30
            )
            data = response.json()

            if data.get('code') != 200:
                print(Colors.red("Login failed!"), file=sys.stderr)
                print(json.dumps(data, indent=2), file=sys.stderr)
                sys.exit(1)

            token = data.get('data', {}).get('token')
            if not token:
                print(Colors.red("Failed to get token from response"), file=sys.stderr)
                sys.exit(1)

            print(Colors.green("Login successful!"), file=sys.stderr)
            self.token = token
            return token

        except requests.RequestException as e:
            print(Colors.red(f"Login request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication"""
        if not self.token:
            self.login()
        return {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }

    def list_directory(self, path: str = "/", page: int = 1, per_page: int = 30) -> Dict:
        """List directory contents"""
        print(Colors.yellow(f"Listing: {path}"))

        try:
            response = requests.post(
                f"{self.server_url}/api/fs/list",
                headers=self._get_headers(),
                json={
                    "path": path,
                    "page": page,
                    "per_page": per_page
                },
                timeout=30
            )
            data = response.json()

            if data.get('code') == 200:
                content = data.get('data', {}).get('content', [])
                for item in content:
                    print(json.dumps({
                        'name': item.get('name'),
                        'size': item.get('size'),
                        'is_dir': item.get('is_dir'),
                        'modified': item.get('modified')
                    }, indent=2))
            else:
                print(Colors.red("List failed"))
                print(json.dumps(data, indent=2))

            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def get_info(self, path: str) -> Dict:
        """Get file/directory information"""
        try:
            response = requests.post(
                f"{self.server_url}/api/fs/get",
                headers=self._get_headers(),
                json={"path": path},
                timeout=30
            )
            data = response.json()
            print(json.dumps(data, indent=2))
            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def search(self, keywords: str, parent: str = "/") -> Dict:
        """Search for files"""
        print(Colors.yellow(f"Searching for: {keywords} in {parent}"))

        try:
            response = requests.post(
                f"{self.server_url}/api/fs/search",
                headers=self._get_headers(),
                json={
                    "parent": parent,
                    "keywords": keywords,
                    "scope": 0,
                    "page": 1,
                    "per_page": 30
                },
                timeout=30
            )
            data = response.json()

            if data.get('code') == 200:
                content = data.get('data', {}).get('content', [])
                for item in content:
                    print(json.dumps({
                        'name': item.get('name'),
                        'size': item.get('size'),
                        'parent': item.get('parent')
                    }, indent=2))
            else:
                print(Colors.red("Search failed"))
                print(json.dumps(data, indent=2))

            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def mkdir(self, path: str) -> Dict:
        """Create a directory"""
        print(Colors.yellow(f"Creating directory: {path}"))

        try:
            response = requests.post(
                f"{self.server_url}/api/fs/mkdir",
                headers=self._get_headers(),
                json={"path": path},
                timeout=30
            )
            data = response.json()

            if data.get('code') == 200:
                print(Colors.green("Directory created successfully!"))
            else:
                print(Colors.red("Failed to create directory"))
                print(json.dumps(data, indent=2))

            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def upload_file(self, local_file: str, remote_path: str) -> Dict:
        """Upload a file"""
        local_path = Path(local_file)

        if not local_path.exists():
            print(Colors.red(f"Error: Local file not found: {local_file}"))
            sys.exit(1)

        if not local_path.is_file():
            print(Colors.red(f"Error: Path is not a file: {local_file}"))
            sys.exit(1)

        print(Colors.yellow(f"Uploading {local_file} to {remote_path}..."))

        # Encode remote path in base64
        remote_path_b64 = base64.b64encode(remote_path.encode('utf-8')).decode('ascii')

        try:
            with open(local_path, 'rb') as f:
                headers = {
                    "Authorization": self.token or self.login(),
                    "File-Path": remote_path_b64,
                    "Content-Type": "application/octet-stream"
                }

                response = requests.put(
                    f"{self.server_url}/api/fs/put",
                    headers=headers,
                    data=f,
                    timeout=300  # 5 minutes for large files
                )
                data = response.json()

                if data.get('code') == 200:
                    print(Colors.green("File uploaded successfully!"))
                else:
                    print(Colors.red("Upload failed"))
                    print(json.dumps(data, indent=2))

                return data

        except requests.RequestException as e:
            print(Colors.red(f"Upload failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def delete(self, name: str, parent_dir: str) -> Dict:
        """Delete a file or directory"""
        print(Colors.yellow(f"Deleting: {name} in {parent_dir}"))

        try:
            response = requests.post(
                f"{self.server_url}/api/fs/remove",
                headers=self._get_headers(),
                json={
                    "names": [name],
                    "dir": parent_dir
                },
                timeout=30
            )
            data = response.json()

            if data.get('code') == 200:
                print(Colors.green("Deleted successfully!"))
            else:
                print(Colors.red("Delete failed"))
                print(json.dumps(data, indent=2))

            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def rename(self, path: str, new_name: str) -> Dict:
        """Rename a file or directory"""
        print(Colors.yellow(f"Renaming: {path} -> {new_name}"))

        try:
            response = requests.post(
                f"{self.server_url}/api/fs/rename",
                headers=self._get_headers(),
                json={
                    "path": path,
                    "name": new_name
                },
                timeout=30
            )
            data = response.json()

            if data.get('code') == 200:
                print(Colors.green("Renamed successfully!"))
            else:
                print(Colors.red("Rename failed"))
                print(json.dumps(data, indent=2))

            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def move(self, src_dir: str, dst_dir: str, names: list) -> Dict:
        """Move files or directories"""
        print(Colors.yellow(f"Moving {names} from {src_dir} to {dst_dir}"))

        try:
            response = requests.post(
                f"{self.server_url}/api/fs/move",
                headers=self._get_headers(),
                json={
                    "src_dir": src_dir,
                    "dst_dir": dst_dir,
                    "names": names
                },
                timeout=30
            )
            data = response.json()

            if data.get('code') == 200:
                print(Colors.green("Moved successfully!"))
            else:
                print(Colors.red("Move failed"))
                print(json.dumps(data, indent=2))

            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def copy(self, src_dir: str, dst_dir: str, names: list) -> Dict:
        """Copy files or directories"""
        print(Colors.yellow(f"Copying {names} from {src_dir} to {dst_dir}"))

        try:
            response = requests.post(
                f"{self.server_url}/api/fs/copy",
                headers=self._get_headers(),
                json={
                    "src_dir": src_dir,
                    "dst_dir": dst_dir,
                    "names": names
                },
                timeout=30
            )
            data = response.json()

            if data.get('code') == 200:
                print(Colors.green("Copied successfully!"))
            else:
                print(Colors.red("Copy failed"))
                print(json.dumps(data, indent=2))

            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def list_storages(self) -> Dict:
        """List configured storage providers"""
        print(Colors.yellow("Listing storages..."))

        try:
            response = requests.get(
                f"{self.server_url}/api/admin/storage/list",
                headers=self._get_headers(),
                timeout=30
            )
            data = response.json()

            if data.get('code') == 200:
                content = data.get('data', {}).get('content', [])
                for storage in content:
                    print(json.dumps({
                        'id': storage.get('id'),
                        'mount_path': storage.get('mount_path'),
                        'driver': storage.get('driver'),
                        'disabled': storage.get('disabled')
                    }, indent=2))
            else:
                print(Colors.red("Failed to list storages"))
                print(json.dumps(data, indent=2))

            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def get_offline_tools(self) -> Dict:
        """Get available offline download tools"""
        print(Colors.yellow("Getting available offline download tools..."))

        try:
            response = requests.get(
                f"{self.server_url}/api/public/offline_download_tools",
                timeout=30
            )
            data = response.json()
            print(json.dumps(data, indent=2))
            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def add_offline_download(
        self,
        url: str,
        path: str,
        tool: str = "aria2",
        delete_policy: str = "delete_on_upload_succeed"
    ) -> Dict:
        """Add an offline download task"""
        print(Colors.yellow("Adding offline download task..."))
        print(f"URL: {url}")
        print(f"Path: {path}")
        print(f"Tool: {tool}")
        print(f"Delete policy: {delete_policy}")

        try:
            response = requests.post(
                f"{self.server_url}/api/fs/add_offline_download",
                headers=self._get_headers(),
                json={
                    "urls": [url],
                    "path": path,
                    "tool": tool,
                    "delete_policy": delete_policy
                },
                timeout=30
            )
            data = response.json()

            if data.get('code') == 200:
                print(Colors.green("Offline download task added successfully!"))
                tasks = data.get('data', {}).get('tasks', [])
                print(json.dumps(tasks, indent=2))
            else:
                print(Colors.red("Failed to add offline download task"))
                print(json.dumps(data, indent=2))

            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def list_offline_tasks(self, page: int = 1, per_page: int = 10) -> Dict:
        """List offline download tasks (both undone and done)"""
        print(Colors.yellow("Listing offline download tasks..."))

        all_tasks = []
        try:
            # Fetch undone (pending/running/errored) tasks
            resp_undone = requests.get(
                f"{self.server_url}/api/task/offline_download/undone",
                headers=self._get_headers(),
                timeout=30
            )
            data_undone = resp_undone.json()
            if data_undone.get('code') == 200:
                all_tasks.extend(data_undone.get('data', []) or [])

            # Fetch done (succeeded/failed/canceled) tasks
            resp_done = requests.get(
                f"{self.server_url}/api/task/offline_download/done",
                headers=self._get_headers(),
                timeout=30
            )
            data_done = resp_done.json()
            if data_done.get('code') == 200:
                all_tasks.extend(data_done.get('data', []) or [])

            if all_tasks:
                for task in all_tasks:
                    print(json.dumps({
                        'id': task.get('id'),
                        'name': task.get('name'),
                        'state': task.get('state'),
                        'status': task.get('status'),
                        'progress': task.get('progress'),
                        'error': task.get('error')
                    }, indent=2))
            else:
                print(Colors.yellow("No offline download tasks found."))

            return {"code": 200, "data": all_tasks}

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def get_offline_task(self, task_id: str) -> Dict:
        """Get offline download task information"""
        try:
            response = requests.post(
                f"{self.server_url}/api/task/offline_download/info",
                headers=self._get_headers(),
                params={"tid": task_id},
                timeout=30
            )
            data = response.json()
            print(json.dumps(data, indent=2))
            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def cancel_offline_task(self, task_id: str) -> Dict:
        """Cancel an offline download task"""
        print(Colors.yellow(f"Canceling task: {task_id}"))

        try:
            response = requests.post(
                f"{self.server_url}/api/task/offline_download/cancel",
                headers=self._get_headers(),
                params={"tid": task_id},
                timeout=30
            )
            data = response.json()

            if data.get('code') == 200:
                print(Colors.green("Task canceled successfully!"))
            else:
                print(Colors.red("Failed to cancel task"))
                print(json.dumps(data, indent=2))

            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)

    def delete_offline_task(self, task_id: str) -> Dict:
        """Delete an offline download task"""
        print(Colors.yellow(f"Deleting task: {task_id}"))

        try:
            response = requests.post(
                f"{self.server_url}/api/task/offline_download/delete",
                headers=self._get_headers(),
                params={"tid": task_id},
                timeout=30
            )
            data = response.json()

            if data.get('code') == 200:
                print(Colors.green("Task deleted successfully!"))
            else:
                print(Colors.red("Failed to delete task"))
                print(json.dumps(data, indent=2))

            return data

        except requests.RequestException as e:
            print(Colors.red(f"Request failed: {e}"), file=sys.stderr)
            sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="OpenList API Helper - Python CLI tool for OpenList operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list /
  %(prog)s search document /
  %(prog)s mkdir /test-folder
  %(prog)s upload ./file.txt /test-folder/file.txt
  %(prog)s delete file.txt /test-folder
  %(prog)s offline-download http://example.com/file.zip /downloads aria2

Environment variables:
  OPENLIST_CONFIG - Path to config file (default: openlist-config.json)
"""
    )

    parser.add_argument(
        '--config',
        help='Path to config file (default: openlist-config.json)',
        default=None
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Login command
    subparsers.add_parser('login', help='Test login and get token')

    # List command
    list_parser = subparsers.add_parser('list', help='List directory contents')
    list_parser.add_argument('path', nargs='?', default='/', help='Directory path')
    list_parser.add_argument('--page', type=int, default=1, help='Page number')
    list_parser.add_argument('--per-page', type=int, default=30, help='Items per page')

    # Info command
    info_parser = subparsers.add_parser('info', help='Get file/directory info')
    info_parser.add_argument('path', help='File or directory path')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for files')
    search_parser.add_argument('keywords', help='Search keywords')
    search_parser.add_argument('parent', nargs='?', default='/', help='Parent directory')

    # Mkdir command
    mkdir_parser = subparsers.add_parser('mkdir', help='Create directory')
    mkdir_parser.add_argument('path', help='Directory path to create')

    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload file')
    upload_parser.add_argument('local_file', help='Local file path')
    upload_parser.add_argument('remote_path', help='Remote file path')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete file or directory')
    delete_parser.add_argument('name', help='File or directory name')
    delete_parser.add_argument('parent_dir', help='Parent directory path')

    # Rename command
    rename_parser = subparsers.add_parser('rename', help='Rename file or directory')
    rename_parser.add_argument('path', help='Full path of the file/directory to rename')
    rename_parser.add_argument('new_name', help='New name')

    # Move command
    move_parser = subparsers.add_parser('move', help='Move files or directories')
    move_parser.add_argument('src_dir', help='Source directory path')
    move_parser.add_argument('dst_dir', help='Destination directory path')
    move_parser.add_argument('names', nargs='+', help='Names of files/directories to move')

    # Copy command
    copy_parser = subparsers.add_parser('copy', help='Copy files or directories')
    copy_parser.add_argument('src_dir', help='Source directory path')
    copy_parser.add_argument('dst_dir', help='Destination directory path')
    copy_parser.add_argument('names', nargs='+', help='Names of files/directories to copy')

    # Storages command
    subparsers.add_parser('storages', help='List configured storages')

    # Offline download commands
    subparsers.add_parser('offline-tools', help='List available download tools')

    offline_download_parser = subparsers.add_parser(
        'offline-download', help='Add offline download task'
    )
    offline_download_parser.add_argument('url', help='Download URL')
    offline_download_parser.add_argument('path', help='Destination path')
    offline_download_parser.add_argument(
        'tool', nargs='?', default='aria2', help='Download tool (default: aria2)'
    )
    offline_download_parser.add_argument(
        'delete_policy',
        nargs='?',
        default='delete_on_upload_succeed',
        help='Delete policy (default: delete_on_upload_succeed)'
    )

    offline_list_parser = subparsers.add_parser(
        'offline-list', help='List offline download tasks'
    )
    offline_list_parser.add_argument('--page', type=int, default=1, help='Page number')
    offline_list_parser.add_argument(
        '--per-page', type=int, default=10, help='Items per page'
    )

    offline_info_parser = subparsers.add_parser(
        'offline-info', help='Get task information'
    )
    offline_info_parser.add_argument('task_id', help='Task ID')

    offline_cancel_parser = subparsers.add_parser(
        'offline-cancel', help='Cancel a task'
    )
    offline_cancel_parser.add_argument('task_id', help='Task ID')

    offline_delete_parser = subparsers.add_parser(
        'offline-delete', help='Delete a task'
    )
    offline_delete_parser.add_argument('task_id', help='Task ID')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Initialize client
    client = OpenListClient(config_path=args.config)

    # Execute command
    try:
        if args.command == 'login':
            client.login()
        elif args.command == 'list':
            client.list_directory(args.path, args.page, args.per_page)
        elif args.command == 'info':
            client.get_info(args.path)
        elif args.command == 'search':
            client.search(args.keywords, args.parent)
        elif args.command == 'mkdir':
            client.mkdir(args.path)
        elif args.command == 'upload':
            client.upload_file(args.local_file, args.remote_path)
        elif args.command == 'delete':
            client.delete(args.name, args.parent_dir)
        elif args.command == 'rename':
            client.rename(args.path, args.new_name)
        elif args.command == 'move':
            client.move(args.src_dir, args.dst_dir, args.names)
        elif args.command == 'copy':
            client.copy(args.src_dir, args.dst_dir, args.names)
        elif args.command == 'storages':
            client.list_storages()
        elif args.command == 'offline-tools':
            client.get_offline_tools()
        elif args.command == 'offline-download':
            client.add_offline_download(
                args.url, args.path, args.tool, args.delete_policy
            )
        elif args.command == 'offline-list':
            client.list_offline_tasks(args.page, args.per_page)
        elif args.command == 'offline-info':
            client.get_offline_task(args.task_id)
        elif args.command == 'offline-cancel':
            client.cancel_offline_task(args.task_id)
        elif args.command == 'offline-delete':
            client.delete_offline_task(args.task_id)
        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)


if __name__ == '__main__':
    main()
