# 🚀 Git Repository Segregation And Deployment Guide

Use these terminal commands in your macOS Zsh shell to isolate, initialize, and push the files to your two separate GitHub repositories: `Brew-Ghost` and `Homebrew-Tap`.

---

## 📂 Step 1: Create Isolated Staging Directories

We will clean any previous staging folders on your Desktop and create isolated directory structures.

```zsh
# Clean and create isolated directories on your Desktop
rm -rf ~/Desktop/brew-ghost-staging
mkdir -p ~/Desktop/brew-ghost-staging/Brew-Ghost
mkdir -p ~/Desktop/brew-ghost-staging/Homebrew-Tap/Formula
```

---

## 💾 Step 2: Copy Files To Respective Repositories

Copy each file from your project folder to the staging area corresponding to its destination repository.

```zsh
# Copy core application files to the Brew-Ghost repository
cp /Users/even/Desktop/Projects/Tooling/Brew-Ghost/ghost.py ~/Desktop/brew-ghost-staging/Brew-Ghost/
cp /Users/even/Desktop/Projects/Tooling/Brew-Ghost/readme.md ~/Desktop/brew-ghost-staging/Brew-Ghost/
cp /Users/even/Desktop/Projects/Tooling/Brew-Ghost/release.md ~/Desktop/brew-ghost-staging/Brew-Ghost/
cp /Users/even/Desktop/Projects/Tooling/Brew-Ghost/test_ghost_exorcise.py ~/Desktop/brew-ghost-staging/Brew-Ghost/

# Copy the Homebrew Formula to the Homebrew-Tap repository
cp /Users/even/Desktop/Projects/Tooling/Brew-Ghost/formula/brew-ghost.rb ~/Desktop/brew-ghost-staging/Homebrew-Tap/Formula/
```

---

## 🌐 Step 3: Initialize & Push Repository 1 (`Brew-Ghost`)

This repository contains the source code, documentation, and tests. We will also create the `v1.0.0` tag required for Homebrew tarball distribution.

```zsh
# Move to the Brew-Ghost staging directory
cd ~/Desktop/brew-ghost-staging/Brew-Ghost

# Initialize git, stage files, and commit
git init
git checkout -b main
git add .
git commit -m "feat: release core engine"

# Tag the commit for v1.0.0 release tarball generation
git tag -a v1.0.0 -m "feat: release initial tag"

# Link to GitHub and push main branch + tag
git remote add origin https://github.com/AMFI-Disable/Brew-Ghost.git
git push -u origin main
git push origin v1.0.0
```

---

## 🍺 Step 4: Initialize & Push Repository 2 (`Homebrew-Tap`)

This repository acts as your personal Homebrew Tap distribution endpoint containing the formula file.

```zsh
# Move to the Homebrew-Tap staging directory
cd ~/Desktop/brew-ghost-staging/Homebrew-Tap

# Initialize git, stage files, and commit
git init
git checkout -b main
git add .
git commit -m "feat: add tap formula"

# Link to GitHub and push main branch
git remote add origin https://github.com/AMFI-Disable/Homebrew-Tap.git
git push -u origin main
```
