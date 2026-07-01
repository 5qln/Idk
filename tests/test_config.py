"""config.py — the shared loader/parser/atomic-writer (guards H1/H3/H6)."""
import json
from pathlib import Path
import config


def test_boolean_coercion_yaml_idioms():
    for t in ("true", "True", "yes", "on"):
        assert config._coerce(t) is True
    for f in ("false", "no", "off"):
        assert config._coerce(f) is False
    assert config._coerce("3") == 3
    assert config._coerce("-2") == -2
    assert config._coerce("3.5") == 3.5
    assert config._coerce("ephemeral") == "ephemeral"


def test_parse_real_config(tmp_path):
    cp = Path(config.__file__).resolve().parent.parent / "config.yaml"
    parsed = config.parse_simple_yaml(cp)
    assert "idk" in parsed
    assert isinstance(parsed["idk"].get("max_agent_outputs_in_void"), int)


def test_inline_comment_and_quotes(tmp_path):
    f = tmp_path / "c.yaml"
    f.write_text('idk:\n  tor: yes   # enable\n  pseudonym: "a:b"\n', encoding="utf-8")
    d = config.parse_simple_yaml(f)
    assert d["idk"]["tor"] is True           # not the string "yes"
    assert d["idk"]["pseudonym"] == "a:b"    # colon inside quotes preserved


def test_atomic_write_roundtrip_and_no_tmp_left(tmp_path):
    target = tmp_path / "sub" / "state.json"
    config.atomic_write_json(target, {"a": 1}, indent=2)
    assert json.loads(target.read_text()) == {"a": 1}
    # no leftover *.tmp files in the directory
    assert not list(target.parent.glob("*.tmp"))
