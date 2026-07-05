#!/usr/bin/env python3
"""Test suite for validate-identities.py"""

import json
import importlib.util
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def load_validate_module():
    module_path = Path(__file__).resolve().parents[1] / '.agents' / 'scripts' / 'validate-identities.py'
    spec = importlib.util.spec_from_file_location('validate_identities', module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


load_json = load_validate_module().load_json


def test_load_json():
    # Test with a mock JSON file
    test_data = {"test": "data", "number": 123}
    temp_path = Path(__file__).parent / "temp_test.json"

    try:
        temp_path.write_text(json.dumps(test_data), encoding="utf-8")
        loaded = load_json(temp_path)
        assert loaded == test_data
    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_identities_structure():
    root = Path(__file__).resolve().parents[1] / ".agents"
    identities_path = root / "skills" / "codex-agent-identity-bank" / "references" / "identities.json"

    data = load_json(identities_path)
    assert "identities" in data
    assert isinstance(data["identities"], list)
    assert len(data["identities"]) > 0

    # Check first identity has required fields
    first = data["identities"][0]
    required = ["id", "title", "keywords", "skills", "mission", "boundaries", "output_focus"]
    for field in required:
        assert field in first, f"Missing field: {field}"


def run_tests():
    tests = [
        ("load_json", test_load_json),
        ("identities_structure", test_identities_structure),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {name}: {type(e).__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())
