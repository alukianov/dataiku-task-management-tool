"""Per-resource REST API modules (see specification/task-management-app.md).

Each module holds the functions for exactly one resource and takes a `BaseAPIClient` as its first
argument instead of constructing its own HTTP session - this keeps resources stateless, independently
testable/importable, and composable from any facade (e.g. src/api/client.py).
"""
