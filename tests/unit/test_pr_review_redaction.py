"""Tests for local PR review redaction preflight."""

from __future__ import annotations

from ai_sdlc.core.loop_models import LoopPolicyProfile
from ai_sdlc.core.pr_review_redaction import (
    RedactionAction,
    RedactionReason,
    analyze_redaction,
)


def test_redaction_includes_safe_text_files(tmp_path) -> None:
    path = tmp_path / "src" / "app.py"
    path.parent.mkdir(parents=True)
    path.write_text("print('hello')\n", encoding="utf-8")

    report = analyze_redaction(tmp_path, ["src/app.py"])

    assert report.included_files == ["src/app.py"]
    assert report.omitted_files == []
    assert report.decisions[0].action == RedactionAction.INCLUDED
    assert report.decisions[0].reason == RedactionReason.NONE


def test_redaction_omits_env_and_private_key_paths(tmp_path) -> None:
    (tmp_path / ".env").write_text("TOKEN=super-secret-value\n", encoding="utf-8")
    (tmp_path / "id_ed25519").write_text("not-a-real-key\n", encoding="utf-8")

    report = analyze_redaction(tmp_path, [".env", "id_ed25519"])

    assert report.omitted_files == [".env", "id_ed25519"]
    assert report.high_risk_secret_files == [".env", "id_ed25519"]
    assert {item.reason for item in report.decisions} == {
        RedactionReason.SECRET_PATH
    }


def test_redaction_marks_common_secret_pattern_as_redacted(tmp_path) -> None:
    path = tmp_path / "src" / "settings.py"
    path.parent.mkdir(parents=True)
    path.write_text(
        'api_key = "abcdefghijklmnop"\n',
        encoding="utf-8",
    )

    report = analyze_redaction(tmp_path, ["src/settings.py"])

    assert report.redacted_files == ["src/settings.py"]
    assert report.high_risk_secret_files == ["src/settings.py"]
    assert report.decisions[0].action == RedactionAction.REDACTED
    assert report.decisions[0].reason == RedactionReason.SECRET_PATTERN
    assert report.decisions[0].redacted_occurrences == 1


def test_redaction_scans_base_blob_for_removed_secret_lines(tmp_path) -> None:
    path = tmp_path / "src" / "settings.py"
    path.parent.mkdir(parents=True)
    path.write_text("token = 'safe'\n", encoding="utf-8")

    report = analyze_redaction(
        tmp_path,
        ["src/settings.py"],
        head_file_bytes={"src/settings.py": b"token = 'safe'\n"},
        base_file_bytes={"src/settings.py": b'token = "abcdefghijklmnop"\n'},
    )

    assert report.redacted_files == ["src/settings.py"]
    assert report.high_risk_secret_files == ["src/settings.py"]
    assert report.decisions[0].action == RedactionAction.REDACTED
    assert report.decisions[0].reason == RedactionReason.SECRET_PATTERN


def test_redaction_omits_private_key_content(tmp_path) -> None:
    path = tmp_path / "src" / "fixture.txt"
    path.parent.mkdir(parents=True)
    path.write_text(
        "-----BEGIN PRIVATE KEY-----\nsecret\n-----END PRIVATE KEY-----\n",
        encoding="utf-8",
    )

    report = analyze_redaction(tmp_path, ["src/fixture.txt"])

    assert report.omitted_files == ["src/fixture.txt"]
    assert report.high_risk_secret_files == ["src/fixture.txt"]
    assert report.decisions[0].reason == RedactionReason.PRIVATE_KEY
    assert report.decisions[0].omitted_lines == 3


def test_redaction_omits_binary_large_and_generated_files(tmp_path) -> None:
    binary = tmp_path / "assets" / "image.bin"
    large = tmp_path / "src" / "large.txt"
    generated = tmp_path / "dist" / "bundle.js"
    binary.parent.mkdir(parents=True)
    large.parent.mkdir(parents=True)
    generated.parent.mkdir(parents=True)
    binary.write_bytes(b"\0\1\2")
    large.write_text("abcdef\n", encoding="utf-8")
    generated.write_text("console.log('generated')\n", encoding="utf-8")

    report = analyze_redaction(
        tmp_path,
        ["assets/image.bin", "src/large.txt", "dist/bundle.js"],
        max_file_bytes=3,
    )

    assert report.binary_files == ["assets/image.bin"]
    assert report.large_files == ["src/large.txt"]
    assert report.generated_files == ["dist/bundle.js"]
    assert report.omitted_files == [
        "assets/image.bin",
        "src/large.txt",
        "dist/bundle.js",
    ]


def test_high_risk_secret_with_code_egress_requires_user_confirmation(tmp_path) -> None:
    path = tmp_path / "src" / "settings.py"
    path.parent.mkdir(parents=True)
    path.write_text('token = "abcdefghijklmnop"\n', encoding="utf-8")

    report = analyze_redaction(
        tmp_path,
        ["src/settings.py"],
        code_egress=True,
        code_egress_confirmed=False,
    )

    assert report.needs_user is True
    assert "High-risk secrets" in report.blocker
    assert "Confirm code egress" in report.next_action


def test_high_risk_secret_can_continue_after_explicit_confirmation(tmp_path) -> None:
    path = tmp_path / "src" / "settings.py"
    path.parent.mkdir(parents=True)
    path.write_text('password = "abcdefghijklmnop"\n', encoding="utf-8")

    report = analyze_redaction(
        tmp_path,
        ["src/settings.py"],
        policy=LoopPolicyProfile(high_risk_secret_policy="needs_user"),
        code_egress=True,
        code_egress_confirmed=True,
    )

    assert report.needs_user is False
    assert report.redacted_files == ["src/settings.py"]


def test_high_risk_allow_with_waiver_still_requires_egress_confirmation(
    tmp_path,
) -> None:
    path = tmp_path / ".env"
    path.write_text("TOKEN=abcdefghijklmnop\n", encoding="utf-8")

    report = analyze_redaction(
        tmp_path,
        [".env"],
        policy=LoopPolicyProfile(
            high_risk_secret_policy="allow-with-waiver",
            allowed_omitted_file_policy="allow-with-waiver",
        ),
        code_egress=True,
        code_egress_confirmed=False,
    )

    assert report.needs_user is True
    assert report.blocked is False
    assert report.high_risk_secret_files == [".env"]
    assert "High-risk secrets" in report.blocker


def test_high_risk_secret_forbid_policy_blocks_code_egress(tmp_path) -> None:
    path = tmp_path / "src" / "settings.py"
    path.parent.mkdir(parents=True)
    path.write_text('token = "abcdefghijklmnop"\n', encoding="utf-8")

    report = analyze_redaction(
        tmp_path,
        ["src/settings.py"],
        policy=LoopPolicyProfile(high_risk_secret_policy="forbid"),
        code_egress=True,
        code_egress_confirmed=True,
    )

    assert report.blocked is True
    assert report.needs_user is False
    assert "forbids" in report.blocker
