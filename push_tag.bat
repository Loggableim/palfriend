@echo off
REM Script to push the v1.0.0 tag to GitHub
REM
REM This script should be run by a repository maintainer with write access.
REM It pushes the v1.0.0 tag that was created to enable GitHub release creation.

echo ==========================================
echo Pushing v1.0.0 tag to GitHub
echo ==========================================
echo.

REM Check if tag exists
git tag -l | findstr /X "v1.0.0" > nul
if errorlevel 1 (
    echo Error: Tag v1.0.0 does not exist locally.
    echo Please run: git tag -a v1.0.0 -m "Release v1.0.0"
    exit /b 1
)

echo Tag v1.0.0 exists locally
echo.

REM Show tag details
echo Tag details:
git show v1.0.0 --no-patch
echo.

REM Push the tag
echo Pushing tag to origin...
git push origin v1.0.0
if errorlevel 1 (
    echo.
    echo X Failed to push tag to GitHub
    echo.
    echo This may be due to:
    echo - No write permissions to the repository
    echo - Authentication issues
    echo - Network connectivity issues
    echo.
    echo Please check your GitHub credentials and try again.
    exit /b 1
)

echo.
echo Successfully pushed v1.0.0 tag to GitHub
echo.
echo Next steps:
echo 1. Go to https://github.com/Loggableim/palfriend/releases
echo 2. Click 'Draft a new release'
echo 3. Select tag 'v1.0.0'
echo 4. Use content from RELEASE_NOTES_v1.0.0.md
echo 5. (Optional) Attach Windows executables
echo 6. Publish the release
echo.
echo See CREATE_RELEASE_GUIDE.md for detailed instructions.
echo.

pause
