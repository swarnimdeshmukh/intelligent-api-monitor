from pathlib import Path
def test_runbooks(): assert len(list(Path('data/runbooks').glob('*.md')))>=4
