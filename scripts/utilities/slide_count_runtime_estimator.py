#!/usr/bin/env python3
"""
Slide Count and Runtime Estimator for Marcus Precursor Step

Analyzes extracted.md to recommend:
- Slide count (1 per major section, operator-overridable ceiling)
- Total runtime estimate (based on word count)
- Word count
- Average slide runtime (default 45s)
- Runtime variability scale (default 0.5)
"""

import re
from pathlib import Path
from typing import Any


def analyze_content_for_slides(
    extracted_md_path: str,
    max_slides: int | None = None,
) -> dict[str, Any]:
    """Analyze extracted.md to recommend slide count and runtime parameters.

    Args:
        extracted_md_path: Path to the extracted.md file.
        max_slides: Optional operator ceiling for slide count.
            If None, uses the section count directly (no arbitrary cap).
    """

    with open(extracted_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count words
    words = re.findall(r'\b\w+\b', content)
    word_count = len(words)

    # Identify major sections (Slide headers, major headings)
    slide_headers = re.findall(r'^Slide \d+:', content, re.MULTILINE)
    major_sections = re.findall(r'^## .*$', content, re.MULTILINE)
    part_headers = re.findall(r'^Part \d+:', content, re.MULTILINE)

    # Recommend slide count: section-driven, operator ceiling if provided
    section_count = len(slide_headers) + len(major_sections) + len(part_headers)
    recommended_slides = max(section_count, 1)
    if max_slides is not None:
        recommended_slides = min(recommended_slides, max_slides)

    # Estimate total runtime: word count / 150 wpm for narration + slide time
    narration_minutes = word_count / 150  # 150 words per minute typical speaking rate
    slide_time_minutes = recommended_slides * 0.75  # 45 seconds per slide
    total_runtime_minutes = narration_minutes + slide_time_minutes

    # Round to reasonable values
    total_runtime_minutes = round(total_runtime_minutes, 1)
    if total_runtime_minutes < 1:
        total_runtime_minutes = 1.0  # floor

    return {
        'recommended_slide_count': recommended_slides,
        'estimated_total_runtime_minutes': total_runtime_minutes,
        'word_count': word_count,
        'average_slide_runtime_seconds': 45,
        'runtime_variability_scale': 0.5,
        'recommended_mode_proportions': {
            'creative': 0.4,
            'literal_text': 0.3,
            'literal_visual': 0.3
        },
        'analysis': {
            'slide_headers_found': len(slide_headers),
            'major_sections_found': len(major_sections),
            'part_headers_found': len(part_headers),
            'total_sections': section_count
        }
    }


def main():
    """CLI interface for testing."""
    import argparse
    parser = argparse.ArgumentParser(description="Slide count and runtime estimator")
    parser.add_argument("extracted_md_path", help="Path to extracted.md")
    parser.add_argument("--max-slides", type=int, default=None,
                        help="Operator ceiling for slide count (no cap if omitted)")
    args = parser.parse_args()

    result = analyze_content_for_slides(args.extracted_md_path, max_slides=args.max_slides)

    print("Slide Count and Runtime Recommendations:")
    print(f"- Recommended slides: {result['recommended_slide_count']}")
    print(f"- Estimated total runtime: {result['estimated_total_runtime_minutes']} minutes")
    print(f"- Word count: {result['word_count']}")
    print(f"- Average slide runtime: {result['average_slide_runtime_seconds']} seconds")
    print(f"- Runtime variability scale: {result['runtime_variability_scale']}")
    print(f"\nAnalysis: {result['analysis']}")


if __name__ == '__main__':
    main()