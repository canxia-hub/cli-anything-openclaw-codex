---
name: >-
  cli-anything-adguardhome
description: >-
  Command-line interface for Adguardhome - CLI harness for AdGuardHome - control your ad blocker from the command line or via agents....
---

# cli-anything-adguardhome

CLI harness for AdGuardHome - control your ad blocker from the command line or via agents.

## Installation

This CLI is installed as part of the cli-anything-adguardhome package:

```bash
pip install cli-anything-adguardhome
```

**Prerequisites:**
- Python 3.10+
- adguardhome must be installed on your system


## Usage

### Basic Commands

```bash
# Show help
cli-anything-adguardhome --help

# Start interactive REPL mode
cli-anything-adguardhome

# Create a new project
cli-anything-adguardhome project new -o project.json

# Run with JSON output (for agent consumption)
cli-anything-adguardhome --json project info -p project.json
```

### REPL Mode

When invoked without a subcommand, the CLI enters an interactive REPL session:

```bash
cli-anything-adguardhome
# Enter commands interactively with tab-completion and history
```


## Command Groups


### Parental

Parental control.

| Command | Description |
|---------|-------------|



### Safebrowsing

Safe browsing control.

| Command | Description |
|---------|-------------|



### Safesearch

Safe search control.

| Command | Description |
|---------|-------------|




## Examples


### Create a New Project

Create a new adguardhome project file.

```bash
cli-anything-adguardhome project new -o myproject.json
# Or with JSON output for programmatic use
cli-anything-adguardhome --json project new -o myproject.json
```


### Interactive REPL Session

Start an interactive session with undo/redo support.

```bash
cli-anything-adguardhome
# Enter commands interactively
# Use 'help' to see available commands
# Use 'undo' and 'redo' for history navigation
```


## State Management

The CLI maintains session state with:

- **Undo/Redo**: Up to 50 levels of history
- **Project persistence**: Save/load project state as JSON
- **Session tracking**: Track modifications and changes

## Output Formats

All commands support dual output modes:

- **Human-readable** (default): Tables, colors, formatted text
- **Machine-readable** (`--json` flag): Structured JSON for agent consumption

```bash
# Human output
cli-anything-adguardhome project info -p project.json

# JSON output for agents
cli-anything-adguardhome --json project info -p project.json
```

## For AI Agents

When using this CLI programmatically:

1. **Always use `--json` flag** for parseable output
2. **Check return codes** - 0 for success, non-zero for errors
3. **Parse stderr** for error messages on failure
4. **Use absolute paths** for all file operations
5. **Verify outputs exist** after export operations

## More Information

- Full documentation: See README.md in the package
- Test coverage: See TEST.md in the package
- Methodology: See HARNESS.md in the cli-anything-plugin

## Version

1.0.0