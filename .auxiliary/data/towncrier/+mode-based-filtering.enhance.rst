CLI: Implement mode-based filtering in populate commands.
The populate project and populate user commands now filter coders by their default mode to ensure each command handles only appropriate coders: populate project processes per-project default coders, while populate user processes per-user default coders.
Coder directory symlinks are now only created for coders whose default mode is per-project, preventing dangling symlinks for per-user coders.
