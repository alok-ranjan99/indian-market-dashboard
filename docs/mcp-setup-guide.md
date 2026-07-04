# MCP Setup Guide — Step by Step

Detected on your machine (2026-07-04):
- ✅ `claude` CLI (`/opt/homebrew/bin/claude`)
- ✅ `node` v26.4.0, `npm`, `git`
- ❌ `gh` (GitHub CLI) — install for GitHub MCP convenience
- ❌ `docker` — not needed; we use npx-based MCPs

All MCPs below are added with `claude mcp add`. Scope options:
`-s local` (this project only), `-s user` (all your projects), `-s project` (shared via `.mcp.json`).
We use `-s user` for general tools and `-s local`/`-s project` where it makes sense.

> Verify anytime with: `claude mcp list`  ·  Remove with: `claude mcp remove <name>`

---

## 1. GitHub MCP ⭐ (code hosting, PRs, issues)

**Step 1 — Create a GitHub Personal Access Token (PAT):**
1. Go to https://github.com/settings/tokens → **Generate new token (fine-grained)**.
2. Repo access: select the repo you'll create (or "All repositories").
3. Permissions: `Contents: Read/Write`, `Pull requests: Read/Write`, `Issues: Read/Write`, `Metadata: Read`.
4. Generate and **copy** the token (starts with `github_pat_...`).

**Step 2 — Add the MCP (official GitHub server, remote HTTP):**
```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  -H "Authorization: Bearer github_pat_YOUR_TOKEN_HERE" \
  -s user
```
> Alternative (local npx server, no remote):
> ```bash
> claude mcp add github -s user \
>   -e GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_YOUR_TOKEN \
>   -- npx -y @modelcontextprotocol/server-github
> ```

**Step 3 — (Recommended) Install GitHub CLI too:**
```bash
brew install gh && gh auth login
```

**Step 4 — Verify:** `claude mcp list` → `github` should show ✓ Connected.

---

## 2. Filesystem MCP ⭐ (read/write project files)

Gives project-scoped file access to the dashboard folder.
```bash
claude mcp add filesystem -s local \
  -- npx -y @modelcontextprotocol/server-filesystem \
     /Users/alok.ranjan/Documents/Projects/indian-market-dashboard
```
> Note: Claude Code already has native file tools for your working dir; this MCP is
> mainly useful if you want to grant access to *additional* folders. Optional.

---

## 3. Fetch / Web MCP ⭐ (pull live news & NSE pages during dev)

⚠️ The official fetch server is a **Python** package run via `uvx` — NOT an npm package.
`npx @modelcontextprotocol/server-fetch` will fail (that npm package does not exist / 404).

```bash
# one-time: install uv (provides uvx)
brew install uv

# add fetch using uvx (absolute path is safest for the MCP subprocess)
claude mcp add fetch -s user -- "$(which uvx)" mcp-server-fetch
```
Used to fetch RSS/news/NSE public endpoints while building & testing.
Verify: `claude mcp list` → `fetch  ✔ Connected`.

---

## 4. Puppeteer / Playwright MCP 🔸 (scrape sites without APIs)

For NSE pages that block simple requests. Playwright is the more robust choice:
```bash
claude mcp add playwright -s user -- npx -y @playwright/mcp@latest
```
First run downloads a headless browser (~150MB). Optional — only if we hit anti-scraping.

---

## 5. Figma MCP 🔸 (UI mockups — optional)

**Step 1 — Get a Figma access token:**
Figma → Settings → **Security** → *Personal access tokens* → generate. Copy it.

**Step 2 — Add MCP:**
```bash
claude mcp add figma -s user \
  -e FIGMA_API_KEY=figd_YOUR_TOKEN \
  -- npx -y figma-developer-mcp --stdio
```
> Figma also ships a built-in **Dev Mode MCP server** inside the desktop app
> (Preferences → Enable Dev Mode MCP Server, runs at `http://127.0.0.1:3845/mcp`).
> To use that instead:
> ```bash
> claude mcp add --transport http figma-dev http://127.0.0.1:3845/mcp -s user
> ```

---

## 6. Sequential-Thinking MCP 🔹 (optional reasoning aid)

```bash
claude mcp add sequential-thinking -s user \
  -- npx -y @modelcontextprotocol/server-sequential-thinking
```

---

## Recommended minimal setup to start
Run just these two now; add the rest when needed:
```bash
# 1) GitHub (after creating your PAT)
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  -H "Authorization: Bearer github_pat_YOUR_TOKEN_HERE" -s user

# 2) Fetch (for news/NSE during dev)
claude mcp add fetch -s user -- npx -y @modelcontextprotocol/server-fetch

# verify
claude mcp list
```

## Troubleshooting
- `command not found: npx` → ensure Node is on PATH (`which npx`).
- MCP shows ✗ Failed → run `claude mcp get <name>` for details; re-check token/scopes.
- Reset a server → `claude mcp remove <name>` then re-add.
- Tokens are stored in `~/.claude.json` (user scope) — treat that file as a secret.
