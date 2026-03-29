# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Generate a skeleton production plan from content type and module structure.

Reads the course context YAML to resolve module/lesson hierarchy, then
produces a markdown production plan with specialist sequencing, checkpoint
gates, and dependency ordering appropriate for the requested content type.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


CONTENT_TYPE_WORKFLOWS: dict[str, dict[str, Any]] = {
    "lecture-slides": {
        "label": "Lecture Slides",
        "stages": [
            {"stage": "outline", "specialist": "content-creator", "description": "Draft learning-objective-aligned outline"},
            {"stage": "slides", "specialist": "gamma-specialist", "description": "Generate slide deck from outline"},
            {"stage": "review", "specialist": "quality-reviewer", "description": "Quality gate: style bible compliance, Bloom's alignment"},
            {"stage": "checkpoint", "specialist": "human", "description": "User review and approval"},
        ],
    },
    "case-study": {
        "label": "Case Study",
        "stages": [
            {"stage": "draft", "specialist": "content-creator", "description": "Draft clinical case with learning integration"},
            {"stage": "review", "specialist": "quality-reviewer", "description": "Quality gate: clinical accuracy, pedagogical alignment"},
            {"stage": "checkpoint", "specialist": "human", "description": "User review and approval"},
        ],
    },
    "assessment": {
        "label": "Assessment / Quiz",
        "stages": [
            {"stage": "draft", "specialist": "content-creator", "description": "Draft assessment items aligned to objectives"},
            {"stage": "alignment-check", "specialist": "quality-reviewer", "description": "Verify assessment-objective tracing"},
            {"stage": "checkpoint", "specialist": "human", "description": "User review and approval"},
            {"stage": "publish", "specialist": "canvas-specialist", "description": "Publish to LMS"},
        ],
    },
    "discussion-prompt": {
        "label": "Discussion Prompt",
        "stages": [
            {"stage": "draft", "specialist": "content-creator", "description": "Draft discussion prompt with facilitation notes"},
            {"stage": "checkpoint", "specialist": "human", "description": "User review and approval"},
            {"stage": "publish", "specialist": "canvas-specialist", "description": "Publish to LMS"},
        ],
    },
    "video-script": {
        "label": "Video Script",
        "stages": [
            {"stage": "draft", "specialist": "content-creator", "description": "Draft video script with visual cues"},
            {"stage": "review", "specialist": "quality-reviewer", "description": "Quality gate: content accuracy, pacing"},
            {"stage": "checkpoint", "specialist": "human", "description": "User review and approval"},
        ],
    },
    "animated-explainer": {
        "label": "Animated Explainer",
        "stages": [
            {"stage": "brief", "specialist": "content-creator", "description": "Draft instructional brief for animation"},
            {"stage": "storyboard", "specialist": "vyond-specialist", "description": "Produce storyboard and Vyond build guidance"},
            {"stage": "review", "specialist": "quality-reviewer", "description": "Quality gate: instructional clarity and pacing"},
            {"stage": "checkpoint", "specialist": "human", "description": "User review and approval"},
        ],
    },
    "bespoke-medical-illustration": {
        "label": "Bespoke Medical Illustration",
        "stages": [
            {"stage": "prompting", "specialist": "midjourney-specialist", "description": "Generate parameterized prompt package and iteration plan"},
            {"stage": "review", "specialist": "quality-reviewer", "description": "Quality gate: visual fidelity and instructional fit"},
            {"stage": "checkpoint", "specialist": "human", "description": "User review and approval"},
        ],
    },
    "voiceover": {
        "label": "Voiceover Narration",
        "stages": [
            {"stage": "script", "specialist": "content-creator", "description": "Draft narration script"},
            {"stage": "script-review", "specialist": "quality-reviewer", "description": "Quality gate: tone, clarity, pacing"},
            {"stage": "script-checkpoint", "specialist": "human", "description": "Script approval before synthesis"},
            {"stage": "synthesis", "specialist": "elevenlabs-specialist", "description": "Voice synthesis from approved script"},
            {"stage": "audio-checkpoint", "specialist": "human", "description": "Audio review and approval"},
        ],
    },
    "interactive-module": {
        "label": "Interactive Module",
        "stages": [
            {"stage": "design", "specialist": "content-creator", "description": "Design interaction model and content flow"},
            {"stage": "author", "specialist": "articulate-specialist", "description": "Build Storyline/Rise interaction guidance and branching map"},
            {"stage": "deploy", "specialist": "coursearc-specialist", "description": "Prepare LTI embedding and SCORM deployment checklist"},
            {"stage": "review", "specialist": "quality-reviewer", "description": "Quality gate: interaction design, accessibility"},
            {"stage": "checkpoint", "specialist": "human", "description": "User review and approval"},
        ],
    },
    "coursearc-deployment": {
        "label": "CourseArc Deployment",
        "stages": [
            {"stage": "package-check", "specialist": "coursearc-specialist", "description": "Validate LTI 1.3 and SCORM deployment prerequisites"},
            {"stage": "accessibility-check", "specialist": "quality-reviewer", "description": "Quality gate: WCAG 2.1 AA interactive compliance"},
            {"stage": "checkpoint", "specialist": "human", "description": "User review and approval"},
        ],
    },
}


def load_course_context(course_context_path: Path) -> dict | None:
    """Load course context YAML if available."""
    if not course_context_path.exists():
        return None
    if yaml is None:
        print("Warning: pyyaml not available, skipping course context", file=sys.stderr)
        return None
    with open(course_context_path) as f:
        return yaml.safe_load(f)


def generate_plan(
    content_type: str,
    module_id: str | None = None,
    lesson_id: str | None = None,
    course_context: dict | None = None,
) -> str:
    """Generate a markdown production plan for the given content type and scope.

    Args:
        content_type: One of the known content type keys.
        module_id: Optional module identifier for scope.
        lesson_id: Optional lesson identifier for scope.
        course_context: Optional course context dictionary from YAML.

    Returns:
        Markdown string with the production plan.
    """
    workflow = CONTENT_TYPE_WORKFLOWS.get(content_type)
    if not workflow:
        available = ", ".join(sorted(CONTENT_TYPE_WORKFLOWS.keys()))
        return f"Unknown content type: {content_type}\n\nAvailable types: {available}"

    lines: list[str] = []
    lines.append(f"# Production Plan: {workflow['label']}")
    lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Content Type:** {workflow['label']}")

    if module_id:
        lines.append(f"**Module:** {module_id}")
    if lesson_id:
        lines.append(f"**Lesson:** {lesson_id}")

    if course_context and module_id:
        modules = course_context.get("modules", {})
        module_info = modules.get(module_id, {})
        if module_info:
            lines.append(f"**Module Title:** {module_info.get('title', 'Unknown')}")
            if lesson_id:
                lessons = module_info.get("lessons", {})
                lesson_info = lessons.get(lesson_id, {})
                if lesson_info:
                    lines.append(f"**Lesson Title:** {lesson_info.get('title', 'Unknown')}")
                    objectives = lesson_info.get("learning_objectives", [])
                    if objectives:
                        lines.append("\n**Learning Objectives:**")
                        for obj in objectives:
                            lines.append(f"- {obj}")

    lines.append("\n## Production Stages\n")
    lines.append("| # | Stage | Specialist | Description | Status |")
    lines.append("|---|-------|-----------|-------------|--------|")

    for i, stage in enumerate(workflow["stages"], 1):
        specialist = stage["specialist"]
        if specialist == "human":
            specialist = "**USER REVIEW**"
        lines.append(f"| {i} | {stage['stage']} | {specialist} | {stage['description']} | pending |")

    lines.append("\n## Pre-Production Checklist\n")
    lines.append("- [ ] Style bible consulted (`resources/style-bible/`)")
    lines.append("- [ ] Exemplar library checked (`resources/exemplars/`)")
    lines.append("- [ ] Learning objectives confirmed")
    lines.append("- [ ] Asset-lesson pairing established")
    lines.append("- [ ] Source materials gathered (if applicable)")

    lines.append("\n## Notes\n")
    lines.append("- All quality gates reference the style bible as primary rubric")
    lines.append("- User checkpoints require explicit approval before proceeding")
    lines.append("- Asset-lesson pairing is verified before marking any stage complete")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a skeleton production plan from content type and module structure.",
        epilog="Outputs a markdown production plan to stdout.",
    )
    parser.add_argument(
        "content_type",
        choices=sorted(CONTENT_TYPE_WORKFLOWS.keys()),
        help="Type of content to produce.",
    )
    parser.add_argument(
        "--module",
        type=str,
        default=None,
        help="Module identifier (e.g., M1, M2).",
    )
    parser.add_argument(
        "--lesson",
        type=str,
        default=None,
        help="Lesson identifier within the module.",
    )
    parser.add_argument(
        "--course-context",
        type=Path,
        default=None,
        help="Path to course_context.yaml. Default: state/config/course_context.yaml",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output as JSON instead of markdown.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print diagnostic info to stderr.",
    )
    args = parser.parse_args()

    course_context_path = args.course_context
    if course_context_path is None:
        project_root = Path(__file__).resolve().parent.parent.parent
        course_context_path = project_root / "state" / "config" / "course_context.yaml"

    course_context = load_course_context(course_context_path)

    if args.verbose:
        print(f"Content type: {args.content_type}", file=sys.stderr)
        print(f"Course context path: {course_context_path}", file=sys.stderr)
        print(f"Course context loaded: {course_context is not None}", file=sys.stderr)

    try:
        if args.output_json:
            workflow = CONTENT_TYPE_WORKFLOWS.get(args.content_type)
            output = {
                "content_type": args.content_type,
                "label": workflow["label"] if workflow else "Unknown",
                "module": args.module,
                "lesson": args.lesson,
                "stages": workflow["stages"] if workflow else [],
                "generated_at": datetime.now().isoformat(),
            }
            json.dump(output, sys.stdout, indent=2)
            print()
        else:
            plan = generate_plan(
                content_type=args.content_type,
                module_id=args.module,
                lesson_id=args.lesson,
                course_context=course_context,
            )
            print(plan)
        sys.exit(0)
    except Exception as e:
        error = {"error": str(e), "timestamp": datetime.now().isoformat()}
        json.dump(error, sys.stderr, indent=2)
        print(file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
