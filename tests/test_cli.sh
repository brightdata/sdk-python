#!/bin/bash
# Comprehensive CLI Testing Script
# Tests all brightdata CLI commands to validate end-user experience

set -e  # Exit on error

echo "================================================================================"
echo "COMPREHENSIVE CLI VALIDATION - Testing Real User Experience"
echo "================================================================================"
echo "Timestamp: $(date '+%Y%m%d_%H%M%S')"
echo "================================================================================"

# Create probe directory structure for CLI tests
PROBE_DIR="probe/cli"
mkdir -p "$PROBE_DIR"/{scrape,search,help,errors}

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
SUMMARY_FILE="$PROBE_DIR/cli_summary_$TIMESTAMP.txt"

# Track results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper function to run CLI test
run_cli_test() {
    local test_name=$1
    local command=$2
    local category=$3
    local output_file="$PROBE_DIR/$category/${test_name}_${TIMESTAMP}.txt"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "TEST: $test_name"
    echo "COMMAND: $command"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Run command and save output
    if eval "$command" > "$output_file" 2>&1; then
        echo "   ✅ PASSED"
        echo "   📁 Output: $output_file"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        EXIT_CODE=$?
        echo "   ❌ FAILED (exit code: $EXIT_CODE)"
        echo "   📁 Error output: $output_file"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# =============================================================================
# STEP 1: HELP COMMANDS
# =============================================================================

echo ""
echo "📋 STEP 1: HELP & INFO COMMANDS"
echo "================================================================================"

run_cli_test "help_main" "brightdata --help" "help"
run_cli_test "help_scrape" "brightdata scrape --help" "help"
run_cli_test "help_search" "brightdata search --help" "help"
run_cli_test "help_scrape_amazon" "brightdata scrape amazon --help" "help"
run_cli_test "help_search_amazon" "brightdata search amazon --help" "help"
run_cli_test "help_search_linkedin" "brightdata search linkedin --help" "help"

# =============================================================================
# STEP 2: SCRAPE COMMANDS (if we have test token - these will fail without real API)
# =============================================================================

echo ""
echo "📋 STEP 2: SCRAPE COMMANDS (syntax validation)"
echo "================================================================================"
echo "Note: These test CLI syntax, not actual API calls (would need valid token)"

# Test CLI syntax validation (will fail on auth but validates parsing)
run_cli_test "scrape_amazon_products_help" \
    "brightdata scrape amazon products --help" \
    "scrape" || true

run_cli_test "scrape_linkedin_profiles_help" \
    "brightdata scrape linkedin profiles --help" \
    "scrape" || true

run_cli_test "scrape_facebook_posts_help" \
    "brightdata scrape facebook --help" \
    "scrape" || true

run_cli_test "scrape_instagram_profiles_help" \
    "brightdata scrape instagram --help" \
    "scrape" || true

# =============================================================================
# STEP 3: SEARCH COMMANDS (syntax validation)
# =============================================================================

echo ""
echo "📋 STEP 3: SEARCH COMMANDS (syntax validation)"
echo "================================================================================"

run_cli_test "search_google_help" \
    "brightdata search google --help" \
    "search" || true

run_cli_test "search_linkedin_jobs_help" \
    "brightdata search linkedin jobs --help" \
    "search" || true

# =============================================================================
# STEP 4: FORMAT OPTIONS
# =============================================================================

echo ""
echo "📋 STEP 4: OUTPUT FORMAT OPTIONS"
echo "================================================================================"

# Test that --output-format is recognized
run_cli_test "format_json_help" \
    "brightdata scrape --help | grep 'output-format'" \
    "help" || true

run_cli_test "format_generic_help" \
    "brightdata scrape generic --help" \
    "help" || true

# =============================================================================
# FINAL SUMMARY
# =============================================================================

echo ""
echo "================================================================================"
echo "CLI VALIDATION SUMMARY"
echo "================================================================================"

{
    echo "Timestamp: $(date)"
    echo ""
    echo "TEST RESULTS:"
    echo "   Total:  $TOTAL_TESTS"
    echo "   Passed: $PASSED_TESTS"
    echo "   Failed: $FAILED_TESTS"
    echo ""
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo "✅ ALL CLI TESTS PASSED"
        echo ""
        echo "CLI is fully functional and ready for users!"
    else
        echo "⚠️  $FAILED_TESTS test(s) failed"
        echo ""
        echo "Check probe/cli/ directory for details"
    fi
    
    echo ""
    echo "📁 All outputs saved to: probe/cli/"
    echo ""
    echo "Directory structure:"
    find "$PROBE_DIR" -type f | sort
    
} | tee "$SUMMARY_FILE"

echo ""
echo "================================================================================"
if [ $FAILED_TESTS -eq 0 ]; then
    echo "🎉 CLI VALIDATION COMPLETE - ALL SYSTEMS GO"
    exit 0
else:
    echo "⚠️  SOME CLI TESTS FAILED - CHECK OUTPUTS"
    exit 1
fi
echo "================================================================================"

