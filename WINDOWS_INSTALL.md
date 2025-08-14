# Windows Installation Guide

## Quick Install

1. **Download and run the installer:**
   ```cmd
   curl -O https://raw.githubusercontent.com/your-repo/nlcli/main/install_windows.bat
   install_windows.bat
   ```

2. **Or install manually:**
   ```cmd
   pip install --upgrade pip setuptools wheel
   pip install nlcli
   ```

## Common Issues and Solutions

### Error: "setuptools build_meta.py get_requires_for_build_wheel"

This error typically occurs due to outdated build tools. Fix it with:

```cmd
# Method 1: Upgrade build tools
python -m pip install --upgrade pip setuptools wheel build

# Method 2: Use legacy installer
python -m pip install --use-pep517 nlcli

# Method 3: Install from source
git clone <repository>
cd nlcli
python -m pip install -e .
```

### Error: "Microsoft Visual C++ 14.0 is required"

Install Visual Studio Build Tools:
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "C++ build tools" workload

### Error: "Long path names not supported"

Enable long path support (Windows 10+):
1. Open Group Policy Editor (gpedit.msc)
2. Navigate to: Computer Configuration > Administrative Templates > System > Filesystem
3. Enable "Enable Win32 long paths"

### Error: "Permission denied"

Run as administrator or use user install:
```cmd
pip install --user nlcli
```

## Verification

After installation, verify with:
```cmd
nlcli --version
nlcli "list files"
```

## Uninstall

```cmd
pip uninstall nlcli
```

## Alternative Installation Methods

### Using pipx (Recommended for CLI tools)
```cmd
pip install pipx
pipx install nlcli
```

### Using conda
```cmd
conda install -c conda-forge nlcli
```

### From GitHub
```cmd
pip install git+https://github.com/your-repo/nlcli.git
```