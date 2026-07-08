Fixed ``agentsmgr`` source resolution for Windows absolute local paths, so
drive-letter paths such as ``C:\\...`` are treated as filesystem paths rather
than unsupported URL schemes.
