# Git Workflow: Syncing Latest Changes to Main

You're currently on `chore/bug-fixes` branch with uncommitted changes. Here's how to get everything synced to main:

## Option 1: Commit on Current Branch, Then Merge to Main (Recommended)

```bash
# 1. Stage all changes
git add .

# 2. Commit with the message from commit-message.txt
git commit -F commit-message.txt

# 3. Push the branch
git push origin chore/bug-fixes

# 4. Switch to main
git checkout main

# 5. Pull latest changes from GitHub
git pull origin main

# 6. Merge your branch into main
git merge chore/bug-fixes

# 7. Push to GitHub
git push origin main
```

## Option 2: Switch to Main, Pull, Then Create New Branch

```bash
# 1. Stash your current changes
git stash

# 2. Switch to main
git checkout main

# 3. Pull latest from GitHub
git pull origin main

# 4. Create a new branch for these fixes
git checkout -b fix/favicon-and-tailwind-docs

# 5. Apply your stashed changes
git stash pop

# 6. Stage and commit
git add .
git commit -F commit-message.txt

# 7. Push the new branch
git push origin fix/favicon-and-tailwind-docs

# 8. Create PR on GitHub, then merge to main
```

## Option 3: Direct Commit to Main (If You Have Direct Access)

```bash
# 1. Switch to main
git checkout main

# 2. Pull latest
git pull origin main

# 3. Cherry-pick or merge your changes
# (You'll need to handle the uncommitted changes first)

# 4. Stage and commit
git add .
git commit -F commit-message.txt

# 5. Push
git push origin main
```

## Recommended: Option 1

Since you already have a branch, Option 1 is cleanest:
1. Commit your changes to the current branch
2. Merge that branch into main
3. Push main to GitHub

This keeps your history clean and allows for PR review if needed.

