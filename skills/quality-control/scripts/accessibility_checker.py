"""Automated WCAG 2.1 AA accessibility scanning for educational content.

Checks reading level (Flesch-Kincaid), heading hierarchy, alt text presence,
and content density. Returns structured JSON with pass/fail per criterion.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def flesch_kincaid_grade(text: str) -> float:
    """Estimate Flesch-Kincaid grade level for the given text."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = text.split()

    if not sentences or not words:
        return 0.0

    syllable_count = sum(_count_syllables(w) for w in words)
    word_count = len(words)
    sentence_count = len(sentences)

    grade = (
        0.39 * (word_count / sentence_count)
        + 11.8 * (syllable_count / word_count)
        - 15.59
    )
    return round(max(grade, 0.0), 1)


def _count_syllables(word: str) -> int:
    """Approximate syllable count using vowel-group heuristic."""
    word = word.lower().strip(".,;:!?\"'()-")
    if not word:
        return 1
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def check_heading_hierarchy(text: str) -> list[dict]:
    """Check for heading level skips (e.g., H2 → H4 without H3)."""
    findings = []
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    headings = [(len(m.group(1)), m.group(2), m.start()) for m in heading_pattern.finditer(text)]

    for i in range(1, len(headings)):
        prev_level = headings[i - 1][0]
        curr_level = headings[i][0]
        if curr_level > prev_level + 1:
            line_num = text[:headings[i][2]].count('\n') + 1
            findings.append({
                "severity": "critical",
                "location": f"Line {line_num}, heading '{headings[i][1]}'",
                "description": f"Heading hierarchy skip: H{prev_level} → H{curr_level} (missing H{prev_level + 1})",
                "fix_suggestion": f"Add an H{prev_level + 1} heading before this section, or promote this to H{prev_level + 1}",
            })
    return findings


def check_alt_text(text: str) -> list[dict]:
    """Check for image references missing alt text annotations."""
    findings = []
    img_pattern = re.compile(r'!\[([^\]]*)\]\([^)]+\)', re.MULTILINE)
    for match in img_pattern.finditer(text):
        alt = match.group(1).strip()
        if not alt:
            line_num = text[:match.start()].count('\n') + 1
            findings.append({
                "severity": "critical",
                "location": f"Line {line_num}",
                "description": "Image reference missing alt text",
                "fix_suggestion": "Add descriptive alt text inside the brackets: ![description of image](url)",
            })
    return findings


def check_content_density(text: str, max_words_per_block: int = 200) -> list[dict]:
    """Check for content blocks exceeding cognitive load guidelines."""
    findings = []
    blocks = re.split(r'\n#{1,6}\s+', text)
    for i, block in enumerate(blocks):
        word_count = len(block.split())
        if word_count > max_words_per_block:
            findings.append({
                "severity": "medium",
                "location": f"Content block {i + 1}",
                "description": f"Content block has {word_count} words (max recommended: {max_words_per_block})",
                "fix_suggestion": "Break into smaller sections with subheadings for better readability",
            })
    return findings


def run_accessibility_check(
    content: str,
    target_grade: float = 12.0,
) -> dict:
    """Run all accessibility checks and return structured results.

    Args:
        content: Text content to check.
        target_grade: Maximum acceptable Flesch-Kincaid grade level.

    Returns:
        Structured dict with overall status, grade level, and findings.
    """
    findings: list[dict] = []

    grade = flesch_kincaid_grade(content)
    grade_diff = grade - target_grade
    if grade_diff > 3:
        findings.append({
            "severity": "high",
            "location": "Overall document",
            "description": f"Reading level Grade {grade} exceeds target Grade {target_grade} by {grade_diff:.1f}",
            "fix_suggestion": "Simplify sentence structure and replace complex terminology where appropriate",
        })
    elif grade_diff > 0:
        findings.append({
            "severity": "medium",
            "location": "Overall document",
            "description": f"Reading level Grade {grade} is {grade_diff:.1f} above target Grade {target_grade}",
            "fix_suggestion": "Consider simplifying compound sentences for accessibility",
        })

    findings.extend(check_heading_hierarchy(content))
    findings.extend(check_alt_text(content))
    findings.extend(check_content_density(content))

    critical_count = sum(1 for f in findings if f["severity"] == "critical")
    status = "fail" if critical_count > 0 else "pass"

    return {
        "checker": "accessibility",
        "status": status,
        "reading_level": grade,
        "target_grade": target_grade,
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": critical_count,
            "high": sum(1 for f in findings if f["severity"] == "high"),
            "medium": sum(1 for f in findings if f["severity"] == "medium"),
            "low": sum(1 for f in findings if f["severity"] == "low"),
        },
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: accessibility_checker.py <file_path> [--target-grade N]")
        sys.exit(2)

    file_path = Path(sys.argv[1])
    target = 12.0
    if "--target-grade" in sys.argv:
        idx = sys.argv.index("--target-grade")
        target = float(sys.argv[idx + 1])

    content = file_path.read_text(encoding="utf-8")
    result = run_accessibility_check(content, target_grade=target)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "pass" else 1)
