export const PostEditLinter = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.after": async (input, output) => {
      // Only run linters after write/edit operations
      if (input.tool === "write" || input.tool === "edit") {
        try {
          const result = await $`hatch --env develop run linters`.quiet();
          if (result.exitCode !== 0) {
            // Combine stdout and stderr since linting output may go to stdout
            const resultText = `${result.stdout}\n\n${result.stderr}`.trim();
            console.error(resultText);
            throw new Error("Linters failed");
          }
        } catch (err) {
          if (err.message !== "Linters failed") {
            console.error(`Linters failed: ${err.message}`);
          }
          throw err;
        }
      }
    },
  }
}