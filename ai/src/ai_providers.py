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
_model_cache = {"models": [], "timestamp": 0, "ttl": 300}  # 5 min TTL


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
        self.model = config.get("model", "google/gemma-3-12b-it:free")
        self.max_tokens = config.get("max_tokens", 2048)
        self.temperature = config.get("temperature", 0.3)
        self.max_retries = config.get("max_retries", 3)

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def get_name(self) -> str:
        return f"OpenRouter ({self.model})"

    def _try_generate(self, model: str, prompt: str, system_prompt: str) -> tuple:
        """Attempt generation with a specific model. Returns (success, result)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/amitdevx/TurboC-",
            "X-Title": "TurboCPP AI",
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)

        # Some models don't support system prompts — retry with combined user message
        if resp.status_code == 400 and "not enabled" in resp.text.lower():
            payload["messages"] = [
                {"role": "user", "content": f"{system_prompt}\n\n{prompt}"},
            ]
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)

        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return True, self._extract_code(content)
        elif resp.status_code == 429:
            return False, f"rate-limited ({model})"
        elif resp.status_code == 404:
            return False, f"not found ({model})"
        else:
            error_msg = resp.text[:200]
            return False, f"API {resp.status_code}: {error_msg}"

    def generate_code(self, prompt: str, system_prompt: str) -> str:
        try:
            # First try the configured model
            success, result = self._try_generate(self.model, prompt, system_prompt)
            if success:
                return result

            logger.warning(f"Primary model failed: {result}. Trying fallbacks...")

            # Auto-fallback: try other available free models
            fallback_models = get_free_model_ids()
            tried = {self.model}
            for fallback in fallback_models:
                if fallback in tried:
                    continue
                tried.add(fallback)
                logger.info(f"Trying fallback model: {fallback}")
                success, result = self._try_generate(fallback, prompt, system_prompt)
                if success:
                    logger.info(f"Fallback succeeded with: {fallback}")
                    return result
                logger.warning(f"Fallback {fallback} failed: {result}")
                if len(tried) >= self.max_retries + 1:
                    break

            return f"/* ERROR: All models unavailable. Last error: {result} */"

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
