import os
import sys
from dulwich import porcelain
from dulwich.repo import Repo

REPO_PATH = os.path.abspath(".")
REMOTE_URL = "git@github.com:fathimafarhana8714-rgb/kerala-trip.git"

print(f"Working Directory: {REPO_PATH}")

# 1. Initialize repository if .git doesn't exist
git_dir = os.path.join(REPO_PATH, ".git")
if not os.path.exists(git_dir):
    print("Initializing new Git repository...")
    repo = porcelain.init(REPO_PATH)
else:
    print("Opening existing Git repository...")
    repo = Repo(REPO_PATH)

# 2. Stage files
print("Staging project files...")
# List of files to stage (excluding .venv, __pycache__, etc.)
staged_files = []
for root, dirs, files in os.walk(REPO_PATH):
    # Skip ignored dirs
    if any(ignored in root for ignored in [".venv", ".git", "__pycache__", "instance"]):
        continue
    for file in files:
        if file.endswith((".pyc", ".db", ".sqlite3")):
            continue
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, REPO_PATH).replace("\\", "/")
        staged_files.append(rel_path)

porcelain.add(repo, paths=staged_files)
print(f"Staged {len(staged_files)} files.")

# 3. Commit
try:
    commit_id = porcelain.commit(
        repo,
        message=b"Initial commit: NestKerala premium rental property platform with feedback system",
        author=b"NestKerala Developer <dev@nestkerala.com>",
        committer=b"NestKerala Developer <dev@nestkerala.com>"
    )
    print(f"Committed changes: {commit_id.decode() if isinstance(commit_id, bytes) else commit_id}")
except Exception as e:
    print(f"Commit status: {e}")

# Ensure branch is main
try:
    repo.refs[b'refs/heads/main'] = repo.head()
    repo.refs.set_symbolic_ref(b'HEAD', b'refs/heads/main')
    print("Set branch to main.")
except Exception as e:
    print(f"Branch note: {e}")

# 4. Push to remote
print(f"Attempting to push to remote: {REMOTE_URL} ...")
try:
    porcelain.push(repo, REMOTE_URL, refspecs=b"refs/heads/main:refs/heads/main")
    print("SUCCESS: Pushed main branch to GitHub successfully!")
except Exception as e:
    print(f"PUSH_ERROR: {e}")
    sys.exit(1)
