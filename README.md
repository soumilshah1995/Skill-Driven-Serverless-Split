# Lab: Skill-Driven Serverless Split

In this lab you learn how to **leverage a skill `.md` file** and **break a large serverless file into manageable components**—faster and with less drift. You also practice **plan mode** and **build mode** to ship changes in a clear, two-step flow.

---

## What you’ll do

- Use a **skill document** (`skill-split-serverless.md`) that defines the target layout and rules.
- Turn a single `serverless.yml` into a main file plus **lambda** and **step-functions** subfiles under an `infrastructure/` folder.
- Work in **two phases**: **plan first**, then **build** (no name/value changes, only structure).

---

## Workflow: Plan → Build

1. **Plan mode**  
   Ask the AI to apply the skill and produce a plan, e.g.:
   - *"@tmp/skill-split-serverless.md Run @tmp/Lab1 and output the files inside infrastructure inside Lab1"*  
   - Or for Lab2: *"@tmp/skill-split-serverless.md Run @tmp/Lab2 and output the files inside infrastructure inside Lab2"*  
   Get a plan that lists the target layout and what goes in each file.

2. **Build mode**  
   Then: *"Implement the plan as specified."*  
   The AI creates `infrastructure/serverless.yml`, `infrastructure/lambda/serverless.yml`, and `infrastructure/step-functions/serverless.yml` without changing any names or values.

---

## How to run things (after you clone or download)

### Prerequisites

- **Node.js** 14+
- **AWS CLI** configured (credentials and region)
- **Serverless Framework** (e.g. `npm i -g serverless` or use `npx`)

### Option A: Monolithic serverless (e.g. Lab1)

If the lab has a single `serverless.yml` at the lab root:

```bash
cd tmp/Lab1
npm install
npm install --save-dev serverless-step-functions
sls deploy
```

### Option B: Split infrastructure (e.g. Lab2 with `infrastructure/`)

If the lab has an `infrastructure/` folder with the main serverless and includes:

```bash
cd tmp/Lab2
npm install
npm install --save-dev serverless-step-functions
sls deploy --config infrastructure/serverless.yml
```

Deploy runs from the **lab root** so handler paths like `handlers/check_lock.handler` still resolve to the existing `handlers/` directory.

### Useful commands

- **Deploy:** `sls deploy` (or `sls deploy --config infrastructure/serverless.yml` for split layout)
- **Deploy a stage:** `sls deploy --stage prod`
- **Remove stack:** `sls remove` (or `sls remove --config infrastructure/serverless.yml`)

---

## Prompt pattern (copy-paste)

Use this pattern and swap the lab path as needed:

```text
@tmp/skill-split-serverless.md Run @tmp/Lab1 and output the files inside infrastructure inside Lab1
```

Then in build mode:

```text
Implement the plan as specified.
```

That’s it: **plan first, then build**, and keep all names and values unchanged.
