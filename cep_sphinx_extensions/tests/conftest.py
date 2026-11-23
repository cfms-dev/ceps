import importlib.util
import sys
from pathlib import Path

_ROOT_PATH = Path(__file__, "..", "..", "..").resolve()
CEP_ROOT = Path(__file__).resolve().parent / "ceps"

# Import "check-ceps.py" as "check_ceps"
CHECK_CEPS_PATH = _ROOT_PATH / "check-ceps.py"
spec = importlib.util.spec_from_file_location("check_ceps", CHECK_CEPS_PATH)
sys.modules["check_ceps"] = check_ceps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_ceps)
