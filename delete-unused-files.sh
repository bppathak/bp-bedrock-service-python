# Occassionally files are already tracked by Git, so adding them to .gitignore 
# alone will not stop Git from reporting them as modified.

# Git shows modified files that are already tracked, even if they are listed in .gitignore.

# Check if a file is tracked
#     Run:
#         git ls-files
    
#     the file is tracked.
#     If it returns nothing, Git is not tracking it.

# Removing the tracked files from Git's index
# git rm -r --cached backend_python/app/__pycache__
# git rm -r --cached backend_python/app/services/__pycache__
# git rm --cached k8s/.DS_Store

# For many cached files throughout the project, you can remove them all at once:
find . -name "__pycache__" -type d -exec git rm -r --cached {} +
find . -name "*.pyc" -exec git rm --cached {} +
find . -name ".DS_Store" -exec git rm --cached {} +

