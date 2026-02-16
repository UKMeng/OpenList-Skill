#!/usr/bin/env python3
"""
OpenList Skill Test Script
Tests basic functionality of the OpenList Python client
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional

# Add scripts directory to path to import openlist module
sys.path.insert(0, str(Path(__file__).parent))

try:
    from openlist import OpenListClient, Colors
except ImportError:
    print("Error: Could not import openlist module")
    print("Make sure openlist.py is in the same directory")
    sys.exit(1)


def print_header(text: str):
    """Print a section header"""
    print(f"\n{Colors.blue('=' * 50)}")
    print(Colors.blue(f"  {text}"))
    print(f"{Colors.blue('=' * 50)}\n")


def print_test(text: str):
    """Print test name"""
    print(Colors.yellow(f"Test: {text}"))


def print_success(text: str):
    """Print success message"""
    print(Colors.green(f"✓ {text}"))


def print_error(text: str):
    """Print error message"""
    print(Colors.red(f"✗ {text}"))


def print_warning(text: str):
    """Print warning message"""
    print(Colors.yellow(f"⚠ {text}"))


def check_config(config_path: str = "openlist-config.json") -> bool:
    """Check if config file exists and is valid"""
    config_file = Path(config_path)

    if not config_file.exists():
        print_warning("Config file not found. Creating from template...")
        template_path = Path(__file__).parent.parent / "assets" / "openlist-config.template.json"

        if template_path.exists():
            import shutil
            shutil.copy(template_path, config_file)
            print_warning(f"Please edit {config_path} with your server details")
            print_warning("Then run this test script again.")
        else:
            print_error("Template config file not found")

        return False

    # Check if config is filled
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        server_url = config.get('server_url', '')
        if 'your-' in server_url:
            print_warning("Config file contains default values.")
            print_warning(f"Please edit {config_path} with your actual server details.")
            return False

        return True

    except (json.JSONDecodeError, KeyError) as e:
        print_error(f"Invalid config file: {e}")
        return False


def run_tests(config_path: Optional[str] = None):
    """Run the test suite"""
    print_header("OpenList Skill Test")

    # Check config
    config_path = config_path or "openlist-config.json"
    if not check_config(config_path):
        return False

    # Initialize client
    try:
        client = OpenListClient(config_path=config_path)
        print(Colors.blue(f"Testing connection to: {client.server_url}\n"))
    except Exception as e:
        print_error(f"Failed to initialize client: {e}")
        return False

    # Test 1: Login
    print_test("Login")
    try:
        client.login()
        print_success("Login successful\n")
    except Exception as e:
        print_error(f"Login failed: {e}")
        print_error("Please check your credentials in openlist-config.json")
        return False

    # Test 2: List root directory
    print_test("List root directory")
    try:
        result = client.list_directory("/")
        if result.get('code') == 200:
            print_success("List successful\n")
        else:
            print_error("List failed\n")
    except Exception as e:
        print_error(f"List failed: {e}\n")

    # Test 3: Search functionality
    print_test("Search functionality")
    try:
        result = client.search("*", "/")
        if result.get('code') == 200:
            print_success("Search API works\n")
        else:
            print_warning("Search failed\n")
    except Exception as e:
        print_warning(f"Search failed: {e}\n")

    # Test 4: Create test directory
    print_test("Create directory")
    test_dir = f"/openlist-test-{int(time.time())}"

    try:
        result = client.mkdir(test_dir)
        if result.get('code') == 200:
            print_success(f"Directory created: {test_dir}\n")

            # Test 5: Upload test file
            print_test("Upload file")
            try:
                # Create temporary test file
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    delete=False,
                    suffix='.txt'
                ) as tmp_file:
                    tmp_file.write(f"OpenList Python test file - {time.ctime()}\n")
                    tmp_file_path = tmp_file.name

                remote_path = f"{test_dir}/test.txt"
                result = client.upload_file(tmp_file_path, remote_path)

                # Clean up temp file
                os.unlink(tmp_file_path)

                if result.get('code') == 200:
                    print_success("File uploaded\n")

                    # Test 6: Verify upload
                    print_test("Verify upload")
                    result = client.list_directory(test_dir)
                    if result.get('code') == 200:
                        content = result.get('data', {}).get('content', [])
                        file_found = any(
                            item.get('name') == 'test.txt' for item in content
                        )
                        if file_found:
                            print_success("File verified in directory\n")
                        else:
                            print_warning("File not found in listing\n")

                    # Test 7: Get file info
                    print_test("Get file info")
                    try:
                        result = client.get_info(remote_path)
                        if result.get('code') == 200:
                            print_success("File info retrieved\n")
                    except Exception as e:
                        print_warning(f"Failed to get file info: {e}\n")

                else:
                    print_error("File upload failed\n")

            except Exception as e:
                print_error(f"Upload test failed: {e}\n")

            # Cleanup
            print_test("Cleanup: Deleting test directory")
            try:
                result = client.delete(test_dir.split('/')[-1], "/")
                if result.get('code') == 200:
                    print_success("Test directory deleted\n")
                else:
                    print_warning(
                        "Failed to delete test directory "
                        "(manual cleanup may be needed)\n"
                    )
            except Exception as e:
                print_warning(f"Cleanup failed: {e}\n")

        else:
            print_warning(
                "Directory creation failed (may not have permissions)\n"
            )

    except Exception as e:
        print_warning(f"Directory creation test failed: {e}\n")

    # Test 8: List storages (admin endpoint)
    print_test("List storages (admin)")
    try:
        result = client.list_storages()
        if result.get('code') == 200:
            print_success("Storage list retrieved\n")
        else:
            print_warning("Could not list storages (may need admin permissions)\n")
    except Exception as e:
        print_warning(f"Storage list failed: {e}\n")

    # Test 9: Get offline download tools
    print_test("Get offline download tools")
    try:
        result = client.get_offline_tools()
        if result.get('code') == 200:
            print_success("Offline download tools retrieved\n")
        else:
            print_warning("Could not get offline download tools\n")
    except Exception as e:
        print_warning(f"Offline tools query failed: {e}\n")

    # Summary
    print_header("Test Summary")
    print(Colors.green("OpenList Python client is functional!\n"))
    print("Available commands:")
    print("  python scripts/openlist.py login")
    print("  python scripts/openlist.py list [path]")
    print("  python scripts/openlist.py search <keywords> [parent]")
    print("  python scripts/openlist.py mkdir <path>")
    print("  python scripts/openlist.py upload <local> <remote>")
    print("  python scripts/openlist.py delete <name> <parent_dir>")
    print("  python scripts/openlist.py storages")
    print("  python scripts/openlist.py offline-tools")
    print("  python scripts/openlist.py offline-download <url> <path>")
    print("  python scripts/openlist.py offline-list")
    print("\nFor more details, see: SKILL.md\n")

    return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test OpenList Python client functionality"
    )
    parser.add_argument(
        '--config',
        help='Path to config file (default: openlist-config.json)',
        default=None
    )

    args = parser.parse_args()

    try:
        success = run_tests(config_path=args.config)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
