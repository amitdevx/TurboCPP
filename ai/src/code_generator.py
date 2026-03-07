"""
TurboCPP AI - Code Generator
TurboCPP-specific prompt engineering and code generation via OpenRouter.
"""

import logging
from .ai_providers import OpenRouterProvider

logger = logging.getLogger("turbocpp-ai")

TURBOCPP_SYSTEM_PROMPT = """You are a Turbo C++ code generation assistant. You MUST generate code that is 100% compatible with Borland Turbo C++ 3.0 running on DOSBox.

STRICT RULES:
1. Use ONLY C89/C90 standard (ANSI C). No C99+ features.
2. Use these Turbo C++ specific headers and functions:
   - #include <conio.h>   -> clrscr(), getch(), getche(), gotoxy(x,y), textcolor(), textbackground(), cprintf()
   - #include <stdio.h>   -> printf(), scanf(), gets(), puts()
   - #include <stdlib.h>  -> malloc(), free(), exit(), rand(), srand()
   - #include <string.h>  -> strlen(), strcpy(), strcmp(), strcat()
   - #include <dos.h>     -> delay(), sound(), nosound(), sleep()
   - #include <graphics.h> -> initgraph(), circle(), line(), rectangle(), closegraph()
   - #include <math.h>    -> sin(), cos(), sqrt(), pow()

3. ALWAYS use clrscr() at the start of main() to clear screen.
4. ALWAYS use getch() before return in main() so output stays visible.
5. Use void main() instead of int main() (Turbo C++ convention).
6. For graphics programs, use initgraph() with DETECT mode and path "C:\\\\TC\\\\BGI".
7. Variable declarations MUST be at the top of the block (C89 rule).
8. Use /* */ comments, not // single-line comments.

OUTPUT FORMAT:
- Return ONLY the raw C/C++ code. No explanations, no markdown.
- The code must compile and run in Turbo C++ without modifications.
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
        code = self.provider.generate_code(FULL_PROGRAM_PREFIX + user_prompt, TURBOCPP_SYSTEM_PROMPT)
        return self._clean(code)

    def generate_snippet(self, user_prompt: str, file_content: str) -> str:
        context_prompt = (
            f"Existing code in the file:\n---\n{file_content}\n---\n\n"
            f"Generate ONLY the new code to insert for: {user_prompt}\n"
            f"Do NOT repeat existing code. Make sure it integrates properly."
        )
        logger.info(f"Generating snippet: {user_prompt[:80]}...")
        code = self.provider.generate_code(context_prompt, TURBOCPP_SYSTEM_PROMPT)
        return self._clean(code)

    def _clean(self, code: str) -> str:
        if not code:
            return "/* ERROR: No code generated */"
        lines = [l for l in code.strip().split("\n") if not l.strip().startswith("```")]
        return "\n".join(lines).strip()
