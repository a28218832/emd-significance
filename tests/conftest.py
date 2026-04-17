import sys
from pathlib import Path

# Ensure the repo root (which contains the `emdsig` package) is on sys.path
# so `from emdsig import ...` works without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
