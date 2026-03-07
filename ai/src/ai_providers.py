"""
TurboCPP AI - OpenRouter API Provider
Uses OpenRouter (openrouter.ai) for AI code generation.
Free tier: 50 requests/day, 20 requests/minute.
Uses models with :free suffix for free access.
Auto-discovers available models and retries on rate limits.
"""

import logging
import time
import requests

logger = logging.getLogger("turbocpp-ai")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

# Cache for discovered models (avoid repeated API calls)
_model_cache = {"models": [], "timestamp": 0, "ttl": 3600}  # 1 hour TTL (was 5 min)


def fetch_free_models():
    """Fetch available free models from OpenRouter API."""
    now = time.time()
    if _model_cache["models"] and (now - _model_cache["timestamp"]) < _model_cache["ttl"]:
        return _model_cache["models"]

    try:
        resp = requests.get(OPENROUTER_MODELS_URL, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            free = []
            for m in data.get("data", []):
                mid = m.get("id", "")
                if ":free" in mid:
                    free.append({
                        "id": mid,
                        "name": m.get("name", mid),
                        "context_length": m.get("context_length", 0),
                    })
            # Sort: prefer larger context and well-known providers
            free.sort(key=lambda x: x["context_length"], reverse=True)
            _model_cache["models"] = free
            _model_cache["timestamp"] = now
            logger.info(f"Discovered {len(free)} free models on OpenRouter")
            return free
    except Exception as e:
        logger.warning(f"Could not fetch models from OpenRouter: {e}")

    return _model_cache["models"]  # return stale cache if available


def get_free_model_ids():
    """Get just the model IDs of available free models."""
    return [m["id"] for m in fetch_free_models()]


class OpenRouterProvider:
    """OpenRouter API handler — OpenAI-compatible REST API with auto-retry."""

    def __init__(self, config: dict):
        self.api_key = config.get("openrouter_api_key", "")
        self.model = config.get("model", "meta-llama/llama-3.3-70b-instruct:free")
        self.max_tokens = config.get("max_tokens", 4096)  # Increased default for complex programs
        self.temperature = config.get("temperature", 0.5)  # Better for complex logic
        self.timeout = config.get("timeout", 90)  # Increased for complex prompts

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def get_name(self) -> str:
        return f"OpenRouter ({self.model})"
    
    def estimate_tokens(self, prompt: str, system_prompt: str) -> int:
        """Estimate tokens needed (rough: 1 token ≈ 4 chars)."""
        total_chars = len(prompt) + len(system_prompt)
        return total_chars // 4

    def _try_generate(self, model: str, prompt: str, system_prompt: str, max_tokens_override: int = None, temp_override: float = None) -> tuple:
        """Attempt generation with a specific model. Returns (success, result)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/amitdevx/TurboC-",
            "X-Title": "TurboCPP AI",
        }
        
        max_tokens = max_tokens_override or self.max_tokens
        temperature = temp_override or self.temperature
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=self.timeout)
        except requests.exceptions.Timeout:
            return False, f"timeout ({model})"
        except requests.exceptions.ConnectionError:
            return False, f"connection error ({model})"
        except Exception as e:
            return False, f"request error: {e}"

        # Some models don't support system prompts — retry with combined user message
        if resp.status_code == 400 and "not enabled" in resp.text.lower():
            payload["messages"] = [
                {"role": "user", "content": f"{system_prompt}\n\n{prompt}"},
            ]
            try:
                resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=self.timeout)
            except Exception:
                return False, f"system prompt fallback failed ({model})"

        if resp.status_code == 200:
            try:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                code = self._extract_code(content)
                # Reject empty or too-short responses (allow tiny snippets)
                if not code or len(code.strip()) < 5:
                    return False, f"empty response ({model})"
                return True, code
            except (KeyError, IndexError, ValueError) as e:
                return False, f"invalid response format ({model}): {e}"
        elif resp.status_code == 429:
            return False, f"rate-limited ({model})"
        elif resp.status_code == 404:
            return False, f"not found ({model})"
        else:
            error_msg = resp.text[:200]
            return False, f"API {resp.status_code}: {error_msg}"

    def generate_code(self, prompt: str, system_prompt: str, complexity: str = "medium") -> str:
        """
        Generate code with automatic complexity-based token scaling.
        
        Args:
            prompt: User's code generation request
            system_prompt: System instructions for the AI
            complexity: "simple", "medium", or "complex" - auto-adjusts max_tokens
        
        Returns:
            Generated code string
        """
        # Auto-scale max_tokens based on complexity
        token_scale = {
            "simple": self.max_tokens,  # Use configured default
            "medium": max(self.max_tokens, 4096),  # At least 4096
            "complex": max(self.max_tokens, 6144),  # At least 6144 for BST, menus, etc.
        }
        max_tokens = token_scale.get(complexity, self.max_tokens)
        
        # Detect complexity from prompt keywords if not explicitly set
        if complexity == "medium":
            complex_keywords = ["menu", "tree", "linked list", "graph", "sorting", "search", 
                              "operations", "traversal", "recursive", "multiple functions"]
            if any(kw in prompt.lower() for kw in complex_keywords):
                max_tokens = token_scale["complex"]
                logger.info(f"Detected complex prompt, using max_tokens={max_tokens}")
        
        try:
            # First try the configured model
            success, result = self._try_generate(self.model, prompt, system_prompt, max_tokens_override=max_tokens)
            if success:
                return result

            logger.warning(f"Primary model failed: {result}. Trying fallbacks...")

            # Priority fallback list based on reliability and speed
            priority_models = [
                "stepfun/step-3.5-flash:free",  # Proven working in user logs
                "qwen/qwen3-4b:free",  # Fast, small
                "google/gemma-3-12b-it:free",
                "meta-llama/llama-3.2-3b-instruct:free",
                "nvidia/nemotron-nano-9b-v2:free",
            ]
            
            # Auto-fallback: try priority models first, then others
            all_fallbacks = get_free_model_ids()
            fallback_models = []
            for model in priority_models:
                if model in all_fallbacks and model != self.model:
                    fallback_models.append(model)
            # Add remaining models
            for model in all_fallbacks:
                if model not in fallback_models and model != self.model:
                    fallback_models.append(model)
            
            tried = {self.model}
            for fallback in fallback_models:
                if fallback in tried:
                    continue
                tried.add(fallback)
                logger.info(f"Trying fallback model: {fallback}")
                success, result = self._try_generate(fallback, prompt, system_prompt, max_tokens_override=max_tokens)
                if success:
                    logger.info(f"✓ Fallback succeeded with: {fallback}")
                    return result
                logger.warning(f"✗ Fallback {fallback} failed: {result}")
                # Try more models before giving up
                if len(tried) >= 8:  # Try up to 8 models
                    break

            return f"/* ERROR: Tried {len(tried)} models, all unavailable. Last error: {result} */"

        except requests.exceptions.Timeout:
            logger.error("OpenRouter API timeout (60s)")
            return "/* ERROR: API request timed out. Try again. */"
        except requests.exceptions.ConnectionError:
            logger.error("Cannot reach OpenRouter API — check internet connection")
            return "/* ERROR: No internet connection */"
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            return f"/* ERROR: {e} */"

    def _extract_code(self, content: str) -> str:
        """Extract code from markdown code blocks if present."""
        if not content:
            return ""
        if "```" in content:
            lines = content.split("\n")
            code_lines, in_block = [], False
            for line in lines:
                if line.strip().startswith("```"):
                    in_block = not in_block
                    continue
                if in_block:
                    code_lines.append(line)
            return "\n".join(code_lines) if code_lines else content
        return content
