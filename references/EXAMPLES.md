# OpenList API Examples

Practical examples of using the OpenList API via the `OpenListClient` Python class.

## Example 1: Complete File Management Workflow

```python
from scripts.openlist import OpenListClient

client = OpenListClient(config_path='openlist-config.json')

# 1. Login
client.login()

# 2. List root directory
result = client.list_directory('/', page=1, per_page=10)

# 3. Create a test directory
client.mkdir('/test-openlist')

# 4. Upload a test file
# First create a local file to upload
with open('/tmp/test-file.txt', 'w') as f:
    f.write('Hello from OpenList!')

client.upload_file('/tmp/test-file.txt', '/test-openlist/hello.txt')

# 5. Verify the upload
client.list_directory('/test-openlist', page=1, per_page=10)

# 6. Get file info
client.get_info('/test-openlist/hello.txt')

# 7. Search for the file
client.search('hello', '/test-openlist')

# 8. Clean up
client.delete('hello.txt', '/test-openlist')
client.delete('test-openlist', '/')
```

## Example 2: Backup Files from Server

```python
import os
import requests
from scripts.openlist import OpenListClient

client = OpenListClient(config_path='openlist-config.json')
client.login()

remote_dir = '/documents'
local_dir = './backup'
os.makedirs(local_dir, exist_ok=True)

# List remote files
result = client.list_directory(remote_dir, page=1, per_page=100)
content = result.get('data', {}).get('content', [])

for item in content:
    if not item.get('is_dir'):
        name = item['name']
        print(f'Downloading: {name}')

        # Get download sign
        info = client.get_info(f'{remote_dir}/{name}')
        sign = info.get('data', {}).get('sign', '')

        # Download via signed URL
        url = f'{client.server_url}/d{remote_dir}/{name}?sign={sign}'
        resp = requests.get(url, timeout=120)
        with open(os.path.join(local_dir, name), 'wb') as f:
            f.write(resp.content)

print(f'Backup complete! Files saved to: {local_dir}')
```

## Example 3: Upload Directory to Server

```python
import os
from scripts.openlist import OpenListClient

client = OpenListClient(config_path='openlist-config.json')
client.login()

local_dir = './my-files'
remote_dir = '/uploads'

# Create remote directory
client.mkdir(remote_dir)

# Upload each file
for filename in os.listdir(local_dir):
    filepath = os.path.join(local_dir, filename)
    if os.path.isfile(filepath):
        print(f'Uploading: {filename}')
        client.upload_file(filepath, f'{remote_dir}/{filename}')

print('Upload complete!')
```

## Example 4: Sync Files Between Two OpenList Servers

```python
import os
import requests
from scripts.openlist import OpenListClient

source = OpenListClient.__new__(OpenListClient)
source.server_url = 'https://source.example.com'
source.username = 'admin'
source.password = 'password1'
source.token = None
source.config = {'server_url': source.server_url, 'username': source.username, 'password': source.password}
source.login()

dest = OpenListClient.__new__(OpenListClient)
dest.server_url = 'https://dest.example.com'
dest.username = 'admin'
dest.password = 'password2'
dest.token = None
dest.config = {'server_url': dest.server_url, 'username': dest.username, 'password': dest.password}
dest.login()

source_path = '/documents'
dest_path = '/backup'

# Create destination directory
dest.mkdir(dest_path)

# List source files
result = source.list_directory(source_path, page=1, per_page=100)
content = result.get('data', {}).get('content', [])

for item in content:
    if not item.get('is_dir'):
        name = item['name']
        print(f'Syncing: {name}')

        # Get download sign from source
        info = source.get_info(f'{source_path}/{name}')
        sign = info.get('data', {}).get('sign', '')

        # Download from source to temp file
        url = f'{source.server_url}/d{source_path}/{name}?sign={sign}'
        resp = requests.get(url, timeout=120)
        tmp = f'/tmp/sync_{name}'
        with open(tmp, 'wb') as f:
            f.write(resp.content)

        # Upload to destination
        dest.upload_file(tmp, f'{dest_path}/{name}')
        os.remove(tmp)

print('Sync complete!')
```

## Example 5: Monitor Directory Changes

```python
import time
import json
from scripts.openlist import OpenListClient

client = OpenListClient(config_path='openlist-config.json')
client.login()

watch_dir = '/'
previous_state = {}

# Get initial state
result = client.list_directory(watch_dir, page=1, per_page=100)
for item in result.get('data', {}).get('content', []):
    previous_state[item['name']] = {
        'size': item.get('size'),
        'modified': item.get('modified')
    }

print(f'Monitoring {watch_dir} for changes...')

while True:
    time.sleep(30)
    client.login()  # Refresh token

    result = client.list_directory(watch_dir, page=1, per_page=100)
    current_state = {}
    for item in result.get('data', {}).get('content', []):
        current_state[item['name']] = {
            'size': item.get('size'),
            'modified': item.get('modified')
        }

    # Detect added files
    for name in current_state:
        if name not in previous_state:
            print(f'[ADDED] {name}')

    # Detect removed files
    for name in previous_state:
        if name not in current_state:
            print(f'[REMOVED] {name}')

    # Detect modified files
    for name in current_state:
        if name in previous_state and current_state[name] != previous_state[name]:
            print(f'[MODIFIED] {name}')

    previous_state = current_state
```

## Example 6: Generate Storage Report

```python
import json
from scripts.openlist import OpenListClient

client = OpenListClient(config_path='openlist-config.json')
client.login()

print('=== OpenList Storage Report ===')

# List storages (requires admin)
storages_result = client.list_storages()
storages = storages_result.get('data', {}).get('content', [])

for storage in storages:
    mount = storage.get('mount_path')
    driver = storage.get('driver')
    disabled = storage.get('disabled')

    print(f'\nStorage: {mount}')
    print(f'  Driver: {driver}')
    print(f'  Status: {"Disabled" if disabled else "Enabled"}')

    # Count files in this storage
    listing = client.list_directory(mount, page=1, per_page=1000)
    content = listing.get('data', {}).get('content', [])

    files = [c for c in content if not c.get('is_dir')]
    dirs = [c for c in content if c.get('is_dir')]
    total_size = sum(f.get('size', 0) for f in files)

    print(f'  Total items: {len(content)}')
    print(f'  Files: {len(files)}')
    print(f'  Directories: {len(dirs)}')
    print(f'  Total size: {total_size} bytes')

print('\n=== End of Report ===')
```

## Example 7: Offline Download with Aria2

```python
import time
from scripts.openlist import OpenListClient

client = OpenListClient(config_path='openlist-config.json')
client.login()

# List available tools
print('=== Available Offline Download Tools ===')
client.get_offline_tools()

# Add a download task
print('\n=== Adding Offline Download Task ===')
result = client.add_offline_download(
    url='http://example.com/file.zip',
    path='/downloads',
    tool='aria2',
    delete_policy='delete_on_upload_succeed'
)

tasks = result.get('data', {}).get('tasks', [])
if tasks:
    task_id = tasks[0].get('id')
    print(f'Task ID: {task_id}')

    # Monitor task progress
    print('\n=== Monitoring Task Progress ===')
    while True:
        info = client.get_offline_task(task_id)
        state = info.get('data', {}).get('state', '')
        progress = info.get('data', {}).get('progress', 0)
        status = info.get('data', {}).get('status', '')

        print(f'State: {state} | Progress: {progress}% | Status: {status}')

        if state in ('succeeded', 'failed', 'canceled'):
            print(f'\nTask finished with state: {state}')
            break

        time.sleep(5)
```

## Example 8: Batch Offline Download

```python
from scripts.openlist import OpenListClient

client = OpenListClient(config_path='openlist-config.json')
client.login()

urls = [
    'http://example.com/file1.zip',
    'http://example.com/file2.tar.gz',
    'magnet:?xt=urn:btih:...',
]
target_path = '/batch-downloads'
tool = 'aria2'

# Create target directory
client.mkdir(target_path)

# Add each download task
print(f'=== Adding {len(urls)} Download Tasks ===')
for url in urls:
    print(f'Adding: {url}')
    client.add_offline_download(url=url, path=target_path, tool=tool)

# List all tasks
print('\n=== All Offline Download Tasks ===')
client.list_offline_tasks(page=1, per_page=50)
```

## Tips

1. **Config file**: All examples assume `openlist-config.json` exists in the working directory
2. **Token refresh**: For long-running scripts, call `client.login()` periodically to refresh the token
3. **Error handling**: The `OpenListClient` exits on fatal errors; wrap calls in try/except for custom handling
4. **Test on demo**: Test against the demo server first: `https://demo.oplist.org` (guest/guest)
5. **Pagination**: For large directories, iterate pages with `page` parameter
