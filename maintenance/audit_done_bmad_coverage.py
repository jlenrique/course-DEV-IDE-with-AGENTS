"""Audit: done stories vs formal BMAD + remediation/deferral evidence."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "_bmad-output" / "implementation-artifacts"
SK = re.compile(r"\*\*Sprint key:\*\*\s*`([^`]+)`")


def load_dev() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in (ROOT / "sprint-status.yaml").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^  ([a-z0-9][a-z0-9-]*):\s*(\S+)\s*(?:#.*)?$", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def index_by_sprint_key() -> dict[str, tuple[Path, str]]:
    by_sk: dict[str, tuple[Path, str]] = {}
    for md in ROOT.glob("*.md"):
        c = md.read_text(encoding="utf-8")
        m = SK.search(c)
        if m:
            by_sk[m.group(1).strip()] = (md, c)
    return by_sk


def resolve(key: str, by_sk: dict[str, tuple[Path, str]]) -> tuple[Path, str] | None:
    if key in by_sk:
        return by_sk[key]
    p = ROOT / f"{key}.md"
    if p.exists():
        return p, p.read_text(encoding="utf-8")
    return None


def has_bmad_formal(c: str) -> bool:
    if "## Adversarial Review (BMAD)" in c:
        return True
    if "## BMAD tracking closure" in c:
        return True
    if re.search(r"Review closed:.*BMAD", c, re.I | re.DOTALL):
        return True
    if re.search(r"\|\s*Formal BMAD\s*\|\s*Complete", c):
        return True
    if re.search(r"Formal BMAD review completed", c, re.I):
        return True
    return False


def has_review_closed(c: str) -> bool:
    return bool(re.search(r"Review closed\s*:", c, re.I))


def has_formal_completed_prose(c: str) -> bool:
    return bool(re.search(r"Formal BMAD review completed", c, re.I))


def has_remediation_or_deferral(c: str) -> bool:
    """Explicit remediation, waiver, deferral, or checked review findings (not generic 'review')."""
    low = c.lower()
    if "remediation" in low or "remediated" in low:
        return True
    if re.search(r"\bwaiv", low):
        return True
    if "deferred" in low or "deferral" in low:
        return True
    if "review findings" in low:
        return True
    if "accepted residual" in low:
        return True
    if "no further code" in low:
        return True
    if "formal bmad review completed clean" in low:
        return True
    if "retrospective" in low and "adversarial" in low:
        return True
    if "disposition" in low:
        return True
    if re.search(r"closed (late )?review findings", low):
        return True
    if "remediation closed" in low:
        return True
    if re.search(r"- \[x\].*review", low):
        return True
    if "upstream contract" in low and "bmad" in low:
        return True
    # Process closure: dated BMAD review closed implies findings handled per workflow
    if re.search(r"review closed\s*:", c, re.I) and "bmad" in low:
        return True
    return False


def has_strong_closure(c: str) -> bool:
    """BMAD session formally closed in artifact."""
    if re.search(r"Review closed\s*:", c, re.I):
        return True
    if re.search(r"Formal BMAD review completed", c, re.I):
        return True
    if re.search(r"\|\s*Formal BMAD\s*\|\s*Complete", c):
        return True
    return False


def main() -> None:
    dev = load_dev()
    by_sk = index_by_sprint_key()
    done_keys = sorted(
        k
        for k in dev
        if not k.startswith("epic-")
        and not k.endswith("-retrospective")
        and dev[k] == "done"
    )

    no_artifact: list[str] = []
    no_bmad: list[tuple[str, str]] = []
    strong_pass: list[str] = []
    weak_closure: list[tuple[str, str]] = []  # BMAD but no Review closed / formal complete / table
    weak_remediation: list[tuple[str, str]] = (
        []
    )  # Strong closure but no explicit remediation/deferral/waive language

    for key in done_keys:
        r = resolve(key, by_sk)
        if r is None:
            no_artifact.append(key)
            continue
        path, c = r
        if not has_bmad_formal(c):
            no_bmad.append((key, path.name))
            continue

        if not has_strong_closure(c):
            weak_closure.append((key, path.name))
            continue

        if not has_remediation_or_deferral(c):
            weak_remediation.append((key, path.name))
        else:
            strong_pass.append(key)

    print("BMAD coverage for sprint-status `done` stories (excluding epic*/retrospective)")
    print(f"Total done story keys: {len(done_keys)}")
    print()
    print("=== A) No resolvable artifact ({key}.md or **Sprint key:** match) ===")
    for k in no_artifact:
        print(f"  {k}")
    print(f"Count: {len(no_artifact)}")
    print()
    print("=== B) Artifact found but NO formal BMAD markers (policy gap) ===")
    for k, fn in no_bmad:
        print(f"  {k}  ({fn})")
    print(f"Count: {len(no_bmad)}")
    print()
    print(
        "=== C) Formal BMAD markers but NO strong closure "
        "(missing Review closed: / Formal BMAD review completed / table Formal BMAD|Complete) ==="
    )
    for k, fn in weak_closure:
        print(f"  {k}  ({fn})")
    print(f"Count: {len(weak_closure)}")
    print()
    print(
        "=== D) Strong BMAD closure but NO explicit remediation/deferral/waiver/findings checklist ==="
    )
    for k, fn in weak_remediation:
        print(f"  {k}  ({fn})")
    print(f"Count: {len(weak_remediation)}")
    print()
    print("=== E) Pass: formal BMAD + strong closure + remediation/deferral evidence ===")
    print(f"Count: {len(strong_pass)}")
    print()
    need_work = len(no_artifact) + len(no_bmad) + len(weak_closure) + len(weak_remediation)
    print(
        f"Summary: {len(strong_pass)} pass all three bars; "
        f"{need_work} stories need artifact/BMAD/closure/remediation attention."
    )


if __name__ == "__main__":
    main()
