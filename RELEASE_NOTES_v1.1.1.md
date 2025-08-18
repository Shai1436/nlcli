# Release Notes v1.1.1 - Windows Compatibility Fix

**Release Date**: August 18, 2025  
**Type**: Hotfix Release

## 🚀 Critical Fixes

### Windows Installation Issues Resolved
- **Fixed**: Removed problematic dependencies (`fann2`, `padatious`) that caused compilation errors on Windows
- **Fixed**: Cleaned up dependency conflicts that prevented successful installation
- **Fixed**: Streamlined PyPI package to include only essential dependencies
- **Fixed**: Verified Windows PowerShell compatibility (34+ cmdlets, 18+ CMD commands)

## 📦 Installation

### Windows Users (Fixed!)
```powershell
# Uninstall previous broken version
pip uninstall nlcli -y

# Install fixed version
pip install nlcli==1.1.1

# Test installation
nlcli --help
```

### Alternative Installation (if issues persist)
```powershell
pip install --no-deps nlcli==1.1.1
pip install click rich openai psutil
```

## 🔧 Technical Changes

### Dependencies Streamlined
- **Removed**: `fann2`, `padatious`, `anthropic`, `pytest`, `coverage` from core dependencies
- **Core**: Only essential runtime dependencies: `click`, `openai`, `rich`, `psutil`
- **Result**: Clean Windows installation without compilation requirements

### Package Structure
- **Complete**: All 39 Python files included in wheel
- **Modules**: 8 complete submodules (cli, context, execution, pipeline, storage, ui, utils)
- **Compatibility**: Cross-platform Windows/Unix/Linux/macOS support verified

## ✅ Windows PowerShell Support Confirmed

### Windows Commands Working
```powershell
> Get-Process
> dir
> ipconfig
> tasklist
> netstat
> systeminfo
```

### Universal Commands
```powershell
> list files
> network status
> running processes
> disk usage
> find config files
```

## 🧪 Verification

### Installation Test
```powershell
python -c "from nlcli.cli.main import cli; cli()"
```

Should display:
```
Natural Language CLI
Type commands in plain English
Tips: Use arrow keys for history, type 'quit' to exit
>
```

## 📊 Performance

- **Direct Commands**: 534+ supported with sub-1ms response
- **Windows Cmdlets**: 34+ PowerShell commands
- **CMD Commands**: 18+ traditional Windows commands
- **Cross-Platform**: Full Unix/Linux compatibility maintained

## 🚨 Migration from v1.1.0

If you have v1.1.0 installed and experiencing issues:

```powershell
pip uninstall nlcli -y
pip cache purge
pip install nlcli==1.1.1
```

## 🐛 Known Issues Resolved

- ❌ ~~`fann2` compilation errors on Windows~~
- ❌ ~~`ModuleNotFoundError: No module named 'padatious'`~~
- ❌ ~~Windows PowerShell command detection failing~~
- ✅ All Windows compatibility issues resolved

## 📈 What's Next

- v1.2.0: Enhanced context awareness
- Advanced pattern learning
- Enterprise SaaS features

---

**Support**: For issues, contact the development team or open a GitHub issue.