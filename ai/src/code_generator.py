"""
TurboCPP AI - Code Generator
TurboCPP-specific prompt engineering and code generation via OpenRouter.
Includes C89 compliance validation to catch common errors.
"""

import re
import logging
from .ai_providers import OpenRouterProvider

logger = logging.getLogger("turbocpp-ai")


def validate_c89_compliance(code: str) -> tuple:
    """
    Validates code for C89 compliance. Returns (is_valid, errors_list).
    Catches common C89 violations that Turbo C++ would reject.
    """
    errors = []
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Check 1: Variable declaration after statements in a block
        # This is the MOST COMMON error - detect type declarations not at block start
        if re.search(r'^\s+(int|char|float|double|long|short|unsigned|struct|void\s*\*)\s+\w+\s*[=;]', line):
            # Check if there were non-declaration statements before in this block
            # Look backwards to find the block start (opening brace)
            block_start = None
            brace_depth = 0
            for j in range(i-1, -1, -1):
                if '{' in lines[j]:
                    block_start = j + 1
                    break
            
            if block_start is not None and block_start < i - 1:
                # Check if there are statements between block start and this declaration
                has_statement_before = False
                for k in range(block_start, i-1):
                    stmt = lines[k].strip()
                    if stmt and not stmt.startswith('/*') and not stmt.startswith('*') and not stmt.endswith('*/'):
                        # It's a statement, not a comment
                        if not re.match(r'^(int|char|float|double|long|short|unsigned|struct|typedef|void)', stmt):
                            # Found a non-declaration statement before this declaration
                            has_statement_before = True
                            break
                
                if has_statement_before:
                    errors.append(f"Line {i}: Declaration after statements (C89 violation) - '{line_stripped[:50]}'")
        
        # Check 2: for loop with declaration inside
        if re.search(r'for\s*\(\s*(int|char|float|double|long|short|unsigned)\s+\w+', line):
            errors.append(f"Line {i}: Loop variable declared in for() - C99+ only - '{line_stripped[:50]}'")
        
        # Check 3: // comments (C99+)
        if '//' in line and not line.strip().startswith('/*'):
            # Make sure it's not in a string
            if '"' not in line or line.index('//') < line.index('"'):
                errors.append(f"Line {i}: Single-line // comment not allowed (use /* */)")
        
        # Check 4: bool type (not in C89)
        if re.search(r'\b(bool|true|false)\b', line) and '#include' not in line:
            errors.append(f"Line {i}: bool/true/false not in C89 (use int with 1/0)")
        
        # Check 5: int main() with return (should be void main())
        if re.search(r'int\s+main\s*\(', line):
            errors.append(f"Line {i}: Use 'void main()' for Turbo C++, not 'int main()'")
    
    return (len(errors) == 0, errors)


def fix_c89_violations(code: str) -> str:
    """
    Attempts to automatically fix common C89 violations.
    Moves declarations to the top of blocks.
    """
    lines = code.split('\n')
    fixed_lines = []
    current_block_decls = []
    in_function = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()
        
        # Detect function start
        if re.match(r'(void|int)\s+\w+\s*\([^)]*\)\s*{', line_stripped):
            in_function = True
            fixed_lines.append(line)
            current_block_decls = []
            i += 1
            
            # Collect all declarations at the top of the block
            j = i
            while j < len(lines):
                next_line = lines[j].strip()
                
                # If it's a declaration, collect it
                if re.match(r'^(int|char|float|double|long|short|unsigned|struct)\s+\w+', next_line):
                    current_block_decls.append(lines[j])
                    j += 1
                # If it's a non-declaration, stop collecting
                elif next_line and not next_line.startswith('/*') and not next_line.startswith('*'):
                    break
                else:
                    j += 1
            
            # Output all collected declarations
            for decl in current_block_decls:
                fixed_lines.append(decl)
            
            i = j
            continue
        
        fixed_lines.append(line)
        i += 1
    
    return '\n'.join(fixed_lines)


TURBOCPP_SYSTEM_PROMPT = """You are a Turbo C++ code generation assistant for Borland Turbo C++ 3.0 (1992).
You MUST generate code that compiles EXACTLY as written in Turbo C++ 3.0 on DOSBox.

═══════════════════════════════════════════════════════════════
🚨 CRITICAL ERROR TO AVOID 🚨
═══════════════════════════════════════════════════════════════

THIS IS THE #1 ERROR IN TURBO C++:
"Declaration is not allowed here"

CAUSE: Variable declared AFTER statements in a block.

TURBO C++ REJECTS:
    printf("hello");
    int x = 5;        /* ❌ ERROR: Declaration after statement! */

TURBO C++ REQUIRES:
    int x;            /* ✅ Declaration at top */
    
    printf("hello");
    x = 5;            /* ✅ Assignment after declarations */

═══════════════════════════════════════════════════════════════
CRITICAL: C89/ANSI C RULES (1989 standard) - NO MODERN C/C++!
═══════════════════════════════════════════════════════════════

1. VARIABLE DECLARATIONS - MOST IMPORTANT RULE:
   ✓ ALL variables MUST be declared at the VERY TOP of each block/function
   ✓ ALL declarations BEFORE ANY statements (printf, scanf, if, for, etc.)
   ✗ NEVER declare variables after ANY executable statement
   ✗ NEVER use mixed declarations and statements
   ✗ NEVER declare inside a case: block without extra braces
   
   CORRECT PATTERN (ALWAYS USE THIS):
   void main() {
       /* Step 1: ALL DECLARATIONS FIRST - nothing else! */
       int i, sum, count;
       float avg, result;
       char name[50], choice;
       Node *ptr, *temp;
       
       /* Step 2: NOW executable statements */
       clrscr();
       sum = 0;
       printf("Enter name: ");
       scanf("%s", name);
       
       for(i=0; i<10; i++) {
           /* ... */
       }
   }
   
   WRONG PATTERNS (WILL CAUSE ERRORS):
   void main() {
       clrscr();               /* Statement */
       int i = 0;              /* ❌ ERROR: Declaration after statement! */
       
       printf("...");
       float avg = 0.0;        /* ❌ ERROR: Declaration in middle! */
       
       scanf("%d", &num);
       Node *result = search(); /* ❌ ERROR: Common mistake! */
   }
   
   NESTED BLOCKS - SAME RULE:
   if(condition) {
       int x, y;    /* ✅ At top of block */
       
       x = 5;       /* ✅ Statements after */
       printf("%d", x);
   }
   
   SWITCH CASE - BE CAREFUL:
   switch(choice) {
       case 1: {
           int x;         /* ✅ Need braces + declaration at top */
           x = 10;
           break;
       }
       case 2:
           printf("...");
           int y = 5;     /* ❌ ERROR: Can't declare without braces! */
   }

       float avg = 0.0;  /* ERROR: in middle! */
   }

2. FOR LOOP VARIABLES:
   ✓ Declare loop counters at the TOP of function
   ✗ NEVER declare inside for() statement
   
   CORRECT:
   int i;
   for(i=0; i<10; i++) { ... }
   
   WRONG:
   for(int i=0; i<10; i++) { ... }  /* C99+ only! */

3. FUNCTION SIGNATURES:
   ✓ Use void main() - Turbo C++ convention
   ✗ Do NOT use int main() or return statements in main
   ✓ Declare all functions before main() or use prototypes
   
   CORRECT:
   void main() {
       /* ... */
       getch();
   }
   
   WRONG:
   int main() {
       /* ... */
       return 0;
   }

4. COMMENTS:
   ✓ Use /* block comments */ ONLY
   ✗ NEVER use // single-line comments (C99+ only)
   
   CORRECT: /* This is a comment */
   WRONG:   // This is wrong

5. STRING LITERALS:
   ✓ Use double quotes for strings: "hello"
   ✓ Use single quotes for chars: 'a'
   ✗ No string concatenation at compile time
   
6. STANDARD I/O:
   ✓ scanf() needs & for addresses: scanf("%d", &num);
   ✓ printf() format: %d (int), %f (float), %c (char), %s (string)
   ✓ Use gets() for strings (yes, even though it's unsafe - Turbo C++ era)
   ✗ No fgets() - not common in Turbo C++ code

7. MEMORY & TYPES:
   ✓ Use int, char, float, double, long, short only
   ✗ No bool, true, false (use int with 1/0)
   ✗ No stdint.h types (int32_t, uint8_t, etc.)
   ✗ No size_t in user code (use int/long)
   ✓ NULL is defined, use it for pointers

═══════════════════════════════════════════════════════════════
TURBO C++ SPECIFIC LIBRARIES
═══════════════════════════════════════════════════════════════

#include <conio.h>    /* Console I/O */
  - clrscr()          /* Clear screen - MUST be first in main() */
  - getch()           /* Wait for keypress - MUST be last in main() */
  - getche()          /* Get char with echo */
  - gotoxy(x,y)       /* Move cursor to column x, row y */
  - textcolor(color)  /* Set text color (0-15) */
  - textbackground(c) /* Set bg color */
  - cprintf("...")    /* Colored printf */

#include <stdio.h>    /* Standard I/O */
  - printf(), scanf()
  - gets(), puts()
  - sprintf(), sscanf()

#include <stdlib.h>   /* Utilities */
  - malloc(), free(), calloc(), realloc()
  - exit(0)
  - rand(), srand()
  - atoi(), atof()

#include <string.h>   /* String functions */
  - strlen(), strcpy(), strcmp()
  - strcat(), strchr(), strstr()

#include <math.h>     /* Math functions */
  - sqrt(), pow(), sin(), cos(), tan()
  - fabs(), ceil(), floor()

#include <dos.h>      /* DOS functions */
  - delay(milliseconds) /* Pause execution */
  - sound(frequency)    /* Beep sound */
  - nosound()          /* Stop sound */

#include <graphics.h> /* Graphics mode */
  int gd=DETECT, gm;
  initgraph(&gd, &gm, "C:\\\\TC\\\\BGI");
  /* then: circle(), line(), rectangle(), etc. */
  closegraph();

═══════════════════════════════════════════════════════════════
MANDATORY PROGRAM STRUCTURE
═══════════════════════════════════════════════════════════════

EVERY FULL PROGRAM MUST FOLLOW THIS TEMPLATE:

#include <stdio.h>
#include <conio.h>
/* other includes as needed */

void main()
{
    /* Declare ALL variables HERE at top */
    int i, num;
    float result;
    char name[50];
    
    clrscr();  /* ALWAYS first statement */
    
    /* Your code logic here */
    printf("Enter number: ");
    scanf("%d", &num);
    
    /* ... rest of logic ... */
    
    getch();  /* ALWAYS last statement before closing brace */
}

═══════════════════════════════════════════════════════════════
EXAMPLES OF CORRECT TURBO C++ CODE
═══════════════════════════════════════════════════════════════

EXAMPLE 1: Simple input/output
#include <stdio.h>
#include <conio.h>

void main()
{
    int num, square;
    
    clrscr();
    printf("Enter a number: ");
    scanf("%d", &num);
    
    square = num * num;
    printf("Square is: %d", square);
    
    getch();
}

EXAMPLE 2: Array with loop
#include <stdio.h>
#include <conio.h>

void main()
{
    int arr[10], i, sum;
    
    clrscr();
    sum = 0;
    
    printf("Enter 10 numbers:\\n");
    for(i=0; i<10; i++) {
        scanf("%d", &arr[i]);
        sum = sum + arr[i];
    }
    
    printf("Sum = %d", sum);
    getch();
}

EXAMPLE 3: Switch case menu
#include <stdio.h>
#include <conio.h>

void main()
{
    int choice;
    float a, b, result;
    
    clrscr();
    
    printf("1. Add\\n2. Subtract\\n3. Exit\\n");
    printf("Enter choice: ");
    scanf("%d", &choice);
    
    switch(choice) {
        case 1:
            printf("Enter two numbers: ");
            scanf("%f %f", &a, &b);
            result = a + b;
            printf("Result: %f", result);
            break;
        case 2:
            printf("Enter two numbers: ");
            scanf("%f %f", &a, &b);
            result = a - b;
            printf("Result: %f", result);
            break;
        default:
            printf("Invalid choice");
    }
    
    getch();
}

═══════════════════════════════════════════════════════════════
OUTPUT REQUIREMENTS
═══════════════════════════════════════════════════════════════

✓ Return ONLY raw C code - no explanations, no markdown, no backticks
✓ Code must compile without errors in Turbo C++ 3.0
✓ Code must run correctly on DOSBox
✗ Do NOT include any modern C++ features
✗ Do NOT use C99/C11/C17 features
✗ Do NOT add comments explaining the code (unless specifically asked)

Remember: You are coding for a 1992 compiler. Think like a 1990s programmer!
"""

FULL_PROGRAM_PREFIX = """Generate a COMPLETE Turbo C++ program for the following request.
Include all necessary #include headers, void main(), clrscr(), and getch().

Request: """

SNIPPET_PREFIX = """Generate ONLY a Turbo C++ code snippet (NOT a full program) for the following.
Output only the relevant code lines — no #include, no main() function.

Request: """


class CodeGenerator:
    """Generates TurboCPP-compatible code using OpenRouter."""

    def __init__(self, provider: OpenRouterProvider):
        self.provider = provider

    def generate_full_program(self, user_prompt: str) -> str:
        logger.info(f"Generating full program: {user_prompt[:80]}...")
        
        # Detect complexity from prompt
        complexity = "simple"
        complex_keywords = ["menu", "tree", "linked list", "graph", "sorting", "search tree",
                           "operations", "traversal", "recursive", "multiple functions", "bst", "binary"]
        if any(kw in user_prompt.lower() for kw in complex_keywords):
            complexity = "complex"
            logger.info(f"Detected complex program request, using extended token limit")
        
        code = self.provider.generate_code(FULL_PROGRAM_PREFIX + user_prompt, TURBOCPP_SYSTEM_PROMPT, complexity=complexity)
        code = self._clean(code)
        
        # Validate and fix C89 compliance
        is_valid, errors = validate_c89_compliance(code)
        if not is_valid:
            logger.warning(f"C89 violations detected: {errors}")
            logger.info("Attempting to auto-fix C89 violations...")
            code = fix_c89_violations(code)
            
            # Re-validate
            is_valid, errors = validate_c89_compliance(code)
            if not is_valid:
                logger.error(f"C89 violations remain after fix: {errors}")
                # Add comment about violations
                error_comment = "\n/* WARNING: C89 compliance issues detected:\n"
                for err in errors[:3]:  # Show first 3 errors
                    error_comment += f" * {err}\n"
                error_comment += " * Fix: Move ALL variable declarations to top of blocks.\n */\n\n"
                code = error_comment + code
        
        return code

    def generate_snippet(self, user_prompt: str, file_content: str) -> str:
        context_prompt = (
            f"Existing code in the file:\n---\n{file_content}\n---\n\n"
            f"Generate ONLY the new code to insert for: {user_prompt}\n"
            f"Do NOT repeat existing code. Make sure it integrates properly."
        )
        logger.info(f"Generating snippet: {user_prompt[:80]}...")
        code = self.provider.generate_code(context_prompt, TURBOCPP_SYSTEM_PROMPT)
        code = self._clean(code)
        
        # Validate C89 compliance
        is_valid, errors = validate_c89_compliance(code)
        if not is_valid:
            logger.warning(f"C89 violations in snippet: {errors}")
            code = fix_c89_violations(code)
        
        return code

    def _clean(self, code: str) -> str:
        if not code:
            return "/* ERROR: No code generated */"
        lines = [l for l in code.strip().split("\n") if not l.strip().startswith("```")]
        return "\n".join(lines).strip()
