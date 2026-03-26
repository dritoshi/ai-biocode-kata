"""check_urls_browser のテスト."""

from pathlib import Path

from scripts.review.check_urls_browser import (
    build_output_document,
    classify_browser_observation,
    detect_block_reason,
    select_target_entries,
    summarize_body_text,
)


SAMPLE_DOCUMENT = {
    "metadata": {"timestamp": "2026-03-25T00:00:00+0900"},
    "summary": {"ok": 1, "anti-bot": 2},
    "urls": [
        {
            "url": "https://example.org/ok",
            "category": "ok",
            "locations": [{"file": "chapters/01_design.md", "line": 1}],
        },
        {
            "url": "https://example.org/blocked",
            "category": "anti-bot",
            "locations": [{"file": "chapters/02_terminal.md", "line": 2}],
        },
        {
            "url": "https://example.org/paywall",
            "category": "anti-bot",
            "locations": [{"file": "references/ch02.bib", "line": 20}],
        },
    ],
}


class TestSelectTargetEntries:
    """対象 URL 抽出のテスト."""

    def test_filters_by_category(self) -> None:
        entries = select_target_entries(SAMPLE_DOCUMENT, category="anti-bot")
        assert len(entries) == 2
        assert all(entry["category"] == "anti-bot" for entry in entries)

    def test_applies_limit(self) -> None:
        entries = select_target_entries(SAMPLE_DOCUMENT, category="anti-bot", limit=1)
        assert len(entries) == 1
        assert entries[0]["url"] == "https://example.org/blocked"


class TestDetectBlockReason:
    """ブロック画面らしさ判定のテスト."""

    def test_detects_challenge_page(self) -> None:
        reason = detect_block_reason(
            page_title="Just a moment...",
            body_text="Checking your browser before accessing the site.",
        )
        assert reason == "challenge_page"

    def test_detects_access_denied(self) -> None:
        reason = detect_block_reason(
            page_title="Access Denied",
            body_text="You do not have permission to access this resource.",
        )
        assert reason == "access_denied"

    def test_returns_none_for_normal_page(self) -> None:
        reason = detect_block_reason(
            page_title="A normal page",
            body_text="This page contains the article abstract and metadata.",
        )
        assert reason is None


class TestClassifyBrowserObservation:
    """ブラウザ観測結果の分類テスト."""

    def test_marks_browser_ok_with_title_and_200(self) -> None:
        category, error = classify_browser_observation(
            page_title="Article landing page",
            body_text="Abstract and citation details.",
            response_status=200,
        )
        assert category == "browser_ok"
        assert error is None

    def test_marks_blocked_when_challenge_text_present(self) -> None:
        category, error = classify_browser_observation(
            page_title="Security check",
            body_text="Verify you are human to continue.",
            response_status=200,
        )
        assert category == "browser_blocked"
        assert error == "challenge_page"

    def test_marks_error_without_title(self) -> None:
        category, error = classify_browser_observation(
            page_title="",
            body_text="",
            response_status=200,
        )
        assert category == "browser_error"
        assert error == "missing_title_or_unexpected_status"


class TestUtilityHelpers:
    """補助関数のテスト."""

    def test_summarize_body_text_truncates(self) -> None:
        text = "A" * 400
        summary = summarize_body_text(text, limit=20)
        assert summary == ("A" * 20) + "..."

    def test_build_output_document_counts_categories(self) -> None:
        rows = [
            {"browser_category": "browser_ok"},
            {"browser_category": "browser_ok"},
            {"browser_category": "browser_blocked"},
        ]
        output = build_output_document(
            source_path=Path("docs/review/url_check.json"),
            category="anti-bot",
            timeout_sec=20.0,
            delay_sec=1.0,
            rows=rows,
        )
        assert output["metadata"]["category_filter"] == "anti-bot"
        assert output["metadata"]["total_checked"] == 3
        assert output["summary"] == {
            "browser_ok": 2,
            "browser_blocked": 1,
        }
