#!/bin/bash
# Test 4: Verify TC directory structure and critical files
test_tc_structure() {
    echo "Test 4: Checking TC directory structure..."
    
    if [ ! -d "TC" ]; then
        echo "❌ FAILED: TC directory not found"
        return 1
    fi
    
    if [ ! -f "TC/BIN/TC.EXE" ]; then
        echo "❌ FAILED: TC.EXE not found"
        return 1
    fi
    
    if [ ! -f "TC/BIN/CPP.EXE" ]; then
        echo "❌ FAILED: CPP.EXE not found"
        return 1
    fi
    
    if [ ! -d "TC/INCLUDE" ]; then
        echo "❌ FAILED: INCLUDE directory not found"
        return 1
    fi
    
    if [ ! -d "TC/LIB" ]; then
        echo "❌ FAILED: LIB directory not found"
        return 1
    fi
    
    # Verify examples exist
    if [ ! -d "TC/EXAMPLES" ]; then
        echo "❌ FAILED: EXAMPLES directory not found"
        return 1
    fi
    
    echo "✅ PASSED: TC directory structure is complete"
    return 0
}

test_tc_structure
