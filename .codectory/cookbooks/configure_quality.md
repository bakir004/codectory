# Configure deterministic project quality

CODECTORY reads every deterministic quality command from `projects.yaml` at the
repository root. The installer creates a starter file; `adw_modules/quality.py`
contains no repository-specific command.

## Schema

```yaml
projects:
  web:
    path: apps/web             # relative to repository root
    guides: guides             # relative to repository root
    checks:
      - name: lint
        area: frontend         # descriptive grouping shown in traces
        operation: lint        # lint | format | typecheck | build | test
        command: [bun, run, lint]
        timeout_seconds: 120
      - name: format-check
        area: frontend
        operation: format
        command: [bun, run, format, --check]
      - name: types
        area: frontend
        operation: typecheck
        command: [bun, run, typecheck]
      - name: build
        area: frontend
        operation: build
        command: [bun, run, build]
        timeout_seconds: 600
      - name: tests
        area: frontend
        operation: test
        command: [bun, test]
        timeout_seconds: 600
```

`command` must be a YAML array of argv strings, not a shell command. Commands
inherit the operator environment and run with the configured project `path` as
their working directory. Use bare executable names so the same PATH selection
an engineer uses is preserved. Project and guide paths must stay inside the
repository; project and check names must be unique and safe as artifact path
segments. Invalid configuration fails before any command starts and reports the
field that is malformed.

## Changed projects and scope

At run start CODECTORY pins `HEAD`. For `scope="changed"`, quality asks Git for
all tracked files different from that commit and adds untracked, non-ignored
files. A project is selected when a changed path is inside its configured path.
Matching is path-component aware: project `app` does not match `application`.
Deleted tracked files still select their former project. The trace records the
complete changed-file evidence and each selected project's matching files.

- `quality.run_checks(run, scope="changed")` runs every check for affected projects.
- `quality.run_checks(run, scope="all")` runs every check for every project.
- `quality.run_tests(...)` has the same scopes but selects only `operation: test`.
- `quality.run_quality(...)` remains an alias for configured checks.

A changed-scope run with no affected project is a successful empty result, with
a summary explaining that nothing ran. An all-scope run does not require a diff
to select projects.

## Failures and repair

Every selected command runs even when an earlier one fails. Full logs are kept
at `context_handoff/quality/<project>/<check>/<invocation>/command.log`; each
rerun gets a new invocation directory, and `QualityResult`
contains every failure, artifact, project, operation, command, and exit code.
`quality.as_envelope()` carries that aggregate, including bounded verbatim
output tails, into the builder repair loop.

`adw_simple_sdlc.py` runs changed-project checks after the build, hands all
failures to the builder, and retries within its bounded repair loop. Review is a
separate judgement phase. If reviewer revisions change files, changed-project
quality runs again; failures re-enter the bounded builder repair loop and each
repair is checked again before commit. Tests are deterministic checks throughout;
there is no tester agent.
