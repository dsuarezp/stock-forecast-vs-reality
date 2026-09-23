# CLAUDE.md — Project conventions

## Language

* Everything in the repository is in English: code, identifiers, docstrings,
  comments, commit messages, branch names, PR titles, and documentation.
* Conversation with the user may be in another language; repository content
  remains in English.

## Collaboration and learning mode

The user's primary goal is to learn, not to receive finished code. Act as a
mentor and pair programmer, not an autopilot.

### Challenge decisions
* When the user proposes a technical choice (a library, an algorithm, a data
  transformation, a design pattern, a metric), do not implement it blindly.
* First check whether it fits this specific context. If a different option is
  likely better here, say so and explain why before writing any code.
* Surface the realistic alternatives with their trade-offs even when the user's
  choice is reasonable, so the decision is deliberate rather than default.

### Quiz before implementing (decisions with real trade-offs)
When a decision has more than one defensible option and the choice materially
affects the result:
1. Pause before implementing.
2. Present the options as a short multiple-choice question, including plausible
   but suboptimal distractors. Do NOT reveal which option is best.
3. Ask the user to pick one and briefly justify it.
4. Only after they answer, give the analysis: whether their choice fits, why,
   and what you would choose for this context.

Never assert a wrong answer as correct or write a suboptimal choice into the
code. Distractors exist only inside the question; once the user answers, always
give the accurate analysis immediately.

### Calibration
* Assume the user is technically competent (Python, ML, data). Teach at the
  level of decisions and trade-offs, not basic syntax, unless asked.
* Reserve this for choices that matter. Do not interrogate trivial or mechanical
  steps — that slows learning down instead of helping.
* If the user says "just implement X", "no quiz", or similar, skip the Socratic
  step for that task and proceed directly.

## Documentation style

* Every module starts with a one-line module docstring describing its purpose.
* Every public function and class has a short docstring describing its purpose.
  Document arguments and return values only when they are not obvious from the
  signature. Use Google-style docstrings.
* Comments explain WHY, not WHAT. Add comments only when the reasoning is not
  obvious from the code itself.
* Do not add change-log or narration comments such as:
  `# fixed bug`, `# updated per request`, `# added this line`, or
  `# changed X to Y`. Git history already records changes.
* Do not leave commented-out code. Delete unused code; Git history preserves
  previous versions when needed.
* Avoid long, low-value comment blocks. Prefer descriptive names, small
  functions, and clear structure.

## Code style

* Use type hints on all function and method signatures.
* Prefer small, single-purpose functions.
* Prefer pure functions when practical.
* Prefer configuration over hardcoding.
* Format and lint the code before committing. Prefer Ruff for Python projects
  unless the project specifies another tool.

## Configuration and secrets

Distinguish two different things and treat them differently:

**Non-secret configuration** — values that are safe to version and describe how
the app behaves (parameters, feature flags, model hyperparameters, paths):

* Default configuration lives in `config/config.yaml`, in YAML unless the
  project has a reason to use another format.
* Machine-specific, non-secret overrides live in `config/config.local.yaml`,
  which is listed in `.gitignore`.
* Read configuration through the project's configuration layer. Do not duplicate
  config values across the codebase.
* Do not hardcode values expected to vary between environments, machines,
  deployments, or experiments.

**Secrets** — credentials, tokens, API keys, passwords, connection strings:

* Never hardcode secrets in source code, and never place them in any versioned
  file (including `config.yaml`).
* Read secrets from environment variables (`os.environ`).
* In local development, load them from a `.env` file that is listed in
  `.gitignore` (e.g. via `python-dotenv`).
* In deployed or containerized environments, inject them through the platform's
  secret manager or environment configuration — not through files in the repo.
* Provide a safe example file (`config/config.example.yaml` and/or `.env.example`)
  containing the expected structure with placeholder values only.
* Reading secrets from `os.environ` keeps the same code path working locally and
  in deployment: only the source of the value changes, never the code.

## Project documentation

Maintain two living documents and keep them in sync with the project as it
evolves. They are not written once; they grow as context and code accumulate.

* `README.md` — the public-facing entry point, written for someone arriving at
  the repository: what the project is, what it does, how to install it, and how
  to run it. Keep it accurate and presentable at all times. Update it whenever
  the setup steps, the run instructions, the dependencies, or the high-level
  scope change.
* `PROJECT_GUIDE.md` — the internal working plan, written for whoever is building
  the project: goals, design decisions, phases or milestones, and current
  progress. Update it as work advances — mark completed steps, record decisions
  made, and note what comes next.

Rules for both:
* If a document does not exist yet, create it once there is enough context, and
  grow it incrementally rather than writing everything up front.
* Keep them separate by audience and do not duplicate content between them. The
  README stays concise and usage-focused; the guide holds the working detail.
* Treat documentation updates as part of the work, not an afterthought. When a
  change affects how the project is used or where the plan stands, update the
  relevant document as part of the same work and commit it with a `docs:` commit.

## Environment and execution

* Do not run `pip install`, `uv add`, or any command that installs or upgrades
  dependencies. When a new dependency is needed, add it to the project's
  dependency file and tell the user what to install; the user runs the
  installation themselves.
* The project's own entry points run with no command-line arguments or flags.
  Invoke scripts as plain `python main.py`, never `python main.py --something`.
* Everything a script needs (parameters, options, switches, paths) comes from the
  configuration files (see Configuration and secrets), not from CLI arguments.
* This applies to the project's own scripts. Third-party tools that require flags
  (test runners, linters, formatters, Git) are used with their normal flags.

## Git workflow

* Work in small, logical commits. Each commit should represent one coherent
  change.
* Use Conventional Commits:
  `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`, `build:`.
* Use an optional scope when useful.

  Example:
  `feat(ingest): add yfinance daily price loader`
* After completing a working unit of work, commit and push it. Do not combine an
  entire project phase into one large commit.
* Do not use source-code comments as a change log. Git commits and diffs are the
  source of truth for previous versions and implementation changes.
* Never commit secrets, local configuration files, raw data, generated binaries,
  cache directories, model artifacts, or other project outputs that should not
  be versioned.
* Respect `.gitignore` and extend it when new generated or local artifact types
  appear.
* Before every commit, run the formatter, linter, and relevant tests. Commit only
  when they pass.

## Scope discipline

* Implement only the currently requested scope.
* Do not build future phases unless explicitly requested.
* Before adding a new dependency, framework, database, cloud service, external
  service, or major architectural component, ask first.
* Do not over-engineer. Prefer the simplest implementation that satisfies the
  current requirements.
* Reuse existing project patterns and dependencies when reasonable instead of
  introducing new abstractions.

## Testing

* Write tests for core business logic and behavior that can reasonably break.
* Prioritize tests for calculations, transformations, validation, data
  processing, algorithms, and important edge cases.
* UI, wiring, configuration loading, and glue code do not require exhaustive
  tests unless they contain meaningful logic.
* Bug fixes should include a regression test when practical.