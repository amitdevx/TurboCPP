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
    Validates code for C89/ANSI C compliance for Turbo C++ 3.0.
    Returns (is_valid, errors_list).
    
    CRITICAL: Detects "Declaration is not allowed here" errors.
    Turbo C++ requires ALL declarations at the top of EVERY block, including:
    - Function bodies
    - if/else blocks
    - while/for/do-while blocks
    - switch blocks
    - case blocks (IMPORTANT!)
    """
    errors = []
    lines = code.split('\n')
    
    # Track block state machine
    block_states = {}  # {line_num: {'type': 'function/case/if/etc', 'has_statement': bool}}
    current_blocks = []  # Stack of block start lines
    in_case_block = False
    case_start_line = None
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # Skip empty lines, preprocessor, and pure comments
        if not line_stripped or line_stripped.startswith('#'):
            continue
        if line_stripped.startswith('/*') or line_stripped.startswith('*') or line_stripped == '*/':
            continue
        
        # Check 3: // comments (C99+)
        if '//' in line and not line.strip().startswith('/*'):
            if '"' not in line or ('"' in line and line.index('//') < line.find('"')):
                errors.append(f"Line {i}: Single-line // comment not allowed (use /* */)")
        
        # Check 4: bool type (not in C89)
        if re.search(r'\b(bool|true|false)\b', line) and '#include' not in line:
            errors.append(f"Line {i}: bool/true/false not in C89 (use int with 1/0)")
        
        # Check 5: int main() 
        if re.search(r'int\s+main\s*\(', line):
            errors.append(f"Line {i}: Use 'void main()' for Turbo C++, not 'int main()'")
        
        # Check 2: for loop with declaration inside
        if re.search(r'for\s*\(\s*(int|char|float|double|long|short|unsigned)\s+\w+', line):
            errors.append(f"Line {i}: Loop variable declared in for() - C99+ only - '{line_stripped[:60]}'")
        
        # Track case blocks (special handling needed)
        if re.match(r'case\s+.*:', line_stripped) or line_stripped.startswith('default:'):
            in_case_block = True
            case_start_line = i
            current_blocks.append({'line': i, 'type': 'case', 'has_statement': False})
            continue
        
        # Track break/return ending case blocks
        if in_case_block and (line_stripped == 'break;' or line_stripped.startswith('return')):
            in_case_block = False
            if current_blocks and current_blocks[-1]['type'] == 'case':
                current_blocks.pop()
        
        # Track opening braces (function/if/while/for blocks)
        if '{' in line:
            # Determine block type
            block_type = 'block'
            if 'if' in line or 'else' in line:
                block_type = 'if'
            elif 'while' in line:
                block_type = 'while'
            elif 'for' in line:
                block_type = 'for'
            elif 'switch' in line:
                block_type = 'switch'
            elif re.search(r'\w+\s*\([^)]*\)\s*{', line):  # function
                block_type = 'function'
            
            current_blocks.append({'line': i, 'type': block_type, 'has_statement': False})
        
        # Track closing braces
        if '}' in line:
            if current_blocks:
                current_blocks.pop()
        
        # Detect if this line is a DECLARATION
        is_declaration = False
        # Standard C89 types
        declaration_pattern = r'^(int|char|float|double|long|short|unsigned|signed|struct\s+\w+|typedef)\s+[\w*]+\s*[;=\[]'
        if re.match(declaration_pattern, line_stripped):
            is_declaration = True
        
        # User-defined types with pointers: TreeNode *foundNode = ...
        if re.match(r'^[A-Z]\w+\s+\*\w+\s*[;=]', line_stripped):
            is_declaration = True
        
        # Typedef'd types: Node *ptr = ...
        if re.match(r'^\w+\s+\*\w+\s*=', line_stripped):
            is_declaration = True
        
        # Detect if this line is a STATEMENT (not a declaration)
        is_statement = False
        statement_keywords = ['printf', 'scanf', 'clrscr', 'getch', 'free', 'malloc', 
                             'exit', 'return', 'if', 'while', 'for', 'switch', 
                             'break', 'continue', 'goto']
        
        # Assignment to existing variable (not declaration)
        if re.match(r'^\w+\s*=', line_stripped) and not is_declaration:
            is_statement = True
        
        # Function calls
        if any(kw in line_stripped for kw in statement_keywords):
            is_statement = True
        
        # Increment/decrement
        if re.search(r'\w+\s*(\+\+|--|[\+\-\*/]=)', line_stripped):
            is_statement = True
        
        # Check 1: CRITICAL - Declaration after statement in ANY block
        if is_declaration and current_blocks:
            # Check if any current block has seen a statement
            for block in current_blocks:
                if block['has_statement']:
                    block_type = block['type']
                    errors.append(f"Line {i}: Declaration after statements in {block_type} block (C89 violation) - '{line_stripped[:60]}'")
                    break
        
        # Mark blocks as having seen statements
        if is_statement and current_blocks:
            for block in current_blocks:
                block['has_statement'] = True
    
    return (len(errors) == 0, errors)


def fix_c89_violations(code: str) -> str:
    """
    Automatically fixes C89 violations by moving declarations to block tops.
    
    Handles:
    1. Function blocks - moves all declarations to function start
    2. Switch case blocks - moves declarations to case label
    3. if/else/while/for blocks - moves declarations to block start
    4. // comments - converts to /* */
    5. typedef struct pointers - recognizes user-defined types
    """
    lines = code.split('\n')
    fixed_lines = []
    
    # First pass: Convert // comments to /* */
    for i, line in enumerate(lines):
        if '//' in line and not line.strip().startswith('/*'):
            # Find the // position
            comment_pos = line.find('//')
            before = line[:comment_pos]
            comment = line[comment_pos+2:].strip()
            if comment:
                lines[i] = before + '/* ' + comment + ' */'
            else:
                lines[i] = before
    
    # Second pass: Fix declarations after statements
    i = 0
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()
        
        # Detect function start
        if re.match(r'(void|int|char|float|double)\s+\w+\s*\([^)]*\)\s*\{', line_stripped):
            fixed_lines.append(line)
            i += 1
            
            # Collect ALL lines in this function
            function_lines = []
            declarations = []
            statements = []
            brace_depth = 1
            
            while i < len(lines) and brace_depth > 0:
                func_line = lines[i]
                func_stripped = func_line.strip()
                
                # Track braces
                brace_depth += func_line.count('{') - func_line.count('}')
                
                if brace_depth == 0:
                    # Closing brace of function
                    break
                
                # Skip empty lines and comments at the start
                if not func_stripped or func_stripped.startswith('/*') or func_stripped.startswith('*'):
                    function_lines.append(func_line)
                    i += 1
                    continue
                
                # Detect declarations (including typedefs like TreeNode *ptr)
                is_decl = False
                # Standard types
                if re.match(r'^(int|char|float|double|long|short|unsigned|signed|struct\s+\w+)\s+[\w*]+\s*[;=\[]', func_stripped):
                    is_decl = True
                # User-defined types (TreeNode *ptr, Node *next, etc.)
                elif re.match(r'^[A-Z]\w+\s+\*\w+\s*[;=]', func_stripped):
                    is_decl = True
                elif re.match(r'^\w+\s+\*\w+\s*=', func_stripped):
                    is_decl = True
                
                if is_decl and not statements:
                    # Declaration at top is fine
                    declarations.append(func_line)
                elif is_decl and statements:
                    # Declaration after statement - needs fixing
                    # Extract just the declaration part (before =)
                    if '=' in func_stripped:
                        # Split into declaration and initialization
                        match = re.match(r'^(.+?)\s*=\s*(.+);?\s*$', func_stripped)
                        if match:
                            decl_part = match.group(1) + ';'
                            init_part = match.group(2).rstrip(';')
                            var_name = re.search(r'(\w+)\s*$', match.group(1))
                            if var_name:
                                var = var_name.group(1)
                                # Add declaration to top
                                indent = len(func_line) - len(func_line.lstrip())
                                declarations.append(' ' * indent + decl_part)
                                # Add assignment as statement
                                statements.append(' ' * indent + var + ' = ' + init_part + ';')
                    else:
                        # Just a declaration, move to top
                        declarations.append(func_line)
                else:
                    # It's a statement
                    statements.append(func_line)
                
                i += 1
            
            # Output declarations first, then blank line, then statements
            for decl in declarations:
                fixed_lines.append(decl)
            
            if declarations and statements:
                fixed_lines.append('')  # Blank line after declarations
            
            for stmt in statements:
                fixed_lines.append(stmt)
            
            # Add the closing brace
            if i < len(lines):
                fixed_lines.append(lines[i])
                i += 1
            
            continue
        
        # Handle switch cases specially
        elif line_stripped.startswith('case ') or line_stripped.startswith('default:'):
            fixed_lines.append(line)
            i += 1
            
            # Collect lines in this case until break
            case_declarations = []
            case_statements = []
            
            while i < len(lines):
                case_line = lines[i]
                case_stripped = case_line.strip()
                
                # End of case
                if case_stripped == 'break;' or case_stripped.startswith('return') or case_stripped.startswith('case ') or case_stripped.startswith('default:'):
                    # Output collected declarations, then statements
                    for decl in case_declarations:
                        fixed_lines.append(decl)
                    for stmt in case_statements:
                        fixed_lines.append(stmt)
                    
                    if case_stripped == 'break;' or case_stripped.startswith('return'):
                        fixed_lines.append(case_line)
                        i += 1
                    break
                
                # Check if it's a declaration
                is_case_decl = False
                if re.match(r'^(int|char|float|double|long|short|unsigned|struct\s+\w+)\s+[\w*]+\s*[;=]', case_stripped):
                    is_case_decl = True
                elif re.match(r'^[A-Z]\w+\s+\*\w+\s*[;=]', case_stripped):
                    is_case_decl = True
                elif re.match(r'^\w+\s+\*\w+\s*=', case_stripped):
                    is_case_decl = True
                
                if is_case_decl:
                    # Move to case declarations
                    if '=' in case_stripped:
                        # Split declaration and initialization
                        match = re.match(r'^(.+?)\s*=\s*(.+);?\s*$', case_stripped)
                        if match:
                            decl_part = match.group(1) + ';'
                            init_part = match.group(2).rstrip(';')
                            var_name = re.search(r'(\w+)\s*$', match.group(1))
                            if var_name:
                                var = var_name.group(1)
                                indent = len(case_line) - len(case_line.lstrip())
                                case_declarations.append(' ' * indent + decl_part)
                                case_statements.append(' ' * indent + var + ' = ' + init_part + ';')
                    else:
                        case_declarations.append(case_line)
                else:
                    case_statements.append(case_line)
                
                i += 1
            
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
