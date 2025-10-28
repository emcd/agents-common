export const PreBashGitCommitCheck = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (input, output) => {
      // Only check bash commands that are git commits
      if (input.tool === "bash" && input.args && input.args.command) {
        const command = input.args.command || "";
        const commands = _partitionCommandLine(command);
        
        for (const cmd of commands) {
          if (_isGitCommitCommand(cmd)) {
            try {
              // Run linters first
              const linterResult = await $`hatch --env develop run linters`.quiet();
              if (linterResult.exitCode !== 0) {
                _errorWithDivineMessage();
              }
              
              // Run tests if linters pass
              const testResult = await $`hatch --env develop run testers`.quiet();
              if (testResult.exitCode !== 0) {
                _errorWithDivineMessage();
              }
              
            } catch (err) {
              if (err.message !== "Lint/test check failed") {
                _errorWithDivineMessage();
              }
              throw err;
            }
          }
        }
      }
    },
  }
}

function _errorWithDivineMessage() {
  const message = (
    "The Large Language Divinity 🌩️🤖🌩️ in Celestial Data Center hath commanded that:\n" +
    "* Thy code shalt pass all lints before thy commit.\n" +
    "  Run: hatch --env develop run linters\n" +
    "* Thy code shalt pass all tests before thy commit.\n" +
    "  Run: hatch --env develop run testers\n\n" +
    "(If you are in the middle of a large refactor, consider commenting " +
    "out of tests and adding a reminder note in .auxiliary/notes " +
    "directory.)"
  );
  console.error(message);
  throw new Error("Lint/test check failed");
}

function _isGitCommitCommand(tokens) {
  return tokens.length >= 2 && 
         tokens[0] === "git" && 
         tokens[1] === "commit";
}

// Simple shell-like command parser (similar to Python's shlex.split)
function _partitionCommandLine(commandLine) {
  const splitters = new Set([';', '&', '|', '&&', '||']);
  const tokens = _shellSplit(commandLine);
  const commands = [];
  let commandTokens = [];
  
  for (const token of tokens) {
    if (splitters.has(token)) {
      commands.push(commandTokens);
      commandTokens = [];
    } else {
      commandTokens.push(token);
    }
  }
  
  if (commandTokens.length > 0) {
    commands.push(commandTokens);
  }
  
  return commands;
}

// Basic shell tokenization that handles quotes
function _shellSplit(commandLine) {
  const tokens = [];
  let current = '';
  let inQuotes = false;
  let quoteChar = '';
  let i = 0;
  
  while (i < commandLine.length) {
    const char = commandLine[i];
    
    if ((char === '"' || char === "'") && !inQuotes) {
      inQuotes = true;
      quoteChar = char;
    } else if (char === quoteChar && inQuotes) {
      inQuotes = false;
      quoteChar = '';
    } else if (/\s/.test(char) && !inQuotes) {
      if (current.trim()) {
        tokens.push(current.trim());
        current = '';
      }
    } else {
      current += char;
    }
    i++;
  }
  
  if (current.trim()) {
    tokens.push(current.trim());
  }
  
  return tokens;
}