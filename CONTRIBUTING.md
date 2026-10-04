# Contributing

## Branching

- `feature/<short-description>` — new tests, new framework capability
- `fix/<short-description>` — framework bug fix (application bugs are GitHub issues, not branches)
- `docs/<short-description>` — documentation-only changes
- `chore/<short-description>` — tooling/CI/dependency changes

Branch off `main`. Keep branches scoped to one logical change.

## Commits

Prefer [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(api): add negative tests for PATCH /<task_id> ownership
fix(ui): stabilize task list locator
docs(strategy): add risk-based prioritization
```

## Issues

- Use **Bug Report** for confirmed defects in the application under test.
- Use **Specification Clarification** for ambiguities/gaps discovered during static testing or test
  design.
- Every issue should reference the relevant section of `specification/task-management-app.md` and,
  where applicable, the endpoint or UI page affected.

## Pull Requests

1. Open against `main`.
2. Fill in the PR template completely, including test evidence (Allure report screenshot or pytest
   summary).
3. Ensure CI is green: `pytest` (API + UI markers), `black --check .`, and `pylint src tests scripts`.
4. Link the issue(s) the PR addresses.
5. Squash-merge once approved.

## Adding new test coverage

- **New API endpoint**: add a method to `src/api/client.py`, then a test module under `tests/api/`,
  tagged with `@pytest.mark.api` (+ `auth`/`negative`/`regression` as applicable).
- **New UI page or flow**: add/extend a Page Object under `src/ui/pages/`, then a test module under
  `tests/ui/`, tagged with `@pytest.mark.ui`.
- Keep test data isolated — the default instance is shared; use unique data per test and never call
  `/reset` from test code. The current API CI workflow opts into a reset before the suite, so it must
  only target an isolated or explicitly authorized environment; see the reset warning in the
  [README](README.md#ci-cd).

## Code style

- `black .` to format and `pylint src tests scripts` to lint before committing — both run in CI on
  every PR.
- **Never disable a pylint rule** (inline `# pylint: disable=...` or via `pyproject.toml`) to make a
  warning go away — fix the underlying issue instead (add the missing docstring, reduce argument count,
  drop the unused parameter, reorder the import, etc.). If a rule is genuinely not applicable project-wide,
  raise it for discussion rather than silently suppressing it.
- The pylint score must stay at or above **9/10** (`fail-under = 9` in `pyproject.toml`) — the `lint` CI
  job fails the PR if it drops below that.
- Type hints on new public functions/classes.
- No hardcoded URLs/credentials in test code — use `src/config/settings.py`.

