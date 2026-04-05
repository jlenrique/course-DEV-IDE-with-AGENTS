"""Update gary-slide-content.json literal-text slides with real source text."""
import json
import pathlib

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
p = PROJECT_ROOT / "course-content" / "staging" / "tracked" / "source-bundles" / "apc-c1m1-tejal-20260403" / "gary-slide-content.json"
data = json.loads(p.read_text(encoding="utf-8"))

# Slide 3: full CLO list verbatim from extracted.md (literal-text, textMode=preserve)
slide3_content = (
    "By the end of this module, the learner will be able to:\n"
    "1. Define the \u201cinnovation mindset\u201d and correlate core clinical competencies "
    "(e.g. diagnostic reasoning, empathy) directly to established innovation frameworks "
    "like Design Thinking. (Understand / Apply)\n"
    "2. Analyze the macro-economic and structural trends\u2014including administrative burnout, "
    "healthcare consumerism, and technological acceleration\u2014that necessitate intrapreneurial "
    "physician leadership. (Analyze)\n"
    "3. Differentiate between a superficial \u201cidea\u201d and a rigorously vetted \u201copportunity\u201d "
    "using the core tenets of Sandra Lam\u2019s Intrapreneurship Formula. (Analyze / Evaluate)\n"
    "4. Evaluate systemic operational failures within their own clinical environment by "
    "conducting root-cause analyses and defending their findings in a peer-reviewed forum "
    "(the \u201cM&M of Innovation\u201d). (Evaluate)\n"
    "5. Create a personal innovation baseline (SWOT analysis) and an \u201cOpportunity Radar\u201d "
    "that captures and categorizes real-world clinical frictions for future project development. (Create)"
)

# Slide 5: CLO4 + M&M reference verbatim (literal-text, textMode=preserve)
slide5_content = (
    "Evaluate systemic operational failures within their own clinical environment by "
    "conducting root-cause analyses and defending their findings in a peer-reviewed forum "
    "(the \u201cM&M of Innovation\u201d). (CLO4: Evaluate)"
)

# Slide 6: CLO5 verbatim (literal-text, textMode=preserve)
slide6_content = (
    "Create a personal innovation baseline (SWOT analysis) and an \u201cOpportunity Radar\u201d "
    "that captures and categorizes real-world clinical frictions for future project development. "
    "(CLO5: Create)"
)

updates = {3: slide3_content, 5: slide5_content, 6: slide6_content}

for slide in data["slides"]:
    sn = slide.get("slide_number")
    if sn in updates:
        old = slide["content"][:70]
        slide["content"] = updates[sn]
        print(f"Slide {sn}: '{old}...' -> updated ({len(updates[sn])} chars)")

p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print("Written.")
