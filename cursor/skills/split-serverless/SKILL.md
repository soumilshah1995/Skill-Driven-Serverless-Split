# Split Serverless Configuration Skill

Take any monolithic `serverless.yml` and restructure it into manageable components (Lambda and Step Functions in separate files) **without changing any names or values**.

## When to use this skill

Use this skill when you want to create a Cursor skill that restructures serverless configurations. Common scenarios:
- Breaking down large serverless.yml files into modular structure
- Organizing Lambda functions and Step Functions separately
- Improving maintainability without changing functionality

## Instructions

### Target Structure

```
infrastructure/
├── serverless.yml          # main: service, custom, provider, plugins + includes
├── lambda/
│   └── serverless.yml      # all Lambda definitions
└── step-functions/
    └── serverless.yml      # all Step Function state machines
```

### Rules (MUST Follow)

1. **DO NOT change any name or value**
   - Function logical IDs stay the same
   - Handler paths unchanged
   - State machine names unchanged
   - All `Fn::GetAtt` references unchanged
   - Environment variables unchanged

2. **ONLY restructure**
   - Move blocks into separate files
   - Wire main file via `${file(...)}`
   - Single deployment point (main serverless.yml)

### Step-by-Step Process

**Step 1: Analyze Original File**

Identify these blocks in the monolithic `serverless.yml`:
- Keep in main: `service`, `custom`, `provider`, `plugins`
- Extract: `functions` (entire map)
- Extract: `stepFunctions.stateMachines` (entire map)

**Step 2: Create Main serverless.yml**

```yaml
service: <exact value from original>

custom:
  <exact content from original>

provider:
  <exact content from original>

functions: ${file(lambda/serverless.yml)}

stepFunctions:
  stateMachines: ${file(step-functions/serverless.yml)}

plugins:
  <exact content from original>
```

**Step 3: Create lambda/serverless.yml**

Copy the entire `functions` map (no wrapper):

```yaml
functionLogicalId1:
  handler: handlers/function1.handler
  description: ...
  environment:
    KEY: value

functionLogicalId2:
  handler: handlers/function2.handler
  ...
```

**Step 4: Create step-functions/serverless.yml**

Copy the entire `stateMachines` map (no wrapper):

```yaml
stateMachineKey1:
  name: StateMachineName
  role: !GetAtt StepFunctionRole.Arn
  definition:
    ...

stateMachineKey2:
  name: AnotherStateMachine
  ...
```

### Verification Checklist

Before completing, verify:
- [ ] Main serverless has same `service`, `custom`, `provider`, `plugins`
- [ ] Main uses `${file(...)}` for functions and stepFunctions
- [ ] lambda/serverless.yml has complete functions map
- [ ] step-functions/serverless.yml has complete stateMachines map
- [ ] All `Fn::GetAtt` references match function logical IDs
- [ ] No renames anywhere
- [ ] Single `sls deploy` from main works

### Usage Example

```
User: "Split the Lab1/serverless.yml into infrastructure/ folder"

Assistant actions:
1. Read Lab1/serverless.yml
2. Create infrastructure/ folder
3. Create main serverless.yml with includes
4. Create lambda/serverless.yml with all functions
5. Create step-functions/serverless.yml with all state machines
6. Verify all references are intact
```

## Important Notes

- This restructures layout ONLY, no functional changes
- Deploy command remains: `sls deploy` (or with --config flag)
- All handler paths resolve from deployment root
- Works with any serverless.yml that has functions and/or stepFunctions
