"""Reconciliation entrypoint. Fan-out and statistical QA are emitted by build_project."""

from build_project import compute

if __name__ == "__main__":
    compute()

