# Contributing

This project follows GitHub Flow.

## Branching

-'main' is always deployable — protected, no direct pushes
- Create a branch for every change:
  - 'feature/*' — new functionality
  - 'fix/*' — bug fixes
  - 'chore/*' — maintenance, docs, config

## Commit messages

Follow Conventional Commits:
- 'feat:' new feature
- 'fix:' bug fix
- 'docs:' documentation
- 'chore:' tooling/config
- 'refactor:' code restructuring, no behavior change
- 'test:' adding/fixing tests

## Workflow

1. 'git checkout -b feature/your-change'
2. Make changes, commit with a clear message
3. 'git push origin feature/your-change'
4. Open a Pull Request into 'main'
5. CI runs automatically — lint + tests must pass
6. Merge via GitHub UI once green
7. Merging to main auto-deploys to the Raspberry Pi via GitHub Actions

## Note on project history

Early commits to 'main' were made directly during initial hardware/OS setup
and debugging (Aug 2026), before branch protection was enabled. All changes
from that point forward follow the branching strategy above.
