# Occassionally files are already tracked by Git, so adding them to .gitignore 
# alone will not stop Git from reporting them as modified.

# Git shows modified files that are already tracked, even if they are listed in .gitignore.

# Check if a file is tracked
#     Run:
#         git ls-files
    
#     the file is tracked.
#     If it returns nothing, Git is not tracking it.

!/bin/bash

set -e

echo "Cleaning project..."

find . -type d -name "__init__.*" | while read -r dir; do
    git rm -r --cached "$dir" 2>/dev/null || true
    rm -rf "$dir"
done

find . -type d -name "__pycache__" | while read -r dir; do
    git rm -r --cached "$dir" 2>/dev/null || true
    rm -rf "$dir"
done

find . -type f -name "*.pyc" | while read -r file; do
    git rm --cached "$file" 2>/dev/null || true
    rm -f "$file"
done

find . -type f -name ".DS_Store" | while read -r file; do
    git rm --cached "$file" 2>/dev/null || true
    rm -f "$file"
done

echo "Cleanup complete."
git status