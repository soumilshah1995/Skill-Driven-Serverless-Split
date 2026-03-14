# Cursor Skills and Agents

This project uses both **Skills** (instructions) and **Agents** (autonomous workers) for development tasks.

## 📚 Skills (Reference/Instructions)

Skills are `.md` files that provide instructions and patterns. You reference them with `@`.

### Available Skill: Split Serverless

**Location**: `.cursor/skills/split-serverless/SKILL.md`

**Purpose**: Restructure monolithic `serverless.yml` into modular components.

**Usage**:
```
@.cursor/skills/split-serverless/SKILL.md Split Lab1/serverless.yml
```

**What it does**:
- Breaks down large serverless.yml 
- Separates Lambda and Step Functions
- Creates `${file(...)}` includes
- Maintains all names unchanged

## 🤖 Agents (Autonomous Workers)

Agents are defined in `AGENTS.md` and work autonomously. You invoke them with natural language.

### Available Agent: Unit Test Writer

**Documentation**: `../AGENTS.md`

**Purpose**: Write comprehensive unit tests for Python Lambda handlers.

**Usage**:
```
"Write unit tests for Lab1/handlers/"
```

**What it does**:
1. Analyzes handler code
2. Creates `tests/` folder structure
3. Writes test files with proper mocking
4. Runs pytest with coverage
5. Reports results (autonomous, no interaction needed)

## 🎯 Key Differences

| Aspect | Skills | Agents |
|--------|--------|--------|
| **Type** | Instructions/Documentation | Autonomous Workers |
| **Invocation** | `@.cursor/skills/<name>/SKILL.md` | Natural language |
| **Execution** | AI follows instructions | Runs independently |
| **Interaction** | You guide the process | Fully autonomous |
| **Use Case** | Reference patterns | Complex multi-step tasks |

## 📖 Examples

### Using a Skill (Split Serverless)
```
@.cursor/skills/split-serverless/SKILL.md Split Lab1/serverless.yml into infrastructure/
```
↓
AI follows instructions to restructure files

### Using an Agent (Unit Test Writer)
```
Write unit tests for all handlers in Lab1/handlers/
```
↓
Agent runs autonomously:
1. Reads handlers
2. Creates tests
3. Runs pytest
4. Reports: "✅ 25 tests, 95% coverage"

## 🔄 Combined Workflow

```
Step 1: Use Skill to split config
"@.cursor/skills/split-serverless/SKILL.md Split Lab1/serverless.yml"

Step 2: Use Agent to generate tests  
"Write unit tests for Lab1/handlers/"

Step 3: Agent reports completion
"✅ Tests complete, all passing, 95% coverage"
```

## 📂 Project Structure

```
.cursor/
├── README.md (this file)
└── skills/
    └── split-serverless/
        └── SKILL.md

AGENTS.md (at project root)
```

## 💡 When to Use What

**Use a Skill when:**
- You need reference instructions
- Following a pattern/template
- Want to guide the AI step-by-step
- Task benefits from structured documentation

**Use an Agent when:**
- Task has multiple steps
- Need autonomous execution
- Want hands-off completion
- Can verify results programmatically

## 📝 Adding New Skills

1. Create: `.cursor/skills/<skill-name>/SKILL.md`
2. Write clear instructions
3. Include examples and checklists
4. Test with `@.cursor/skills/<skill-name>/SKILL.md`

## 🤖 Adding New Agents

1. Add section to `AGENTS.md` (at project root)
2. Define agent capabilities
3. Specify invocation patterns
4. Document autonomous behavior
5. List success criteria
6. Test with natural language prompts

## 🚀 Getting Started

1. **Split a config**: `@.cursor/skills/split-serverless/SKILL.md Split Lab1/serverless.yml`
2. **Generate tests**: `Write unit tests for Lab1/handlers/`
3. **Review results**: Agent reports completion automatically

See `SKILLS-GUIDE.md` and `AGENTS.md` for complete documentation.
