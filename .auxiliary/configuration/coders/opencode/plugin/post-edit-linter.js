export const PostEditLinter = async ({ project, directory, worktree, $ }) => {
  return {
    "tool.execute.after": async (input, output) => {
      // Only run linters after write/edit operations
      if (input.tool === "write" || input.tool === "edit") {
        try {
          const result = await $`hatch --env develop run linters`.text();
          if (result.includes("errors") || result.includes("failed")) {
            console.error("Linters failed:", result);
          }
        } catch (err) {
          console.error(`Linters failed: ${err.message}`);
        }
      }
    },
  }
}