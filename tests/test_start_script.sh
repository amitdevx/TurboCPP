#!/bin/bash
# Test 2: Verify start.sh has proper structure and is executable
test_start_script() {
    echo "Test 2: Checking start.sh script..."
    
    if [ ! -f "start.sh" ]; then
        echo "❌ FAILED: start.sh not found"
        return 1
    fi
    
    if [ ! -x "start.sh" ]; then
        echo "❌ FAILED: start.sh is not executable"
        return 1
    fi
    
    # Check for shebang
    if ! head -1 start.sh | grep -q "#!/bin/bash"; then
        echo "❌ FAILED: Missing bash shebang"
        return 1
    fi
    
    # Check for critical commands
    if ! grep -q "dosbox" start.sh; then
        echo "❌ FAILED: dosbox command not found"
        return 1
    fi
    
    if ! grep -q "mount C" start.sh; then
        echo "❌ FAILED: mount command not found"
        return 1
    fi
    
    # Check mount path is quoted (handles spaces) - can have escaped quotes
    if ! grep -q 'mount C' start.sh || ! grep -q '\\"' start.sh; then
        echo "❌ FAILED: Mount path not properly quoted"
        return 1
    fi
    
    echo "✅ PASSED: start.sh has correct structure"
    return 0
}

test_start_script
