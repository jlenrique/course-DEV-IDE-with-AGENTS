#!/usr/bin/env python3
"""
Operator Polling Logic for Marcus Precursor Step

Handles polling for slide count, runtime parameters with:
- 3-minute reply hold
- 15-minute auto-close
- Override capability
- Value locking
"""

import time
from typing import Dict, Any, Optional


def poll_operator_for_runtime_params(recommendations: Dict[str, Any], timeout_seconds: int = 900) -> Optional[Dict[str, Any]]:
    """
    Poll operator for confirmation/override of runtime parameters.

    Args:
        recommendations: Dict with recommended values
        timeout_seconds: Auto-close timeout (default 15 min)

    Returns:
        Dict with locked values, or None if timeout
    """

    print("=== MARCUS PRECURSOR POLL: Slide Count & Runtime Parameters ===")
    print("Reply hold: 3 minutes minimum")
    print(f"Auto-close: {timeout_seconds//60} minutes from now")
    print()

    print("CONTENT ANALYSIS:")
    print(f"- Word count: {recommendations['word_count']}")
    print(f"- Sections found: {recommendations['analysis']['total_sections']}")
    print()

    print("RECOMMENDATIONS:")
    print(f"- Slide count: {recommendations['recommended_slide_count']}")
    print(f"- Total runtime: {recommendations['estimated_total_runtime_minutes']} minutes")
    print(f"- Average slide runtime: {recommendations['average_slide_runtime_seconds']} seconds")
    print(f"- Runtime variability: {recommendations['runtime_variability_scale']} (0.0=uniform, 2.0=wide)")
    print(f"- Mode proportions: {recommendations['recommended_mode_proportions']}")
    print()

    print("OPTIONS:")
    print("1. Accept all recommendations")
    print("2. Override slide count only")
    print("3. Override total runtime only")
    print("4. Override average slide runtime only")
    print("5. Override variability only")
    print("6. Override mode proportions only")
    print("7. Override all parameters")
    print("8. Cancel (auto-close in remaining time)")
    print()

    start_time = time.time()
    hold_end = start_time + 180  # 3 min hold

    while True:
        current_time = time.time()
        if current_time - start_time > timeout_seconds:
            print("POLL AUTO-CLOSED: No response within timeout.")
            return None

        if current_time < hold_end:
            remaining_hold = int(hold_end - current_time)
            print(f"Reply hold active: {remaining_hold} seconds remaining")
            time.sleep(10)  # Check every 10 seconds
            continue

        # Hold period passed, accept input
        try:
            choice = input("Enter your choice (1-8): ").strip()

            if choice == "1":
                # Accept all
                return {
                    'locked_slide_count': recommendations['recommended_slide_count'],
                    'target_total_runtime_minutes': recommendations['estimated_total_runtime_minutes'],
                    'slide_runtime_average_seconds': recommendations['average_slide_runtime_seconds'],
                    'slide_runtime_variability_scale': recommendations['runtime_variability_scale'],
                    'slide_mode_proportions': recommendations['recommended_mode_proportions']
                }
            elif choice == "2":
                count = int(input(f"New slide count (current: {recommendations['recommended_slide_count']}): "))
                return {
                    'locked_slide_count': count,
                    'target_total_runtime_minutes': recommendations['estimated_total_runtime_minutes'],
                    'slide_runtime_average_seconds': recommendations['average_slide_runtime_seconds'],
                    'slide_runtime_variability_scale': recommendations['runtime_variability_scale'],
                    'slide_mode_proportions': recommendations['recommended_mode_proportions']
                }
            elif choice == "3":
                runtime = float(input(f"New total runtime minutes (current: {recommendations['estimated_total_runtime_minutes']}): "))
                return {
                    'locked_slide_count': recommendations['recommended_slide_count'],
                    'target_total_runtime_minutes': runtime,
                    'slide_runtime_average_seconds': recommendations['average_slide_runtime_seconds'],
                    'slide_runtime_variability_scale': recommendations['runtime_variability_scale'],
                    'slide_mode_proportions': recommendations['recommended_mode_proportions']
                }
            elif choice == "4":
                avg = int(input(f"New average slide runtime seconds (current: {recommendations['average_slide_runtime_seconds']}): "))
                return {
                    'locked_slide_count': recommendations['recommended_slide_count'],
                    'target_total_runtime_minutes': recommendations['estimated_total_runtime_minutes'],
                    'slide_runtime_average_seconds': avg,
                    'slide_runtime_variability_scale': recommendations['runtime_variability_scale'],
                    'slide_mode_proportions': recommendations['recommended_mode_proportions']
                }
            elif choice == "5":
                var = float(input(f"New variability scale (0.0-2.0, current: {recommendations['runtime_variability_scale']}): "))
                return {
                    'locked_slide_count': recommendations['recommended_slide_count'],
                    'target_total_runtime_minutes': recommendations['estimated_total_runtime_minutes'],
                    'slide_runtime_average_seconds': recommendations['average_slide_runtime_seconds'],
                    'slide_runtime_variability_scale': var,
                    'slide_mode_proportions': recommendations['recommended_mode_proportions']
                }
            elif choice == "6":
                print("Override mode proportions:")
                creative = float(input("Creative proportion (0.0-1.0): "))
                literal_text = float(input("Literal-text proportion (0.0-1.0): "))
                literal_visual = float(input("Literal-visual proportion (0.0-1.0): "))
                total = creative + literal_text + literal_visual
                if abs(total - 1.0) > 0.01:
                    print(f"Proportions must sum to 1.0, got {total}. Try again.")
                    continue
                proportions = {'creative': creative, 'literal_text': literal_text, 'literal_visual': literal_visual}
                return {
                    'locked_slide_count': recommendations['recommended_slide_count'],
                    'target_total_runtime_minutes': recommendations['estimated_total_runtime_minutes'],
                    'slide_runtime_average_seconds': recommendations['average_slide_runtime_seconds'],
                    'slide_runtime_variability_scale': recommendations['runtime_variability_scale'],
                    'slide_mode_proportions': proportions
                }
            elif choice == "7":
                print("Override all parameters:")
                count = int(input("Slide count: "))
                runtime = float(input("Total runtime minutes: "))
                avg = int(input("Average slide runtime seconds: "))
                var = float(input("Variability scale (0.0-2.0): "))
                creative = float(input("Creative proportion (0.0-1.0): "))
                literal_text = float(input("Literal-text proportion (0.0-1.0): "))
                literal_visual = float(input("Literal-visual proportion (0.0-1.0): "))
                total = creative + literal_text + literal_visual
                if abs(total - 1.0) > 0.01:
                    print(f"Proportions must sum to 1.0, got {total}. Try again.")
                    continue
                proportions = {'creative': creative, 'literal_text': literal_text, 'literal_visual': literal_visual}
                return {
                    'locked_slide_count': count,
                    'target_total_runtime_minutes': runtime,
                    'slide_runtime_average_seconds': avg,
                    'slide_runtime_variability_scale': var,
                    'slide_mode_proportions': proportions
                }
            elif choice == "8":
                print("Poll cancelled by operator.")
                return None
            else:
                print("Invalid choice. Try again.")
                continue

        except ValueError:
            print("Invalid input. Try again.")
            continue
        except KeyboardInterrupt:
            print("Poll cancelled by operator.")
            return None


def check_runtime_feasibility(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check mathematical feasibility of runtime parameters.

    Returns:
        {'feasible': bool, 'issues': [], 'recommendations': []}
    """
    issues = []
    recommendations = []

    slide_count = params['locked_slide_count']
    total_min = params['target_total_runtime_minutes']
    avg_sec = params['slide_runtime_average_seconds']
    variability = params['slide_runtime_variability_scale']

    total_sec = total_min * 60
    avg_total_sec = slide_count * avg_sec
    sd_sec = avg_sec * variability

    # Minimum possible total (all slides at avg - 2SD, but not negative)
    min_possible = slide_count * max(0, avg_sec - 2 * sd_sec)
    # Maximum possible total (all slides at avg + 2SD)
    max_possible = slide_count * (avg_sec + 2 * sd_sec)

    if total_sec < min_possible:
        issues.append(f"Target total {total_sec}s too low for min possible {min_possible:.0f}s")
        recommendations.append(f"Increase target runtime to at least {min_possible/60:.1f} min, or reduce slide count, or increase average slide time")

    if total_sec > max_possible:
        issues.append(f"Target total {total_sec}s too high for max possible {max_possible:.0f}s")
        recommendations.append(f"Decrease target runtime to at most {max_possible/60:.1f} min, or increase slide count, or decrease average slide time")

    # Check if variability allows reasonable distribution
    if sd_sec > avg_sec:
        issues.append(f"Variability scale {variability} creates SD {sd_sec:.0f}s > avg {avg_sec}s, may cause negative times")
        recommendations.append("Reduce variability scale to < 1.0")

    feasible = len(issues) == 0

    return {
        'feasible': feasible,
        'issues': issues,
        'recommendations': recommendations
    }


def validate_locked_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that locked parameters are reasonable and feasible."""
    # Basic range checks
    basic_valid = (
        1 <= params['locked_slide_count'] <= 20 and
        1 <= params['target_total_runtime_minutes'] <= 30 and
        10 <= params['slide_runtime_average_seconds'] <= 120 and
        0.0 <= params['slide_runtime_variability_scale'] <= 2.0
    )

    if not basic_valid:
        return {'valid': False, 'reason': 'Parameters out of valid ranges'}

    # Feasibility check
    feasibility = check_runtime_feasibility(params)

    return {
        'valid': feasibility['feasible'],
        'feasible': feasibility,
        'reason': 'Feasible' if feasibility['feasible'] else 'Math not feasible'
    }


if __name__ == '__main__':
    # Test with sample recommendations
    sample_recs = {
        'recommended_slide_count': 10,
        'estimated_total_runtime_minutes': 15.0,
        'word_count': 7450,
        'average_slide_runtime_seconds': 45,
        'runtime_variability_scale': 0.5,
        'analysis': {'total_sections': 18}
    }

    result = poll_operator_for_runtime_params(sample_recs, timeout_seconds=60)  # Short timeout for testing
    if result:
        print("Locked parameters:", result)
        print("Valid:", validate_locked_params(result))
    else:
        print("Poll failed or cancelled.")