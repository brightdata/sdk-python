#!/usr/bin/env python3
"""
Comprehensive test runner - validates EVERYTHING
Saves all outputs to probe/ directory for inspection
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

# Create probe directory structure matching tests/ structure
PROBE_DIR = Path("probe")
PROBE_DIR.mkdir(exist_ok=True)
(PROBE_DIR / "unit").mkdir(exist_ok=True)
(PROBE_DIR / "e2e").mkdir(exist_ok=True)
(PROBE_DIR / "integration").mkdir(exist_ok=True)
(PROBE_DIR / "enes").mkdir(exist_ok=True)
(PROBE_DIR / "root").mkdir(exist_ok=True)

# Test suites to run (matches tests/ directory structure)
test_suites = {
    "root_readme": "tests/readme.py",  # Root level test
    "unit": "tests/unit/",
    "e2e": "tests/e2e/",
    "integration": "tests/integration/",
    "enes": "tests/enes/",
}

# Linting checks
lint_checks = {
    "black": ["black", "--check", "src", "tests"],
    "ruff": ["ruff", "check", "src/", "tests/"],
}

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results = {"timestamp": timestamp, "test_suites": {}, "lint_checks": {}, "summary": {}}

print("=" * 80)
print("COMPREHENSIVE SDK VALIDATION")
print("=" * 80)
print(f"Timestamp: {timestamp}")
print(f"Output directory: {PROBE_DIR.absolute()}")
print("=" * 80)

# Run linting checks
print("\n📋 STEP 1: LINTING CHECKS")
print("-" * 80)

for check_name, command in lint_checks.items():
    print(f"\n{check_name.upper()}:")
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)

    output_file = PROBE_DIR / f"{check_name}_{timestamp}.txt"
    output_file.write_text(result.stdout + "\n\n" + result.stderr)

    passed = result.returncode == 0
    results["lint_checks"][check_name] = {
        "passed": passed,
        "output_file": str(output_file),
        "return_code": result.returncode,
    }

    if passed:
        print("   ✅ PASSED")
    else:
        print(f"   ❌ FAILED (exit code {result.returncode})")
        print(f"   📁 Output saved to: {output_file.name}")

# Run test suites
print("\n📋 STEP 2: TEST SUITES")
print("-" * 80)

total_passed = 0
total_failed = 0

for suite_name, test_path in test_suites.items():
    print(f"\n{suite_name.upper()} TESTS:")

    result = subprocess.run(
        ["python", "-m", "pytest", test_path, "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,  # Increased timeout for readme tests
    )

    # Save to proper subdirectory
    if suite_name == "root_readme":
        output_file = PROBE_DIR / "root" / f"readme_{timestamp}.txt"
    else:
        output_file = PROBE_DIR / suite_name / f"all_{timestamp}.txt"

    output_file.write_text(result.stdout + "\n\n" + result.stderr)

    # Parse results
    output = result.stdout + result.stderr

    # Extract pass/fail counts
    import re

    match = re.search(r"(\d+) passed", output)
    passed = int(match.group(1)) if match else 0

    match = re.search(r"(\d+) failed", output)
    failed = int(match.group(1)) if match else 0

    match = re.search(r"(\d+) skipped", output)
    skipped = int(match.group(1)) if match else 0

    total_passed += passed
    total_failed += failed

    results["test_suites"][suite_name] = {
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "output_file": str(output_file),
        "return_code": result.returncode,
    }

    status = "✅ PASSED" if failed == 0 else f"❌ {failed} FAILED"
    print(f"   {status} - {passed} passed, {failed} failed, {skipped} skipped")
    print(f"   📁 Output saved to: {output_file.relative_to(Path.cwd())}")

    # Also run individual test files for detailed inspection
    if suite_name in ["unit", "e2e", "integration"]:
        test_files = Path(test_path).glob("test_*.py")
        for test_file in test_files:
            individual_result = subprocess.run(
                ["python", "-m", "pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Save individual test outputs
            individual_output = PROBE_DIR / suite_name / f"{test_file.stem}_{timestamp}.txt"
            individual_output.write_text(
                individual_result.stdout + "\n\n" + individual_result.stderr
            )

# Save summary
summary_file = PROBE_DIR / f"summary_{timestamp}.json"
results["summary"] = {
    "total_tests_passed": total_passed,
    "total_tests_failed": total_failed,
    "all_linting_passed": all(v["passed"] for v in results["lint_checks"].values()),
    "all_tests_passed": total_failed == 0,
    "overall_status": (
        "PASS"
        if (total_failed == 0 and all(v["passed"] for v in results["lint_checks"].values()))
        else "FAIL"
    ),
}

summary_file.write_text(json.dumps(results, indent=2))

# Final summary
print("\n" + "=" * 80)
print("FINAL VALIDATION SUMMARY")
print("=" * 80)

print("\n📊 TEST RESULTS:")
for suite, data in results["test_suites"].items():
    print(f"   {suite:15} {data['passed']:4} passed, {data['failed']:4} failed")

print(f"\n   TOTAL:          {total_passed:4} passed, {total_failed:4} failed")

print("\n🔍 LINTING:")
for check, data in results["lint_checks"].items():
    status = "✅ PASS" if data["passed"] else "❌ FAIL"
    print(f"   {check:15} {status}")

print(f"\n📁 All outputs saved to: {PROBE_DIR.absolute()}")
print(f"📄 Summary: {summary_file.name}")

print("\n" + "=" * 80)
if results["summary"]["overall_status"] == "PASS":
    print("🎉 ALL VALIDATIONS PASSED - SDK IS 100% WORKING")
else:
    print("⚠️  SOME VALIDATIONS FAILED - CHECK PROBE OUTPUTS")
print("=" * 80)

# Exit with appropriate code
exit(0 if results["summary"]["overall_status"] == "PASS" else 1)
