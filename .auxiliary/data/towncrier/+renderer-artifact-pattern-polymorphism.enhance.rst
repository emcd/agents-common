Make renderers the authoritative source for distribution artifact file
patterns, mirroring the renderer-owned directory contract from
agentsmgr/18. Adds ``RendererBase.calculate_artifact_pattern(item_type)``
which returns the file glob pattern the renderer uses for artifacts of
that type. Default is ``*.md``; subclasses may override per renderer
per item type for coders whose artifacts use a different file
extension.

Updates ``_detect_orphaned_artifacts`` to delegate to
``renderer.calculate_artifact_pattern(item_type)`` instead of
hardcoding ``*.md``. ``_copy_skills`` is intentionally not updated:
skill files conform to the Skills protocol contract (source ``*.md``
rendered to destination ``SKILL.md``), so the source glob pattern
and the destination filename are coupled and remain protocol-owned.
Future ``agentsmgr/11`` skill-directory support may replace the
flat-file scan with a skill-package abstraction.

The contract returns a single glob expression. Renderers that need
multiple file extensions or sets of patterns would need to widen the
contract (e.g., to ``tuple[str, ...]``); this is intentionally not
done speculatively.
