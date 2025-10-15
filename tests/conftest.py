import sys
import pathlib
# Add the 'src' directory to sys.path so imports like "import swiss_cv" work during tests
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
