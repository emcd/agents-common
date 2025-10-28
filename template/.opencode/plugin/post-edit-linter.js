export const PostEditLinter = async ({ project, client, $, directory, worktree }) => {
  console.log("Post-edit linter plugin initialized!")

  return {
    tool: {
      "tool.execute.after": async (input, output) => {
        // Only run linters after file write/edit operations
        if (input.tool === "write" || input.tool === "edit") {
          console.log(`Running linters after ${input.tool} operation...`);
          
          try {
            const result = await $`hatch --env develop run linters`.text();
            console.log(result);
          } catch (err) {
            console.error(`Linters failed: ${err.message}`);
            // Don't block the operation, just log the error
          }
        }
      },
    },
  }
}