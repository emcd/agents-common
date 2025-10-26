CLI: Add source data structure validation to populate commands.
The populate project and populate user commands now validate that the source location contains the required directory structure before attempting population.
Invalid source structures produce clear error messages listing all missing required directories, allowing graceful failure instead of silently generating no items.
