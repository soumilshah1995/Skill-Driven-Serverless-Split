# Cursor Subagents Guide for Lab1

This guide demonstrates how to leverage Cursor's specialized subagents to automate serverless configuration splitting, unit test creation, and documentation writing.

## What Are Subagents?

Cursor provides specialized subagents that excel at specific tasks:
- **split-serverless skill** - Restructures monolithic serverless.yml files
- **/unit-test-writer** - Creates comprehensive test suites with mocking
- **/documentation-writer** - Generates professional project documentation

## Quick Start

Simply paste this prompt into Cursor to automate the entire workflow:

```
Step 1: Split the serverless configuration for Skill-Driven-Serverless-Split/Lab1
- Apply the split-serverless skill to Lab1/serverless.yml
- Create infrastructure/ folder with main serverless.yml, lambda/serverless.yml, and step-functions/serverless.yml
- Wait for this to complete before proceeding

Step 2: After split is complete, launch two subagents in parallel:

Subagent A (/unit-test-writer): Create comprehensive unit tests for all handlers in Lab1/handlers/. Write tests with mocking, run pytest with coverage, and report results.

Subagent B (/documentation-writer): Document the Lab1 project including the new infrastructure/ layout. Update README with project overview, architecture, setup instructions, and deployment steps.

Execute step 1 first, then step 2 in parallel.
```

## What This Does

### Step 1: Serverless Configuration Split
- Reads `Lab1/serverless.yml`
- Creates modular structure in `infrastructure/` folder:
  ```
  infrastructure/
  ├── serverless.yml              # Main config
  ├── lambda/serverless.yml       # Lambda functions
  └── step-functions/serverless.yml # State machines
  ```
- Preserves all function names, handlers, and references

### Step 2: Parallel Subagent Execution

**Unit Test Writer** creates:
- Comprehensive test suite in `tests/` directory
- Mocked AWS service calls (S3, etc.)
- pytest configuration and fixtures
- Coverage reporting (~100% coverage)
- `requirements-test.txt` with dependencies

**Documentation Writer** creates:
- Professional README.md
- Architecture diagrams and explanations
- Setup and deployment instructions
- Usage examples and testing scenarios
- Configuration details

## Results

After execution, you'll have:
- ✅ Modular serverless configuration
- ✅ 50+ unit tests with full coverage
- ✅ Professional documentation
- ✅ Ready-to-deploy project structure

## Benefits

1. **Automated Refactoring** - No manual file splitting required
2. **Instant Test Coverage** - Comprehensive tests in minutes
3. **Professional Docs** - Production-ready documentation
4. **Parallel Execution** - Unit tests and docs generated simultaneously
5. **Consistency** - Following best practices automatically

## Running the Tests

```bash
cd Skill-Driven-Serverless-Split/Lab1
pip install -r requirements-test.txt
pytest tests/ --cov=handlers --cov-report=term-missing
```

## Deploying from New Structure

```bash
cd infrastructure/
serverless deploy
```

## Tips

- The subagents work autonomously - you can monitor their progress
- Both subagents complete in parallel, saving time
- All original functionality is preserved, only structure changes
- Tests include success cases, error handling, and edge cases
- Documentation is tailored to your specific project structure

---

**Pro Tip:** You can use this pattern for any serverless project. Just modify the paths and handler names in the prompt!
