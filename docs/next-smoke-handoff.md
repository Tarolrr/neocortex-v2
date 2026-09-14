# Handoff: isolated native-result smoke (requires separate approval)

This offline package adds no scheduler, lifecycle, model call, task creation, approval, merge, or service change. Its CLI validation and [SDK gap report](sdk-compatibility-report.md) are not a successful live smoke.

Bootstrap/readiness evidence: [offline-environment-readiness.md](offline-environment-readiness.md). From this worktree:

```console
$ export PATH=/opt/neocortex-v2-runner/.venv/bin:$PATH
$ python3 -m unittest discover -s tests_bootstrap -p 'test_*.py'
$ pytest -q
$ ruff check .
$ python3 -m neocortex_v2 --help
$ python3 -m neocortex_v2 config-check --namespace isolated-smoke --base-url http://127.0.0.1:4096 --workdir /existing/scratch-git --state-dir /existing/state --provider PROVIDER --model MODEL
```

The next package must separately approve an **isolated launch** and native-result investigation/report that can conclude `pass`, `blocked`, `failed`, or `uncertain`; none may create tasks. A successful live smoke remains an obligatory gate before implementation lifecycle.

It must use a scratch Git directory, isolated OpenCode namespace/store/state, and one explicit provider/model call with secret-safe configuration. Record namespace/session/request-response bindings, keeping IDs before and after dispatch distinct. Request native schema-constrained output and validate schema plus semantic bindings. Bound timeout and set `max_retries=0` for create/dispatch; uncertain delivery is reconciled, never automatically replayed.

Durable approval/attempt/outbound-intent records, owner delivery, restart reconciliation, stop settlement, critic/checks, merge/acceptance, and retention remain unimplemented and require distinct approval.
