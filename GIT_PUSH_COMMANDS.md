# Git Push Commands - Quick Reference

**Use these commands every time you want to push code to GitHub**

---

## 🚀 Regular Push (After Making Changes)

```powershell
# Navigate to project
cd "D:\Major Project"

# Check what changed
git status

# Add all changes
git add -A

# Commit with message
git commit -m "Your commit message here"

# Push to GitHub
git push
```

---

## 📋 Step-by-Step Breakdown

### 1. Check Status (See what changed)
```powershell
git status
```
Shows:
- Modified files (red = not staged)
- New files (red = untracked)
- Deleted files

### 2. Add Files to Commit
```powershell
# Add ALL changes
git add -A

# OR add specific file
git add filename.py

# OR add specific folder
git add src/
```

### 3. Commit Changes
```powershell
# Good commit message format:
git commit -m "fix: Fixed camera detection bug"
git commit -m "feat: Added new violence detection rule"
git commit -m "docs: Updated README with examples"
git commit -m "refactor: Cleaned up server.py code"
```

**Commit Message Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code cleanup
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 4. Push to GitHub
```powershell
git push
```

---

## ⚡ Quick One-Liner (Use Carefully!)

```powershell
cd "D:\Major Project"; git add -A; git commit -m "Update code"; git push
```

⚠️ **Warning:** This commits everything without review. Better to check first!

---

## 🔄 Complete Workflow Example

```powershell
# 1. Go to project
cd "D:\Major Project"

# 2. See what you changed
git status
git diff

# 3. Add your changes
git add -A

# 4. Commit with good message
git commit -m "feat: Added weapon detection rule"

# 5. Push to GitHub
git push
```

---

## 📊 Before Pushing - Good Practices

### Always Check First
```powershell
# See what files changed
git status

# See what code changed
git diff

# See recent commits
git log --oneline -5
```

### Make Sure Everything Works
```powershell
# Run tests
python -m unittest discover tests

# Check for syntax errors
python -m py_compile src/*.py
```

---

## 🆘 Common Situations

### Situation 1: First Time Pushing (Already Done!)
```powershell
git remote add origin https://github.com/dhruvkasar/autoguard.git
git branch -M main
git push -u origin main
```
✅ You only do this ONCE when setting up the repo!

---

### Situation 2: Regular Updates (Use This!)
```powershell
cd "D:\Major Project"
git add -A
git commit -m "Your message"
git push
```
✅ Use this every time you make changes!

---

### Situation 3: Added New Files
```powershell
# Git automatically tracks new files with git add -A
git add -A
git commit -m "feat: Added new detection module"
git push
```

---

### Situation 4: Modified Existing Files
```powershell
git add -A
git commit -m "fix: Fixed bug in detector.py"
git push
```

---

### Situation 5: Deleted Files
```powershell
# Git tracks deletions too
git add -A
git commit -m "chore: Removed old test files"
git push
```

---

## ❌ Common Errors & Fixes

### Error: "Your branch is ahead of 'origin/main'"
**Meaning:** You have local commits not pushed yet  
**Fix:**
```powershell
git push
```

---

### Error: "Your branch is behind 'origin/main'"
**Meaning:** Someone else pushed changes  
**Fix:**
```powershell
git pull
# Then fix any conflicts if needed
git push
```

---

### Error: "fatal: The current branch has no upstream"
**Fix:**
```powershell
git push -u origin main
```

---

### Error: "Updates were rejected"
**Meaning:** Remote has changes you don't have  
**Fix:**
```powershell
# Get remote changes first
git pull --rebase

# Then push
git push
```

---

### Error: "Authentication failed"
**Fix:**
```powershell
# Use GitHub token, not password
# Generate at: https://github.com/settings/tokens
```

---

## 🎯 Daily Workflow (Recommended)

### Morning - Start Working
```powershell
cd "D:\Major Project"

# Get latest changes (if working with team)
git pull

# Check status
git status
```

### During Work - Make Changes
```powershell
# Edit files in your editor...
# Test your changes...
```

### Before Lunch/Break - Save Progress
```powershell
git add -A
git commit -m "wip: Working on feature X"
git push
```

### End of Day - Final Push
```powershell
# Make sure everything works
python -m unittest discover tests

# Push all changes
git add -A
git commit -m "feat: Completed feature X, all tests passing"
git push
```

---

## 📝 Commit Message Best Practices

### Good Commit Messages ✅
```powershell
git commit -m "feat: Add weapon detection using YOLOv8"
git commit -m "fix: Camera not opening on startup"
git commit -m "docs: Update API documentation with new endpoints"
git commit -m "refactor: Simplify evidence capture logic"
git commit -m "test: Add unit tests for behavioral rules"
```

### Bad Commit Messages ❌
```powershell
git commit -m "changes"
git commit -m "fix"
git commit -m "update"
git commit -m "asdfasdf"
git commit -m "final version"
git commit -m "final version 2"
git commit -m "final version 3 for real this time"
```

---

## 🔍 Useful Git Commands

### Check History
```powershell
# Last 10 commits
git log --oneline -10

# See what changed in last commit
git show

# See all branches
git branch -a
```

### Undo Mistakes (Before Push)
```powershell
# Undo last commit but keep changes
git reset --soft HEAD~1

# Undo changes to a file
git checkout -- filename.py

# Discard ALL local changes (careful!)
git reset --hard HEAD
```

### See Differences
```powershell
# See all changes not committed
git diff

# See changes in specific file
git diff src/detector.py

# See what will be committed
git diff --staged
```

---

## 🎓 Git Workflow Summary

```
1. Make changes to files
   ↓
2. git status (see what changed)
   ↓
3. git add -A (stage changes)
   ↓
4. git commit -m "message" (save locally)
   ↓
5. git push (send to GitHub)
```

---

## ⚡ Super Quick Reference Card

```powershell
# THE 4 COMMANDS YOU'LL USE 95% OF THE TIME:

git status              # See what changed
git add -A              # Add all changes
git commit -m "msg"     # Save changes
git push                # Upload to GitHub
```

---

## 📱 Save This Cheat Sheet

**Bookmark this file!** You'll use these commands every time you code.

**Location:** `D:\Major Project\GIT_PUSH_COMMANDS.md`

---

## 🚀 Your Typical Push Routine

Every time you finish working:

```powershell
# 1. Go to project folder
cd "D:\Major Project"

# 2. Check what you changed
git status

# 3. Add everything
git add -A

# 4. Commit with message
git commit -m "feat: Describe what you did"

# 5. Push to GitHub
git push

# Done! ✅
```

---

**Time to push:** ~30 seconds  
**Frequency:** Every time you make significant changes  
**Recommendation:** Push at least once per day (end of coding session)

---

**Last Updated:** August 28, 2026  
**Your Repo:** https://github.com/dhruvkasar/autoguard
