# Guide: Creating the v1.0.0 GitHub Release

This guide explains how to create the v1.0.0 release on GitHub to make it available for users as mentioned in the README.

## Prerequisites

- GitHub account with write access to the repository
- (Optional) Built executables for Windows distribution

## Steps to Create the Release

### 1. Create and Push the Git Tag

First, ensure you're on the correct commit (the latest commit on the main branch):

```bash
cd /home/runner/work/palfriend/palfriend
git checkout main
git pull origin main
```

Create an annotated tag for v1.0.0:

```bash
git tag -a v1.0.0 -m "Release v1.0.0 - Production Ready with Modern Web Interface"
```

Push the tag to GitHub:

```bash
git push origin v1.0.0
```

### 2. Create the GitHub Release

1. **Navigate to the Releases page:**
   - Go to https://github.com/Loggableim/palfriend/releases
   - Click "Draft a new release"

2. **Configure the release:**
   - **Tag:** Select `v1.0.0` from the dropdown (it should appear after pushing the tag)
   - **Release title:** `v1.0.0 - Production Ready`
   - **Description:** Copy the contents from `RELEASE_NOTES_v1.0.0.md`

3. **Add release assets (optional but recommended):**
   
   If you have built the Windows executables:
   - `palfriendlauncher.exe` - The GUI installer (primary download)
   - `palfriend.zip` - Zip file containing the palfriend directory with palfriend.exe
   
   To build these executables, see [BUILD_LAUNCHER.md](BUILD_LAUNCHER.md).

4. **Publish:**
   - Check "Set as the latest release"
   - Click "Publish release"

### 3. Verify the Release

After publishing:

1. Check that the release appears at: https://github.com/Loggableim/palfriend/releases
2. Verify the README link works: The link on line 58 of README.md points to the releases page
3. Test downloading the assets (if included)

## Building the Windows Executables (Optional)

If you want to include pre-built Windows executables in the release:

### Requirements:
- Windows machine (or Windows VM)
- Python 3.12.x (NOT 3.13+)
- Node.js 16+

### Build Steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Loggableim/palfriend.git
   cd palfriend
   git checkout v1.0.0
   ```

2. **Run the build script:**
   ```cmd
   build_launcher.bat
   ```

3. **Find the executables:**
   - `dist/palfriendlauncher.exe` - The installer (this is what users download)
   - `dist/palfriend/` - Directory containing palfriend.exe and dependencies

4. **Create a distribution zip:**
   ```cmd
   cd dist
   # Zip the palfriend directory
   tar -a -c -f palfriend-v1.0.0-windows.zip palfriend
   ```

5. **Upload to GitHub Release:**
   - Upload `palfriendlauncher.exe` (main download)
   - Upload `palfriend-v1.0.0-windows.zip` (alternative download)

For detailed build instructions, see [BUILD_LAUNCHER.md](BUILD_LAUNCHER.md).

## Alternative: GitHub Actions Automated Build

The repository includes a GitHub Actions workflow that can build the executables automatically:

1. **Navigate to Actions:**
   - Go to https://github.com/Loggableim/palfriend/actions
   - Select "Build Launcher Executable" workflow

2. **Run the workflow:**
   - Click "Run workflow"
   - Select the `v1.0.0` tag or branch
   - Click "Run workflow"

3. **Download artifacts:**
   - Wait for the workflow to complete
   - Download the build artifacts
   - Extract and upload to the GitHub release

## What This Release Provides

This release makes PalFriend easily accessible to Windows users who:
- Don't have Python installed
- Don't want to deal with command-line installation
- Want a simple double-click installation experience

The release assets mentioned in README.md (line 58-59) will be available for download, fulfilling the documentation promise.

## Troubleshooting

### Tag Already Exists
If you get an error that the tag already exists:
```bash
# Delete local tag
git tag -d v1.0.0
# Delete remote tag (if it exists)
git push origin :refs/tags/v1.0.0
# Recreate and push
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### Build Failures
If the Windows build fails:
- Ensure Python version is 3.11.x or 3.12.x (NOT 3.13+)
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify the frontend is built: `cd frontend && npm run build`
- See [BUILD_LAUNCHER.md](BUILD_LAUNCHER.md) for detailed troubleshooting

### No Write Access
If you don't have permission to create releases:
- Contact the repository owner (Loggableim)
- They can create the release using this guide
- Or they can grant you the necessary permissions

## Summary

After completing these steps:
- ✅ The v1.0.0 tag exists in the repository
- ✅ A GitHub release is published at https://github.com/Loggableim/palfriend/releases
- ✅ Users can download the release as mentioned in README.md
- ✅ (Optional) Windows executables are available for download

The release addresses the issue where README.md references a releases page that was previously empty.
