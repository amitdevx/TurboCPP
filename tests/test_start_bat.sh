#!/bin/bash
# Test 3: Verify start.bat exists and has valid Windows batch syntax
test_start_bat() {
    echo "Test 3: Checking start.bat script..."
    
    if [ ! -f "start.bat" ]; then
        echo "❌ FAILED: start.bat not found"
        return 1
    fi
    
    # Check for batch shebang
    if ! head -1 start.bat | grep -q "@echo"; then
        echo "❌ FAILED: Missing batch header"
        return 1
    fi
    
    # Check for critical commands
    if ! grep -q "dosbox" start.bat; then
        echo "❌ FAILED: dosbox command not found"
        return 1
    fi
    
    if ! grep -q "mount C" start.bat; then
        echo "❌ FAILED: mount command not found"
        return 1
    fi
    
    # Check for error handling
    if ! grep -q "errorlevel" start.bat; then
        echo "❌ FAILED: No error handling found"
        return 1
    fi
    
    # Check for DOSBox path detection
    if ! grep -q "Program Files" start.bat; then
        echo "❌ FAILED: Missing DOSBox path detection"
        return 1
    fi
    
    echo "✅ PASSED: start.bat has correct structure"
    return 0
}

test_start_bat
