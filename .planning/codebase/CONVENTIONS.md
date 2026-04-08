# Conventions

- Prefer standard-library Python unless a phase explicitly adds a dependency.
- Keep controller truth out of UI code.
- Keep demo answers deterministic and regression-protected.
- Preserve existing endpoint and CLI contracts unless a phase states otherwise.
- Automation should never print secrets.
