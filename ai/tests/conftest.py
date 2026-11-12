import json, shutil, sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
DEMO = Path(__file__).resolve().parents[1] / "sample_data" / "demo_backup.json"


@pytest.fixture
def store(tmp_path):
    from portal_ai.store import Store
    p = tmp_path / "data.json"; shutil.copy(DEMO, p)
    return Store(p)


@pytest.fixture
def box(store):
    from portal_ai.tools import Toolbox
    return Toolbox(store)
