CLI: Implement managed block for Git exclude entries.
Git exclude entries are now managed within a clearly-marked, lexicographically sorted managed block with BEGIN/END markers.
This ensures complete block replacement on each update, naturally handling entry removals and preventing accumulation of unnecessary blank lines.
