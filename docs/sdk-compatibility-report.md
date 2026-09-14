# SDK/API compatibility investigation: offline planning evidence

Status: **gap recorded; no live behaviour is claimed.** Investigation date:
2026-09-15. This evaluates the locked candidate, not `main`.

## Exact evidence examined

- Python SDK release [`v0.1.0-alpha.36`](https://github.com/anomalyco/opencode-sdk-python/releases/tag/v0.1.0-alpha.36), tag commit [`817f1a08163452fd7fcfbb1268b262cc78a9d629`](https://github.com/anomalyco/opencode-sdk-python/tree/817f1a08163452fd7fcfbb1268b262cc78a9d629). Its [`pyproject.toml`](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/pyproject.toml) names `opencode-ai` version `0.1.0-alpha.36`; the old shorthand `0.1.0a36` is not its release string.
- Selected OpenCode candidate remains [`anomalyco/opencode` v1.18.30](https://github.com/anomalyco/opencode/releases/tag/v1.18.30), tag commit [`3104c1428ec91f809e5ab86631300de41eb6952e`](https://github.com/anomalyco/opencode/tree/3104c1428ec91f809e5ab86631300de41eb6952e). Its checked API definition is [`packages/sdk/openapi.json`](https://github.com/anomalyco/opencode/blob/3104c1428ec91f809e5ab86631300de41eb6952e/packages/sdk/openapi.json). No server was installed or contacted.

## Actual Python SDK surface

[`SessionResource.create`](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/src/opencode_ai/resources/session.py#L55-L77) exists and returns `Session`, whose actual `id` is defined in [`types/session.py`](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/src/opencode_ai/types/session.py#L29-L43). There is no `session.prompt` in this release. The send method is [`SessionResource.chat`](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/src/opencode_ai/resources/session.py#L151-L204): it needs `id`, `model_id`, `provider_id`, and `parts`, with optional `message_id`, `mode`, `system`, and `tools`.

[`SessionChatParams`](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/src/opencode_ai/types/session_chat_params.py#L16-L29) serializes `model_id` and `provider_id` as `modelID` and `providerID`. It has no `format`, `outputFormat`, schema, or validation-retry field. The immediate return type is [`AssistantMessage`](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/src/opencode_ai/types/assistant_message.py#L49-L76): it has `id`, `session_id` (alias `sessionID`), and optional `error`, but no `structured_output` or native JSON-result field. Thus this SDK cannot prove the required native schema-constrained result path.

The documented upstream JavaScript SDK is different: its [Structured Output section](https://opencode.ai/docs/sdk/#structured-output) documents `session.prompt` with `body.format` and JSON schema. That is API evidence, not Python SDK type evidence, and is not translated into Python pseudo-code.

## Errors, timeout, and replay policy

The Python README documents `APIConnectionError`, `APIStatusError`, and `APITimeoutError`, one-minute default timeout, and two automatic retries; `Opencode(max_retries=0)` disables them. See [errors/retries/timeouts](https://github.com/anomalyco/opencode-sdk-python/blob/817f1a08163452fd7fcfbb1268b262cc78a9d629/README.md#L119-L206). The generated client’s reused idempotency header is not proof that an OpenCode dispatch is safe to replay.

For a future non-idempotent create/dispatch, use `max_retries=0` and bounded explicit timeout. Timeout, connection failure, or missing response is **uncertain**: retain outbound intent and bindings, reconcile, and never automatically replay.

## Planning consequence

The Python SDK has a concrete native-output gap. The pinned server API nevertheless documents a narrow HTTP candidate, which must be separately approved and investigated: `POST /session/{sessionID}/message`, operationId [`session.prompt`](https://github.com/anomalyco/opencode/blob/3104c1428ec91f809e5ab86631300de41eb6952e/packages/sdk/openapi.json#L6203-L6318) (not `/session/{id}/prompt`). The path parameter is `sessionID`; optional query fields are `directory` and `workspace`. The request body requires `parts` and accepts `model.providerID`, `model.modelID`, `messageID`, and `format`. `format` may be [`{ "type": "json_schema", "schema": ..., "retryCount": ... }`](https://github.com/anomalyco/opencode/blob/3104c1428ec91f809e5ab86631300de41eb6952e/packages/sdk/openapi.json#L15929-L15945).

For this exact definition, a successful `200` body requires `info` and `parts`; `info` is an [`AssistantMessage`](https://github.com/anomalyco/opencode/blob/3104c1428ec91f809e5ab86631300de41eb6952e/packages/sdk/openapi.json#L16234-L16374), whose required bindings include `id`, `sessionID`, `parentID`, `modelID`, and `providerID`. Its optional `structured` field is declared as an unconstrained object, and its optional `error` is a union including `StructuredOutputError`. The documented HTTP errors are `400` `BadRequest` (`_tag`) or `InvalidRequestError` (`_tag`, `message`, optional `kind`/`field`), and `404` `NotFoundError` (`name`, `data.message`), as defined by the same operation and [error schemas](https://github.com/anomalyco/opencode/blob/3104c1428ec91f809e5ab86631300de41eb6952e/packages/sdk/openapi.json#L15645-L15675). Thus the result path to investigate is `response.info.structured`; its runtime shape and completion/error timing remain unverified.

That future Python HTTP experiment must disable any client transport retry, use a bounded timeout, set no schema-validation retry unless its non-replay semantics are established, and retain request/response/error capture. It must bind the pre-dispatch session and requested message IDs separately from returned `info.id`/`info.parentID`; a timeout, transport failure, or missing response is **uncertain** and may not trigger automatic replay. This is a candidate, neither implemented nor live verified. Ordinary-text parsing and agent-written `outcome.json` are not allowed as fallback.
