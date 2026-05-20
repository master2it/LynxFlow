"""Application-wide constants."""

TARGET_AI_OPTIONS: tuple[str, ...] = (
    "cursor",
    "claude",
    "chatgpt",
    "windsurf",
    "copilot",
)

# README task types (subset mapped in MVP router)
TASK_TYPES: tuple[str, ...] = (
    "responsive_ui",
    "bug_fix",
    "refactor",
    "architecture",
    "performance",
    "security_review",
    "test_generation",
    "documentation",
    "migration",
    "general",
)

DEFAULT_TASK_TYPE = "general"

# Allowlisted manifest files for repository stub (relative names only)
REPO_MANIFEST_ALLOWLIST: frozenset[str] = frozenset(
    {
        "package.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "tsconfig.json",
        "pyproject.toml",
        "requirements.txt",
        "uv.lock",
        "poetry.lock",
        "README.md",
        "angular.json",
        "next.config.js",
        "next.config.mjs",
        "next.config.ts",
        "vite.config.ts",
        "vite.config.js",
        "docker-compose.yml",
        "Dockerfile",
    }
)

MAX_MANIFEST_BYTES = 256_000
