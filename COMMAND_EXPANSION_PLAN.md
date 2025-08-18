# Command Filter Expansion Plan
## Comprehensive Coverage for All OS/Shell Combinations

**Current Status:**
- Cross-platform commands: ~95
- Command variations: ~25
- Total current: ~119 commands
- Target: 500+ commands for comprehensive coverage

## Phase 1: Essential Missing Commands

### A. File System Operations (Missing ~40 commands)
```python
# Basic file operations
'stat': {'command': 'stat', 'explanation': 'Display file/filesystem status', 'confidence': 1.0},
'file': {'command': 'file', 'explanation': 'Determine file type', 'confidence': 1.0},
'ln': {'command': 'ln', 'explanation': 'Create links between files', 'confidence': 1.0},
'readlink': {'command': 'readlink', 'explanation': 'Display symbolic link target', 'confidence': 1.0},
'basename': {'command': 'basename', 'explanation': 'Extract filename from path', 'confidence': 1.0},
'dirname': {'command': 'dirname', 'explanation': 'Extract directory from path', 'confidence': 1.0},
'realpath': {'command': 'realpath', 'explanation': 'Print absolute pathname', 'confidence': 1.0},

# Extended file operations
'dd': {'command': 'dd', 'explanation': 'Convert and copy files with options', 'confidence': 0.9},
'sync': {'command': 'sync', 'explanation': 'Flush filesystem buffers', 'confidence': 1.0},
'fsync': {'command': 'fsync', 'explanation': 'Synchronize file to disk', 'confidence': 1.0},

# Directory operations
'pushd': {'command': 'pushd', 'explanation': 'Push directory to stack and change', 'confidence': 1.0},
'popd': {'command': 'popd', 'explanation': 'Pop directory from stack', 'confidence': 1.0},
'dirs': {'command': 'dirs', 'explanation': 'Display directory stack', 'confidence': 1.0},

# File searching and finding
'updatedb': {'command': 'updatedb', 'explanation': 'Update locate database', 'confidence': 1.0},
'xargs': {'command': 'xargs', 'explanation': 'Build and execute commands from input', 'confidence': 1.0},
```

### B. Process Management (Missing ~35 commands)
```python
# Process information
'pstree': {'command': 'pstree', 'explanation': 'Display process tree', 'confidence': 1.0},
'lscpu': {'command': 'lscpu', 'explanation': 'Display CPU information', 'confidence': 1.0},
'lsblk': {'command': 'lsblk', 'explanation': 'List block devices', 'confidence': 1.0},
'lspci': {'command': 'lspci', 'explanation': 'List PCI devices', 'confidence': 1.0},
'lsusb': {'command': 'lsusb', 'explanation': 'List USB devices', 'confidence': 1.0},
'lsmod': {'command': 'lsmod', 'explanation': 'Show status of kernel modules', 'confidence': 1.0},

# System monitoring
'sar': {'command': 'sar', 'explanation': 'System activity reporter', 'confidence': 1.0},
'iostat': {'command': 'iostat', 'explanation': 'I/O statistics', 'confidence': 1.0},
'vmstat': {'command': 'vmstat', 'explanation': 'Virtual memory statistics', 'confidence': 1.0},
'dmesg': {'command': 'dmesg', 'explanation': 'Display kernel message buffer', 'confidence': 1.0},
'journalctl': {'command': 'journalctl', 'explanation': 'Query systemd journal', 'confidence': 1.0},

# Process control
'screen': {'command': 'screen', 'explanation': 'Terminal multiplexer', 'confidence': 1.0},
'tmux': {'command': 'tmux', 'explanation': 'Terminal multiplexer', 'confidence': 1.0},
'at': {'command': 'at', 'explanation': 'Schedule commands for later execution', 'confidence': 1.0},
'crontab': {'command': 'crontab', 'explanation': 'Schedule recurring tasks', 'confidence': 0.9},
'batch': {'command': 'batch', 'explanation': 'Execute commands when load permits', 'confidence': 1.0},
```

### C. Network Commands (Missing ~45 commands)
```python
# Network diagnostics
'tracepath': {'command': 'tracepath', 'explanation': 'Trace network path to host', 'confidence': 1.0},
'mtr': {'command': 'mtr', 'explanation': 'Network diagnostic tool', 'confidence': 1.0},
'nslookup': {'command': 'nslookup', 'explanation': 'DNS lookup utility', 'confidence': 1.0},
'dig': {'command': 'dig', 'explanation': 'DNS lookup tool', 'confidence': 1.0},
'host': {'command': 'host', 'explanation': 'DNS lookup utility', 'confidence': 1.0},
'whois': {'command': 'whois', 'explanation': 'Domain registration lookup', 'confidence': 1.0},

# Network configuration
'route': {'command': 'route', 'explanation': 'Show/manipulate IP routing table', 'confidence': 1.0},
'arp': {'command': 'arp', 'explanation': 'Display/modify ARP cache', 'confidence': 1.0},
'iwconfig': {'command': 'iwconfig', 'explanation': 'Configure wireless interface', 'confidence': 1.0},
'ethtool': {'command': 'ethtool', 'explanation': 'Display/modify ethernet settings', 'confidence': 1.0},

# Network monitoring
'iftop': {'command': 'iftop', 'explanation': 'Display bandwidth usage', 'confidence': 1.0},
'nethogs': {'command': 'nethogs', 'explanation': 'Process network usage monitor', 'confidence': 1.0},
'tcpdump': {'command': 'tcpdump', 'explanation': 'Network packet analyzer', 'confidence': 0.9},
'wireshark': {'command': 'wireshark', 'explanation': 'Network protocol analyzer', 'confidence': 0.9},
'nmap': {'command': 'nmap', 'explanation': 'Network discovery and security scanner', 'confidence': 0.8},

# File transfer
'ftp': {'command': 'ftp', 'explanation': 'File Transfer Protocol client', 'confidence': 1.0},
'sftp': {'command': 'sftp', 'explanation': 'Secure File Transfer Protocol', 'confidence': 1.0},
'nc': {'command': 'nc', 'explanation': 'Netcat networking utility', 'confidence': 0.9},
'socat': {'command': 'socat', 'explanation': 'Socket data relay tool', 'confidence': 0.9},
```

### D. Text Processing (Missing ~30 commands)
```python
# Advanced text processing
'tee': {'command': 'tee', 'explanation': 'Write output to both file and stdout', 'confidence': 1.0},
'column': {'command': 'column', 'explanation': 'Format input into columns', 'confidence': 1.0},
'comm': {'command': 'comm', 'explanation': 'Compare sorted files line by line', 'confidence': 1.0},
'diff': {'command': 'diff', 'explanation': 'Compare files line by line', 'confidence': 1.0},
'patch': {'command': 'patch', 'explanation': 'Apply diff patches to files', 'confidence': 0.9},
'split': {'command': 'split', 'explanation': 'Split file into pieces', 'confidence': 1.0},
'join': {'command': 'join', 'explanation': 'Join lines based on common field', 'confidence': 1.0},
'paste': {'command': 'paste', 'explanation': 'Merge lines from files', 'confidence': 1.0},
'fold': {'command': 'fold', 'explanation': 'Wrap lines to specified width', 'confidence': 1.0},
'expand': {'command': 'expand', 'explanation': 'Convert tabs to spaces', 'confidence': 1.0},
'unexpand': {'command': 'unexpand', 'explanation': 'Convert spaces to tabs', 'confidence': 1.0},

# String manipulation
'strings': {'command': 'strings', 'explanation': 'Extract printable strings', 'confidence': 1.0},
'od': {'command': 'od', 'explanation': 'Dump files in octal/hex format', 'confidence': 1.0},
'hexdump': {'command': 'hexdump', 'explanation': 'Display file in hex format', 'confidence': 1.0},
'base64': {'command': 'base64', 'explanation': 'Base64 encode/decode', 'confidence': 1.0},

# Stream editors
'ex': {'command': 'ex', 'explanation': 'Line editor (vi/vim)', 'confidence': 1.0},
'ed': {'command': 'ed', 'explanation': 'Line-oriented text editor', 'confidence': 1.0},
```

## Phase 2: Platform-Specific Extensions

### A. Windows PowerShell/CMD Commands (~80 commands)
```python
# Windows-specific (if platform == 'windows')
# File operations
'attrib': {'command': 'attrib', 'explanation': 'Display/change file attributes', 'confidence': 1.0},
'xcopy': {'command': 'xcopy', 'explanation': 'Extended copy command', 'confidence': 1.0},
'robocopy': {'command': 'robocopy', 'explanation': 'Robust file copy utility', 'confidence': 1.0},
'fc': {'command': 'fc', 'explanation': 'Compare files', 'confidence': 1.0},
'comp': {'command': 'comp', 'explanation': 'Compare files byte by byte', 'confidence': 1.0},

# System information
'systeminfo': {'command': 'systeminfo', 'explanation': 'Display system information', 'confidence': 1.0},
'msinfo32': {'command': 'msinfo32', 'explanation': 'System Information utility', 'confidence': 1.0},
'dxdiag': {'command': 'dxdiag', 'explanation': 'DirectX diagnostic tool', 'confidence': 1.0},
'wmic': {'command': 'wmic', 'explanation': 'Windows Management Interface', 'confidence': 0.9},

# Network
'netsh': {'command': 'netsh', 'explanation': 'Network configuration utility', 'confidence': 0.9},
'nslookup': {'command': 'nslookup', 'explanation': 'DNS lookup tool', 'confidence': 1.0},
'tracert': {'command': 'tracert', 'explanation': 'Trace route to destination', 'confidence': 1.0},
'arp': {'command': 'arp', 'explanation': 'Address Resolution Protocol utility', 'confidence': 1.0},

# PowerShell cmdlets
'Get-Process': {'command': 'Get-Process', 'explanation': 'Get running processes', 'confidence': 1.0},
'Get-Service': {'command': 'Get-Service', 'explanation': 'Get Windows services', 'confidence': 1.0},
'Get-ChildItem': {'command': 'Get-ChildItem', 'explanation': 'Get directory contents', 'confidence': 1.0},
'Set-Location': {'command': 'Set-Location', 'explanation': 'Change directory', 'confidence': 1.0},
'Copy-Item': {'command': 'Copy-Item', 'explanation': 'Copy files/directories', 'confidence': 1.0},
'Move-Item': {'command': 'Move-Item', 'explanation': 'Move/rename items', 'confidence': 1.0},
'Remove-Item': {'command': 'Remove-Item', 'explanation': 'Delete items', 'confidence': 0.9},
'New-Item': {'command': 'New-Item', 'explanation': 'Create new item', 'confidence': 1.0},
```

### B. macOS-Specific Commands (~30 commands)
```python
# macOS-specific (if platform == 'darwin')
'open': {'command': 'open', 'explanation': 'Open files/applications', 'confidence': 1.0},
'pbcopy': {'command': 'pbcopy', 'explanation': 'Copy to clipboard', 'confidence': 1.0},
'pbpaste': {'command': 'pbpaste', 'explanation': 'Paste from clipboard', 'confidence': 1.0},
'defaults': {'command': 'defaults', 'explanation': 'Access user defaults system', 'confidence': 0.9},
'diskutil': {'command': 'diskutil', 'explanation': 'Disk utility', 'confidence': 0.9},
'hdiutil': {'command': 'hdiutil', 'explanation': 'Disk image utility', 'confidence': 0.9},
'launchctl': {'command': 'launchctl', 'explanation': 'Launch daemon control', 'confidence': 0.9},
'sw_vers': {'command': 'sw_vers', 'explanation': 'macOS version information', 'confidence': 1.0},
'system_profiler': {'command': 'system_profiler', 'explanation': 'System information', 'confidence': 1.0},
'dscl': {'command': 'dscl', 'explanation': 'Directory Service command line', 'confidence': 0.8},
'plutil': {'command': 'plutil', 'explanation': 'Property list utility', 'confidence': 1.0},
'mdls': {'command': 'mdls', 'explanation': 'List metadata attributes', 'confidence': 1.0},
'mdfind': {'command': 'mdfind', 'explanation': 'Spotlight search', 'confidence': 1.0},
```

## Phase 3: Command Variations & Arguments (~200 variations)

### A. Common Command + Argument Combinations
```python
# ls variations
'ls -la': {'command': 'ls -la', 'explanation': 'List all files with details', 'confidence': 1.0},
'ls -lh': {'command': 'ls -lh', 'explanation': 'List files with human-readable sizes', 'confidence': 1.0},
'ls -lt': {'command': 'ls -lt', 'explanation': 'List files sorted by modification time', 'confidence': 1.0},
'ls -lS': {'command': 'ls -lS', 'explanation': 'List files sorted by size', 'confidence': 1.0},
'ls -R': {'command': 'ls -R', 'explanation': 'List files recursively', 'confidence': 1.0},

# ps variations  
'ps aux': {'command': 'ps aux', 'explanation': 'Show all processes with details', 'confidence': 1.0},
'ps -ef': {'command': 'ps -ef', 'explanation': 'Show all processes full format', 'confidence': 1.0},
'ps -u': {'command': 'ps -u', 'explanation': 'Show processes for user', 'confidence': 1.0},

# find variations
'find . -name': {'command': 'find . -name', 'explanation': 'Find files by name pattern', 'confidence': 1.0},
'find . -type f': {'command': 'find . -type f', 'explanation': 'Find only files', 'confidence': 1.0},
'find . -type d': {'command': 'find . -type d', 'explanation': 'Find only directories', 'confidence': 1.0},
'find . -size': {'command': 'find . -size', 'explanation': 'Find files by size', 'confidence': 1.0},
'find . -mtime': {'command': 'find . -mtime', 'explanation': 'Find files by modification time', 'confidence': 1.0},

# grep variations
'grep -r': {'command': 'grep -r', 'explanation': 'Search recursively', 'confidence': 1.0},
'grep -i': {'command': 'grep -i', 'explanation': 'Case-insensitive search', 'confidence': 1.0},
'grep -v': {'command': 'grep -v', 'explanation': 'Invert match (show non-matching)', 'confidence': 1.0},
'grep -n': {'command': 'grep -n', 'explanation': 'Show line numbers', 'confidence': 1.0},
'grep -c': {'command': 'grep -c', 'explanation': 'Count matching lines', 'confidence': 1.0},

# tar variations
'tar -xzf': {'command': 'tar -xzf', 'explanation': 'Extract gzipped tar archive', 'confidence': 1.0},
'tar -czf': {'command': 'tar -czf', 'explanation': 'Create gzipped tar archive', 'confidence': 1.0},
'tar -xjf': {'command': 'tar -xjf', 'explanation': 'Extract bzip2 tar archive', 'confidence': 1.0},
'tar -cjf': {'command': 'tar -cjf', 'explanation': 'Create bzip2 tar archive', 'confidence': 1.0},
'tar -tf': {'command': 'tar -tf', 'explanation': 'List contents of tar archive', 'confidence': 1.0},

# Network command variations
'ping -c': {'command': 'ping -c', 'explanation': 'Ping with count limit', 'confidence': 1.0},
'curl -O': {'command': 'curl -O', 'explanation': 'Download file keeping name', 'confidence': 1.0},
'curl -L': {'command': 'curl -L', 'explanation': 'Follow redirects', 'confidence': 1.0},
'wget -r': {'command': 'wget -r', 'explanation': 'Recursive download', 'confidence': 1.0},
'wget -c': {'command': 'wget -c', 'explanation': 'Continue partial download', 'confidence': 1.0},

# System monitoring variations
'top -u': {'command': 'top -u', 'explanation': 'Show processes for specific user', 'confidence': 1.0},
'df -h': {'command': 'df -h', 'explanation': 'Show disk usage human-readable', 'confidence': 1.0},
'du -sh': {'command': 'du -sh', 'explanation': 'Show directory size summary', 'confidence': 1.0},
'free -h': {'command': 'free -h', 'explanation': 'Show memory usage human-readable', 'confidence': 1.0},
```

## Phase 4: Shell-Specific Commands

### A. Bash-specific
```python
'history': {'command': 'history', 'explanation': 'Show command history', 'confidence': 1.0},
'alias': {'command': 'alias', 'explanation': 'Create command aliases', 'confidence': 1.0},
'unalias': {'command': 'unalias', 'explanation': 'Remove command aliases', 'confidence': 1.0},
'export': {'command': 'export', 'explanation': 'Set environment variables', 'confidence': 1.0},
'source': {'command': 'source', 'explanation': 'Execute script in current shell', 'confidence': 1.0},
'type': {'command': 'type', 'explanation': 'Display command type', 'confidence': 1.0},
'help': {'command': 'help', 'explanation': 'Display help for built-in commands', 'confidence': 1.0},
```

### B. Zsh-specific
```python
'autoload': {'command': 'autoload', 'explanation': 'Mark functions for autoloading', 'confidence': 1.0},
'compinit': {'command': 'compinit', 'explanation': 'Initialize completion system', 'confidence': 1.0},
'rehash': {'command': 'rehash', 'explanation': 'Rebuild command hash table', 'confidence': 1.0},
```

## Implementation Strategy

### Phase 1 (Immediate): Essential Missing Commands
- Target: Add 150 essential commands
- Focus: File system, process management, networking basics
- Timeline: 1-2 development sessions

### Phase 2 (Short-term): Platform-Specific Extensions  
- Target: Add 110 platform-specific commands
- Focus: Windows PowerShell, macOS utilities, Linux distributions
- Timeline: 2-3 development sessions

### Phase 3 (Medium-term): Command Variations
- Target: Add 200 command+argument combinations
- Focus: Most common usage patterns
- Timeline: 3-4 development sessions

### Phase 4 (Long-term): Shell Optimization
- Target: Add 40 shell-specific commands
- Focus: Bash, Zsh, PowerShell built-ins
- Timeline: 1-2 development sessions

## Expected Outcomes
- **Current**: ~119 commands
- **Target**: 500+ commands (400% increase)
- **Coverage**: 95%+ of common terminal operations
- **Performance**: Sub-5ms recognition for all direct commands
- **Enterprise Readiness**: Comprehensive command support across all major platforms

## Testing Strategy
1. Automated testing for each command category
2. Cross-platform validation
3. Performance benchmarking
4. User acceptance testing with real-world scenarios