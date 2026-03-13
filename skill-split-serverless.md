# Skill: Split a Monolithic Serverless File into Manageable Structure

**Purpose:** Take any single large `serverless.yml` and restructure it so that Lambdas and Step Functions live in separate files, with a main serverless that composes them. **No changes to names or values**—only file/layout restructuring into manageable pieces.

---

## 1. Target structure

```
<infrastructure-dir>/
├── serverless.yml          # main: service, custom, provider, plugins + includes
├── lambda/
│   └── serverless.yml      # all Lambda definitions (same keys/values as original)
└── step-functions/
    └── serverless.yml      # all Step Function state machines (same keys/values as original)
```

**Optional (one file per state machine):**  
One file per workflow under `step-functions/<state-machine-key>.yml`, with main referencing each via `${file(step-functions/<key>.yml)}`. Content per state machine unchanged.

---

## 2. Rules (must follow)

- **Do not change any name or value:** function logical IDs, handler paths, state machine names, `role`, `definition`, `events`, env vars, `Fn::GetAtt` references, etc. must stay identical to the original file.
- **Only restructure:** move blocks into separate files and wire the main file via `${file(...)}`.
- **Single deployment:** main serverless is the one you deploy; it pulls in Lambda and Step Function content so one `serverless deploy` still deploys everything.

---

## 3. Step-by-step (works for any serverless.yml)

### Step 1: Identify blocks in the original file

From the **single** `serverless.yml`:

1. **Keep in main:** `service`, `custom`, `provider`, `plugins`.
2. **Extract:** `functions` — the entire map (every key under `functions:`).
3. **Extract:** `stepFunctions.stateMachines` — the entire map (every key under `stepFunctions:` → `stateMachines:`).

Do not change any key or value inside these blocks when extracting.

### Step 2: Create the main `serverless.yml`

- Keep **only:** `service`, `custom`, `provider`, and `plugins`.
- **Replace** the inline `functions` map with an include to the Lambda file.
- **Replace** the inline `stepFunctions` section with an include to the Step Functions file.

**Main file pattern:**

```yaml
service: <keep exact value from original>

custom:
  <keep exact content from original>

provider:
  <keep exact content from original>

functions: ${file(lambda/serverless.yml)}

stepFunctions:
  stateMachines: ${file(step-functions/serverless.yml)}

plugins:
  <keep exact content from original>
```

- Include paths are relative to the main serverless.yml directory.
- Do not rename `service` or change `custom` / `provider` / `plugins` content.

### Step 3: Create `lambda/serverless.yml`

- Copy the **entire** `functions` map from the original (all keys and values).
- This file contains **only** that map — no `service`, no `provider`, no top-level `functions:` key. Root of the file is the map of function logical ID → definition.

**Content pattern:**

```yaml
<functionLogicalId1>:
  handler: ...
  description: ...
  environment:
    ...

<functionLogicalId2>:
  handler: ...
  ...
```

- Every `Fn::GetAtt` in Step Function definitions that references a Lambda must use the same logical ID as a key in this file. Do not rename.
- Preserve handler paths, descriptions, environment, and all other properties exactly.

### Step 4: Create `step-functions/serverless.yml`

- Copy the **entire** `stateMachines` map from the original (all state machine keys and full definitions).
- This file contains **only** that map — i.e. the object that was under `stepFunctions.stateMachines`. No `stepFunctions:` or `stateMachines:` wrapper; root of the file is the state-machines map.

**Content pattern:**

```yaml
<stateMachineKey1>:
  name: ...
  role: ...
  definition:
    ...

<stateMachineKey2>:
  name: ...
  ...
```

- Keep every `name`, `role`, `events`, and `definition` exactly as in the original. All `Fn::GetAtt` references in definitions must match function logical IDs in `lambda/serverless.yml`.
- Root keys in this file are the state machine logical IDs; do not change them.

### Step 5: Optional — one file per state machine

To split further:

1. For each key under `stepFunctions.stateMachines`, create `step-functions/<key>.yml` containing **only** that state machine’s value (the object with `name`, `role`, `definition`, `events`).
2. In the **main** serverless:

```yaml
stepFunctions:
  stateMachines:
    <stateMachineKey1>: ${file(step-functions/<stateMachineKey1>.yml)}
    <stateMachineKey2>: ${file(step-functions/<stateMachineKey2>.yml)}
```

Same keys and values as original; only layout changes.

---

## 4. Checklist before finishing

- [ ] Main serverless has same `service`, `custom`, `provider`, `plugins` as original.
- [ ] Main uses `functions: ${file(lambda/serverless.yml)}` and `stepFunctions.stateMachines: ${file(step-functions/serverless.yml)}` (or per-file includes for state machines).
- [ ] `lambda/serverless.yml` has the full `functions` map with identical keys and values.
- [ ] `step-functions/serverless.yml` has the full `stateMachines` map with identical keys and values.
- [ ] Every `Fn::GetAtt: [ <functionLogicalId>, Arn ]` in step definitions matches a function key in `lambda/serverless.yml`.
- [ ] No renames: function logical IDs, state machine keys, state machine `name`, handler paths, and config references unchanged.

---

## 5. How to use this skill

1. **Input:** Path to a single monolithic `serverless.yml`.
2. **Apply:** Follow §3 Step 1–4 (and optionally Step 5) without changing any name or value.
3. **Output:** Same directory (or target folder) with main `serverless.yml`, `lambda/serverless.yml`, and `step-functions/serverless.yml` (or one file per state machine).

The skill applies to **any** serverless YAML that has `functions` and/or `stepFunctions.stateMachines`: restructure into the main + Lambda + Step Function layout and keep all names and values unchanged.
