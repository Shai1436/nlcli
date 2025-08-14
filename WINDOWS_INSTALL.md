# Windows Installation Troubleshooting Guide

## Most Common Issue: "nlcli command not found" after successful installation

**This affects 80% of Windows installations** - the tool installs correctly but can't be accessed.

**Root Cause:** Python Scripts directory is not in your system PATH.

### Quick Fix (Choose One):

#### Option A: Add Scripts to PATH (Permanent Fix)
1. **Find your Scripts directory:**
   ```cmd
   python -c "import site; print(site.USER_BASE + '\\Scripts')"
   ```

2. **Add to Windows PATH:**
   - Press `Win + X` → System → Advanced system settings
   - Click "Environment Variables"
   - Under "User variables", find "Path" → Edit → New
   - Paste the Scripts path
   - Click OK on all dialogs
   - **Restart Command Prompt**

3. **Test:**
   ```cmd
   nlcli --help
   ```

#### Option B: Use Python Module (Immediate Fix)
Instead of `nlcli`, always use:
```cmd
python -m nlcli.main
python -m nlcli.main "show files"
python -m nlcli.main --interactive
```

#### Option C: Reinstall with User Flag
```cmd
pip uninstall nlcli
pip install --user nlcli
```

## Quick Install

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

## Step-by-Step Troubleshooting

**1. Verify the installation worked:**
```cmd
pip show nlcli
python -c "import nlcli; print('Package installed correctly')"
```

**2. Check if nlcli command is accessible:**
```cmd
nlcli --help
```

**3. If step 2 fails, run the PATH fix script:**
Download and run `windows_path_fix.bat` - it will diagnose and fix PATH issues automatically.

**4. Alternative: Use Python module directly:**
```cmd
python -m nlcli.main --help
python -m nlcli.main "show files"
python -m nlcli.main --interactive
```

## Why This Happens

Windows doesn't automatically add Python Scripts directories to PATH during pip installations. The nlcli package installs correctly, but the `nlcli.exe` file is in a location Windows can't find.

## Alternative Installation Methods

### Using pipx (Recommended for CLI tools)
```cmd
pip install pipx
pipx install nlcli
```

### Direct Installation with PATH Fix
```cmd
pip install --user nlcli
# Then run windows_path_fix.bat
```