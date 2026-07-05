# Lessons Learned

> Per Alok's working-style playbook: after ANY correction from the user, append the pattern
> here with a rule that prevents repeating the mistake. Reviewed at session start.

## Format
`YYYY-MM-DD — <pattern>` → **Rule:** <the rule for next time>

## Log
- 2026-07-04 — First upload of a reference image arrived as a placeholder JPG icon (no real content), yet I initially treated it as an attachment. → **Rule:** When the user shares an image, actually read/verify its bytes; if it's a generic placeholder, say so and request a re-send before acting.
- 2026-07-04 — Configured memory path pointed at a non-writable sandbox home (`/Users/dev/...`). → **Rule:** Verify the real memory dir under the actual `$HOME/.claude/projects/...`; create it if missing and flag the mismatch to the user.
- 2026-07-04 — Recommended `npx -y @modelcontextprotocol/server-fetch` in the MCP guide, but that npm package does not exist (404); the official fetch server is a Python pkg run via `uvx mcp-server-fetch`. Caused "failed to connect". → **Rule:** Verify a package actually exists on its registry before recommending an install command. MCP servers split across ecosystems — @modelcontextprotocol/server-* : filesystem/github/sequential-thinking are npm; fetch/git/time are Python (uvx). Use absolute paths for stdio MCP commands so subprocesses resolve them regardless of PATH.
- 2026-07-05 — Pinned `pandas-ta` in core deps; its current release requires Python>=3.12, breaking the 3.11 install resolve. → **Rule:** Don't add a dependency before the phase that uses it, and check a lib's `requires-python` against the project's target before adding. Moved pandas-ta to an optional `[ta]` extra (used from Phase 4). Verify installs in a clean venv before committing dep changes.
- 2026-07-06 — Streamlit theme rendered one toggle behind: injected CSS at top of `main()` using `session_state.theme` BEFORE the toggle widget ran and updated it. Live screenshot showed toggle=light but bg=dark. → **Rule:** In Streamlit, read a widget's value on the same run before using it to drive rendering. Render/evaluate the control first, then inject the global `<style>` (position in DOM doesn't matter for global CSS). Always drive the UI live and screenshot state transitions (theme toggles, tab switches) — unit tests won't catch render-ordering bugs.
