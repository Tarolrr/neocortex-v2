# SDK/API compatibility investigation: offline planning evidence

Status: **gap recorded; no live behaviour is claimed.** Investigation date:
2026-09-15. This evaluates the locked candidate, not `main`.

## Exact evidence examined

- Python SDK release [`v0.1.0-alpha.36`](https://github.com/anomalyco/opencode-sdk-python/releases/tag/v0.1.0-alpha.36), tag commit [`817f1a08163452fd7fcfbb1268b262cc78a9d629`](https://github.com/anomalyco/opencode-sdk-python/tree/817f1a08163452fd7fcfbb1268b262cc78a9d629). Its [`pyproject.toml`](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/pyproject.toml) names `opencode-ai` version `0.1.0-alpha.36`; the old shorthand `0.1.0a36` is not its release string.
- Selected OpenCode candidate remains [`anomalyco/opencode` v1.18.30](https://github.com/anomalyco/opencode/releases/tag/v1.18.30). No server was installed or contacted.

## Actual Python SDK surface

[`SessionResource.create`](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/src/opencode_ai/resources/session.py#L55-L77) exists and returns `Session`, whose actual `id` is defined in [`types/session.py`](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/src/opencode_ai/types/session.py#L29-L43). There is no `session.prompt` in this release. The send method is [`SessionResource.chat`](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/src/opencode_ai/resources/session.py#L151-L204): it needs `id`, `model_id`, `provider_id`, and `parts`, with optional `message_id`, `mode`, `system`, and `tools`.

[`SessionChatParams`](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/src/opencode_ai/types/session_chat_params.py#L16-L29) serializes `model_id` and `provider_id` as `modelID` and `providerID`. It has no `format`, `outputFormat`, schema, or validation-retry field. The immediate return type is [`AssistantMessage`](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/src/opencode_ai/types/assistant_message.py#L49-L76): it has `id`, `session_id` (alias `sessionID`), and optional `error`, but no `structured_output` or native JSON-result field. Thus this SDK cannot prove the required native schema-constrained result path.

The documented upstream JavaScript SDK is different: its [Structured Output section](https://opencode.ai/docs/sdk/#structured-output) documents `session.prompt` with `body.format` and JSON schema. That is API evidence, not Python SDK type evidence, and is not translated into Python pseudo-code.

## Errors, timeout, and replay policy

The Python README documents `APIConnectionError`, `APIStatusError`, and `APITimeoutError`, one-minute default timeout, and two automatic retries; `Opencode(max_retries=0)` disables them. See [errors/retries/timeouts](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/README.md#L119-L206). The generated client’s reused idempotency header is not proof that an OpenCode dispatch is safe to replay.

For a future non-idempotent create/dispatch, use `max_retries=0` and bounded explicit timeout. Timeout, connection failure, or missing response is **uncertain**: retain outbound intent and bindings, reconcile, and never automatically replay.

## Planning consequence

The Python SDK has a concrete native-output gap. A separately approved package may investigate a narrow documented HTTP candidate: Python `httpx` issues the documented `POST /session/{id}/prompt` shape from the JavaScript docs (`body.parts` and `body.format`), with retries disabled, bounded timeout, and explicit response/error capture. It must pin matching OpenCode release API definitions and verify native result/error fields. This is a candidate, neither implemented nor live verified. Ordinary-text parsing and agent-written `outcome.json` are not allowed as fallback.
