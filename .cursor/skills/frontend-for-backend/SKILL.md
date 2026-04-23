---
name: frontend-for-backend
description: Explains frontend behavior, bugs, and changes using backend analogies and plain language with minimal UI jargon. Use when working on ui/web, browser-facing issues, API calls from the UI, CORS, routing, or when the user is a backend engineer who wants frontend topics explained accessibly.
---

# Frontend explanations for backend engineers

## Audience assumption

The reader is comfortable with **HTTP**, **JSON**, **REST-ish APIs**, **auth tokens**, **env-based config**, and **service boundaries**. They are **not** assumed to know React internals, bundlers, or CSS layout models in depth.

## How to explain things

1. **Start with the request/response story** — What URL was called, what status/body came back, and what the page did with it. Treat the browser like a client calling your gateway.
2. **Use backend analogies** — Map UI ideas to things they already know (see table below). Say “like X in backend” once; do not stack metaphors.
3. **Define jargon once, in plain words** — If a term is unavoidable (for example “hydration”, “bundle”), give a one-sentence definition, then continue in normal language.
4. **Separate layers** — Make clear whether the issue is **network/API**, **data shape mismatch**, **routing/URL**, **build or dev server**, or **visual layout** (order on screen, spacing). Backend engineers often care most about the first two.
5. **Avoid deep framework sermons** — Do not lecture on virtual DOM, hooks rules, or bundler plugins unless the user’s problem actually depends on it.

## Concept map (frontend ↔ backend)

Use this to translate; keep wording casual.

| If you would say (frontend) | Say this to a backend engineer |
|------------------------------|--------------------------------|
| Component | Small, reusable “module” of UI; like a function that returns HTML-shaped output |
| Props | Inputs passed into that module — like arguments or a small DTO |
| State | Data the page holds in memory while you use it — like request-scoped or session-like data (but only in the browser unless saved) |
| Effect / “when X changes, do Y” | Side effect when inputs change — like a listener or a deferred job, but synchronous to the UI thread unless async |
| Fetch / API client | Same as any HTTP client; call gateway or service base URL |
| Loading / error UI | The client’s handling of pending/failed responses — like returning 202 vs 500, but shown as a spinner or message |
| Route / URL | Which “endpoint” the SPA is logically on; often drives which data to load |
| Form | Input validation + submit — like a POST body with client-side checks before send |
| CORS | Browser-enforced rule: which **origins** may read responses; fix is usually gateway headers or same-origin proxy, not “magic in React” |
| Build / dev server | Compiles and serves the UI — like `docker build` + static file host for assets |

## Describing bugs (template)

Short structure that reads well to backend folks:

1. **Trigger** — What click, URL, or payload.
2. **Expected vs actual** — Same style as API debugging.
3. **Evidence** — Status code, response body snippet, or console error **in plain English** (not a wall of stack trace unless asked).
4. **Where it lives** — File or area (`ui/web/...`) and whether it is **API contract**, **client handling**, or **display**.

## This repository

Customer UI lives under **`ui/web`**. When explaining changes, tie them to **which service or gateway path** the UI calls, and mention **base URL / env** when relevant so it matches how they already run services.

## What to avoid

- Assuming they know npm script names or bundler config without pointing to the file.
- Explaining CSS with only designer terms; prefer “this box is not wide enough” or “this list is hidden behind another layer”.
- Long lists of library names without saying which one this project actually uses.

## Optional deeper detail

If the user asks “how does X work under the hood?”, add a short subsection or link to official docs — still summarized in request/response or data-flow terms first.
