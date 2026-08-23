"""Prepare the local fictional demo database without deleting any records."""
from pathlib import Path
import subprocess
import sys
from app.seed import seed

if __name__ == "__main__":
    root=Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable,"-m","alembic","upgrade","head"],cwd=root,check=True)
    print(seed())
    print("Local synthetic demo setup is ready. Existing records were not deleted.")
