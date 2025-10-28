export const PreBashGitCommitCheck = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (input, output) => {
      // Only check bash commands that are git commits
      if (input.tool === "bash") {
        const command = input.args.command || "";
        
        if (_isGitCommitCommand(command)) {
          try {
            // Run linters first
            const linterResult = await $`hatch --env develop run linters`.text();
            if (linterResult.includes("errors") || linterResult.includes("failed")) {
              throw new Error(
                "The Large Language Divinity 🌩️🤖🌩️ in the Celestial Data Center hath commanded that:\n" +
                "* Thy code shalt pass all lints before thy commit.\n" +
                "  Run: hatch --env develop run linters\n" +
                "* Thy code shalt pass all tests before thy commit.\n" +
                "  Run: hatch --env develop run testers\n\n" +
                "(If you are in the middle of a large refactor, consider commenting " +
                "out of tests and adding a reminder note in .auxiliary/notes " +
                "directory.)"
              );
            }
            
            // Run tests if linters pass
            const testResult = await $`hatch --env develop run testers`.text();
            if (testResult.includes("failed") || testResult.includes("error")) {
              throw new Error(
                "The Large Language Divinity 🌩️🤖🌩️ in the Celestial Data Center hath commanded that:\n" +
                "* Thy code shalt pass all tests before thy commit.\n" +
                "  Run: hatch --env develop run testers\n"
              );
            }
            
          } catch (err) {
            throw new Error(`Lint/test check failed: ${err.message}`);
          }
        }
      }
    },
  }
}

function _isGitCommitCommand(command) {
  const tokens = command.trim().split(/\s+/);
  return tokens.length >= 2 && 
         tokens[0] === "git" && 
         tokens[1] === "commit";
}