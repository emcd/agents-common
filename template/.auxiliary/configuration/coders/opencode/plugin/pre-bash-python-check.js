export const PreBashPythonCheck = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (input, output) => {
      // Only check bash commands for Python usage
      if (input.tool === "bash") {
        const command = input.args.command || "";
        const commands = _partitionCommandLine(command);
        
        for (const cmd of commands) {
          _checkDirectPythonUsage(cmd);
          _checkMultilinePythonC(cmd);
          _checkDirectToolUsage(cmd);
        }
      }
    },
  }
}

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

// Basic shell tokenization that handles quotes (similar to Python's shlex.split)
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

function _checkDirectPythonUsage(tokens) {
  const message = (
    "Warning: Direct Python usage detected in command.\n" +
    "Consider using 'hatch run python' or " +
    "'hatch --env develop run python' to ensure dependencies " +
    "are available."
  );
  
  for (const token of tokens) {
    if (token === "hatch") return; // noqa: S105
    if (_isPythonCommand(token)) {
      throw new Error(message);
    }
  }
}

function _checkMultilinePythonC(tokens) {
  const message = (
    "Warning: Multi-line Python script detected in command.\n" +
    "Consider writing the script to a file " +
    "in '.auxiliary/scribbles' directory " +
    "instead of using 'python -c' with multi-line code."
  );
  
  for (let i = 0; i < tokens.length; i++) {
    if (_isPythonCommand(tokens[i]) && _checkPythonCArgument(tokens, i)) {
      throw new Error(message);
    }
    if (!tokens[i].startsWith('-')) {
      break; // Non-option argument, stop looking for -c
    }
  }
}

function _checkDirectToolUsage(tokens) {
  const message = (
    "Warning: Direct Python tool usage detected in command.\n" +
    "Use 'hatch --env develop run {tool}' instead to ensure " +
    "proper environment and configuration."
  );
  
  for (const token of tokens) {
    if (token === "hatch") return; // noqa: S105
    if (_isPythonTool(token)) {
      throw new Error(message.replace("{tool}", token));
    }
  }
}

function _isPythonCommand(token) {
  return ["python", "python3"].includes(token) || 
         token.startsWith("python3.");
}

function _isPythonTool(token) {
  return ["coverage", "pyright", "pytest", "ruff"].includes(token);
}

function _checkPythonCArgument(tokens, pythonIndex) {
  for (let j = pythonIndex + 1; j < tokens.length; j++) {
    if (tokens[j] === "-c" && j + 1 < tokens.length) {
      return true; // Found -c with following argument
    }
    if (!tokens[j].startsWith("-")) {
      break; // Non-option argument, stop looking for -c
    }
  }
  return false;
}