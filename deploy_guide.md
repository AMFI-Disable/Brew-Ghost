# 🚀 Git Repository Segregation and Deployment Guide

Use these terminal commands in your macOS Zsh shell to isolate, initialize, and push the files to your two separate GitHub repositories: `brew-ghost` and `homebrew-tap`.

---

## 📂 Step 1: Create Isolated Staging Directories
We will clean any previous staging folders on your Desktop and create isolated directory structures.

```zsh
# Clean and create isolated directories on your Desktop
rm -rf ~/Desktop/brew-ghost-staging
mkdir -p ~/Desktop/brew-ghost-staging/brew-ghost
mkdir -p ~/Desktop/brew-ghost-staging/homebrew-tap/Formula
```

---

## 💾 Step 2: Copy Files to Respective Repositories
Copy each file from your project folder to the staging area corresponding to its destination repository.

```zsh
# Copy core application files to the brew-ghost repository
cp /Users/even/Desktop/Projects/Brew-Ghost/ghost.py ~/Desktop/brew-ghost-staging/brew-ghost/
cp /Users/even/Desktop/Projects/Brew-Ghost/readme.md ~/Desktop/brew-ghost-staging/brew-ghost/
cp /Users/even/Desktop/Projects/Brew-Ghost/release.md ~/Desktop/brew-ghost-staging/brew-ghost/
cp /Users/even/Desktop/Projects/Brew-Ghost/test_ghost_exorcise.py ~/Desktop/brew-ghost-staging/brew-ghost/

# Copy the Homebrew Formula to the homebrew-tap repository
cp /Users/even/Desktop/Projects/Brew-Ghost/Formula/brew-ghost.rb ~/Desktop/brew-ghost-staging/homebrew-tap/Formula/
```

---

## 🌐 Step 3: Initialize & Push Repository 1 (`brew-ghost`)
This repository contains the source code, documentation, and tests. We will also create the `V1.0.0` tag required for Homebrew tarball distribution.

```zsh
# Move to the brew-ghost staging directory
cd ~/Desktop/brew-ghost-staging/brew-ghost

# Initialize git, stage files, and commit
git init
git checkout -b main
git add .
git commit -m "feat: initial release of brew-ghost core engine"

# Tag the commit for V1.0.0 release tarball generation
git tag -a V1.0.0 -m "feat: initial tag release"

# Link to GitHub and push main branch + tag
git remote add origin https://github.com/amfi-disable/brew-ghost.git
git push -u origin main
git push origin V1.0.0
```

---

## 🍺 Step 4: Initialize & Push Repository 2 (`homebrew-tap`)
This repository acts as your personal Homebrew Tap distribution endpoint containing the formula file.

```zsh
# Move to the homebrew-tap staging directory
cd ~/Desktop/brew-ghost-staging/homebrew-tap

# Initialize git, stage files, and commit
git init
git checkout -b main
git add .
git commit -m "feat: add custom tap formula for brew-ghost"

# Link to GitHub and push main branch
git remote add origin https://github.com/amfi-disable/homebrew-tap.git
git push -u origin main
```
