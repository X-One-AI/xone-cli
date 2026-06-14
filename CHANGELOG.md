# Changelog

## 0.1.3

- Add `xone eval open-source` for repeatable, sanitized open-source adoption evaluation.
- Support metadata-only evaluation and optional `--clone-root` shallow public clone evaluation.
- Keep the evaluator read-only by default and document that it does not run third-party scripts, containers, tests, or project commands.

## 0.1.2

- Pin `xone doctor --install-plan` to the current recommended X-One tool versions.
- Add scenario-specific `when` and `next` guidance so first-run users know the next command to try.
- Keep the unified entrypoint small while making the install plan more actionable.

## 0.1.1

- Add scenario-based `xone doctor --install-plan` guidance.
- Let `xone runbook` auto-detect the local repository default branch when `--base` is omitted.
- Reject remote repository URLs in `xone runbook` with a clone-first message instead of producing a misleading dry run.
- Expand open-source feedback classifications for adoption evaluation.

## 0.1.0

- Add the first X-One unified CLI foundation.
