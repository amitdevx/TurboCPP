#!/bin/bash
# Test 5: Verify .gitignore is configured properly
test_gitignore() {
    echo "Test 5: Checking .gitignore configuration..."
    
    if [ ! -f ".gitignore" ]; then
        echo "❌ FAILED: .gitignore not found"
        return 1
    fi
    
    # Check for swap file rules
    if ! grep -q "\.SWP" .gitignore; then
        echo "❌ FAILED: Missing .SWP pattern"
        return 1
    fi
    
    # Check for build artifact rules
    if ! grep -q "\.OBJ" .gitignore; then
        echo "❌ FAILED: Missing .OBJ pattern"
        return 1
    fi
    
    if ! grep -q "NONAME" .gitignore; then
        echo "❌ FAILED: Missing NONAME pattern"
        return 1
    fi
    
    # Check for backup rules
    if ! grep -q "\.backup" .gitignore; then
        echo "❌ FAILED: Missing backup pattern"
        return 1
    fi
    
    # Check that TC/BIN executables are NOT ignored
    if ! grep -q "!TC/BIN/.*\.EXE" .gitignore; then
        echo "❌ FAILED: TC/BIN executables should not be ignored"
        return 1
    fi
    
    echo "✅ PASSED: .gitignore is properly configured"
    return 0
}

test_gitignore
