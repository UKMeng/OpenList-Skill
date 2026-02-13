# OpenList Skill - Quick Install Guide

## 🎉 Skill Created Successfully!

The OpenList skill has been created at: `.openclaw/skills/openlist/`

## 📁 Files Created

- **SKILL.md** (8.2KB) - Main skill documentation with complete API reference
- **README.md** (3.8KB) - Overview and quick start guide  
- **EXAMPLES.md** (12KB) - Practical usage examples and workflows
- **openlist.sh** (7.5KB) - Helper script for common operations
- **test.sh** (4.5KB) - Test script to verify functionality
- **openlist-config.template.json** - Configuration template
- **.gitignore** - Protects sensitive config files

## 🚀 Quick Start

### Step 1: Setup Configuration

```bash
# Copy the template to workspace root
cp .openclaw/skills/openlist/openlist-config.template.json openlist-config.json

# Edit with your server details
nano openlist-config.json
```

Configuration format:
```json
{
  "server_url": "https://your-openlist-server.com",
  "username": "admin",
  "password": "your-password"
}
```

### Step 2: Test Connection

```bash
# Run the test script
.openclaw/skills/openlist/test.sh
```

This will:
- ✓ Test login
- ✓ List directories
- ✓ Search files
- ✓ Create/upload/delete (if permissions allow)
- ✓ List storages

### Step 3: Start Using

```bash
# List files
.openclaw/skills/openlist/openlist.sh list /

# Search files
.openclaw/skills/openlist/openlist.sh search "document" /

# Upload file
.openclaw/skills/openlist/openlist.sh upload ./local.txt /remote.txt

# Create directory
.openclaw/skills/openlist/openlist.sh mkdir /new-folder

# List storages
.openclaw/skills/openlist/openlist.sh storages
```

## 📖 Documentation

- **SKILL.md** - Complete API reference and authentication guide
- **README.md** - Feature overview and basic examples
- **EXAMPLES.md** - Advanced workflows (backup, sync, monitoring)

## 🔧 Helper Commands

```bash
# Show all available commands
.openclaw/skills/openlist/openlist.sh

# Get help
.openclaw/skills/openlist/openlist.sh --help
```

## 🌐 Test with Demo Server

If you don't have your own OpenList server yet, you can test with the official demo:

```json
{
  "server_url": "https://demo.oplist.org",
  "username": "guest",
  "password": "guest"
}
```

**Note**: Demo server may have limited permissions.

## 📚 Resources

- **API Documentation**: https://fox.oplist.org
- **Official Docs**: https://doc.oplist.org  
- **GitHub**: https://github.com/OpenListTeam/OpenList
- **Demo Site**: https://demo.oplist.org

## 🔐 Security Notes

1. ⚠️ Never commit `openlist-config.json` to git (it's in `.gitignore`)
2. ✓ JWT tokens are obtained per-session, not stored
3. ✓ Always use HTTPS for production servers
4. ✓ Use strong passwords for OpenList admin accounts

## 🎯 What You Can Do

With this skill, OpenClaw can now:

- ✅ Authenticate with OpenList servers
- ✅ List and browse directories
- ✅ Search for files across storages
- ✅ Upload and download files
- ✅ Create, rename, delete files/folders
- ✅ Copy and move files between locations
- ✅ Manage storage providers (admin)
- ✅ Query server settings and status

## 🐛 Troubleshooting

**Config not found?**
```bash
# Make sure it's in workspace root
ls -la openlist-config.json
```

**Login failed?**
- Check server URL is correct (include https://)
- Verify username and password
- Try the demo server to test connectivity

**Permission denied?**
- Some operations require admin permissions
- Check your user role in OpenList settings

## 🤝 Contributing

Found a bug or want to add features?
- OpenList GitHub: https://github.com/OpenListTeam/OpenList
- Report issues or submit PRs

## 📝 License

OpenList is licensed under AGPL-3.0. All operations using this skill comply with this license.

---

**You're all set!** 🎉

Run `.openclaw/skills/openlist/test.sh` to get started, or check out the examples in EXAMPLES.md for advanced usage.
