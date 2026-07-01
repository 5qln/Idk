"""decoding.py — footer parsing + version export (guards H5, validator philosophy)."""
import decoding


def test_version_is_exported():
    assert decoding.__version__ == decoding.DECODING_VERSION  # H5: no longer dead


def test_parse_footer_extracts_named_fields():
    block = "X: Why does this hold?\nALPHA: self-verifying infrastructure\nSEEKS: convergence"
    fields = decoding.parse_footer(block)
    assert fields.get("ALPHA") == "self-verifying infrastructure"
    assert fields.get("SEEKS") == "convergence"


def test_question_recognition():
    assert decoding._looks_like_question("Why does the seed hold?") is True
    assert decoding._looks_like_question("This is a flat statement.") is False
