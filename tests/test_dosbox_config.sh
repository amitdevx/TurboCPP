#!/bin/bash
# Test 1: Verify dosbox-turbo.conf exists and has valid syntax
test_dosbox_config() {
    echo "Test 1: Checking DOSBox configuration file..."
    
    if [ ! -f "dosbox-turbo.conf" ]; then
        echo "❌ FAILED: dosbox-turbo.conf not found"
        return 1
    fi
    
    # Check for required sections
    if ! grep -q "\[cpu\]" dosbox-turbo.conf; then
        echo "❌ FAILED: Missing [cpu] section"
        return 1
    fi
    
    if ! grep -q "\[mixer\]" dosbox-turbo.conf; then
        echo "❌ FAILED: Missing [mixer] section"
        return 1
    fi
    
    # Check for cycles setting
    if ! grep -q "cycles=" dosbox-turbo.conf; then
        echo "❌ FAILED: Missing cycles setting"
        return 1
    fi
    
    echo "✅ PASSED: dosbox-turbo.conf is valid"
    return 0
}

test_dosbox_config
