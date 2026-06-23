AI Chat Summary — how I used AI

What I asked AI to do:
- Suggest a backend stack and pagination approach.
- Scaffold a `FastAPI` app and a seed generator for 200k products.
- Provide cursor encoding/decoding helpers and snapshot pagination logic.
- Draft a minimal UI to demo browsing and pagination.

What AI did well:
- Quickly produced working scaffolding and code samples.
- Suggested cursor + snapshot pattern and deterministic ordering.
- Gave a usable UI mockup and testing snippets.

What I corrected or validated myself:
- Ensured cursor validation and error handling are robust.
- Verified indexes and ordering for deterministic pagination.
- Rewrote some shell/test commands to be Windows-compatible and installed missing test deps.

Notes for reviewers:
- Full chat logs are available on request but I validated and adjusted every generated snippet before committing it to the repo.