import os
import sys
import dulwich.client
from dulwich import porcelain
from dulwich.repo import Repo

REPO_PATH = os.path.abspath(".")
KEY_FILE = os.path.join(REPO_PATH, "id_ed25519")
REMOTE_URL = sys.argv[1] if len(sys.argv) > 1 else "git@github.com:fathimafarhana8714-rgb/hhhh.git"

class CustomSSHVendor(dulwich.client.SubprocessSSHVendor):
    def run_command(self, host, command, **kwargs):
        kwargs['key_filename'] = KEY_FILE
        kwargs['ssh_command'] = "ssh -o StrictHostKeyChecking=accept-new"
        return super().run_command(host, command, **kwargs)

dulwich.client.get_ssh_vendor = CustomSSHVendor

print(f"Loading repository at {REPO_PATH}...")
repo = Repo(REPO_PATH)

# Stage all files
print("Staging all updated project files...")
staged = []
for root, dirs, files in os.walk(REPO_PATH):
    if any(ig in root for ig in [".venv", ".git", "__pycache__", "instance"]):
        continue
    for file in files:
        if file.endswith((".pyc", ".db", ".sqlite3")) or file.startswith(".ssh_key") or file.startswith("id_ed25519"):
            continue
        rel_path = os.path.relpath(os.path.join(root, file), REPO_PATH).replace("\\", "/")
        staged.append(rel_path)

porcelain.add(repo, paths=staged)
try:
    porcelain.remove(repo, ['test_ssh_conn.py'], cached=True)
except Exception:
    pass

try:
    c = porcelain.commit(
        repo,
        message=b"Update README documentation, launcher scripts, requirements, and feedback system details",
        author=b"Fathima Farhana <fathimafarhana8714@gmail.com>",
        committer=b"Fathima Farhana <fathimafarhana8714@gmail.com>"
    )
    print("Committed update:", c.decode() if isinstance(c, bytes) else c)
except Exception as e:
    print("Commit check:", e)

repo.refs[b'refs/heads/main'] = repo.head()
print("Latest commit on main:", repo.head().decode('ascii'))

print(f"Connecting to {REMOTE_URL} using SSH key...")
try:
    print("Pushing to remote with force=True...")
    res = porcelain.push(repo, REMOTE_URL, refspecs=b"refs/heads/main:refs/heads/main", force=True)
    print("SUCCESS: Code pushed to GitHub main branch!")
    print("Result:", res)
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"PUSH_RESULT_ERROR: {e}")
    sys.exit(1)
