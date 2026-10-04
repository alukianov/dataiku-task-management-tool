---
applyTo: "src/**/*.py,tests/**/*.py,scripts/**/*.py"
---

# Docstring conventions

Every module and every function/method gets a docstring that states only *what* it is/does, its
args, and its output. Never explain *why* it's built that way, note limitations, or reference defect
IDs/docs (`TM-xx`, `docs/known-defects-and-improvements.md`, etc.) inside a docstring - that kind of context
belongs in a code comment near the relevant line, not the docstring.

**File (module) docstring** - one or two plain sentences stating what the module contains:
```python
"""<What this module contains/provides.>"""
```

**Function/method docstring** (Google-style; apply to every non-test function/method):
```python
"""<One-line summary of what the function does, imperative mood.>

Args:
    param_name: What it represents.
    other_param: What it represents.

Returns:
    What is returned.
"""
```
Omit the `Args:` section for functions with no parameters (besides `self`). Omit the `Returns:`
section for functions that return `None`.

**Test function docstring** (`tests/api/`, `tests/ui/`) - one line stating the scenario verified, no
`Args:`/`Returns:` section (fixture parameters aren't documented as args, and tests return `None`):
```python
"""Verifies that <scenario/behavior under test>."""
```
