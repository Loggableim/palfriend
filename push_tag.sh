#!/bin/bash
# Script to push the v1.0.0 tag to GitHub
#
# This script should be run by a repository maintainer with write access.
# It pushes the v1.0.0 tag that was created to enable GitHub release creation.

set -e

echo "=========================================="
echo "Pushing v1.0.0 tag to GitHub"
echo "=========================================="
echo

# Check if tag exists
if ! git tag -l | grep -q "^v1.0.0$"; then
    echo "Error: Tag v1.0.0 does not exist locally."
    echo "Please run: git tag -a v1.0.0 -m 'Release v1.0.0'"
    exit 1
fi

echo "Tag v1.0.0 exists locally"
echo

# Show tag details
echo "Tag details:"
git show v1.0.0 --no-patch
echo

# Push the tag
echo "Pushing tag to origin..."
if git push origin v1.0.0; then
    echo
    echo "✓ Successfully pushed v1.0.0 tag to GitHub"
    echo
    echo "Next steps:"
    echo "1. Go to https://github.com/Loggableim/palfriend/releases"
    echo "2. Click 'Draft a new release'"
    echo "3. Select tag 'v1.0.0'"
    echo "4. Use content from RELEASE_NOTES_v1.0.0.md"
    echo "5. (Optional) Attach Windows executables"
    echo "6. Publish the release"
    echo
    echo "See CREATE_RELEASE_GUIDE.md for detailed instructions."
else
    echo
    echo "✗ Failed to push tag to GitHub"
    echo
    echo "This may be due to:"
    echo "- No write permissions to the repository"
    echo "- Authentication issues"
    echo "- Network connectivity issues"
    echo
    echo "Please check your GitHub credentials and try again."
    exit 1
fi
