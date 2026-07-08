# 📦 Step-by-Step Release Protocol (`V1.0.0`)

Follow this guide to package, hash, and publish the first release of `brew-ghost` to your custom Homebrew Tap.

---

## 🛠 Prerequisites

Ensure you have created two public GitHub repositories:
1. `https://github.com/amfi-disable/brew-ghost` (holds the application code)
2. `https://github.com/amfi-disable/homebrew-tap` (holds your custom formula)

---

## 📋 Release Checklist

### Step 1: Push Source Code to GitHub
Ensure all application files (`ghost.py`, `readme.md`, etc.) are committed and pushed to the main branch of your `brew-ghost` repository.

```bash
cd /Users/even/Desktop/Projects/Brew-Ghost
git add .
git commit -m "feat: initial release of brew-ghost core engine"
git push origin main
```

---

### Step 2: Create a GitHub Release (Tarball Generation)
1. Navigate to your `brew-ghost` repository page on GitHub.
2. On the right-hand sidebar, click **Releases** -> **Draft a new release**.
3. Under **Choose a tag**, enter `V1.0.0`.
4. Leave the Target as `main`.
5. Set the Title as `V1.0.0`.
6. Click **Publish release**.
7. GitHub will automatically package the source code and generate the source tarball archive at:
   `https://github.com/amfi-disable/brew-ghost/archive/refs/tags/V1.0.0.tar.gz`

---

### Step 3: Compute the SHA256 Checksum on macOS
Download the generated source archive and calculate its cryptographic hash:

```bash
# 1. Download the source tarball
curl -LO https://github.com/amfi-disable/brew-ghost/archive/refs/tags/V1.0.0.tar.gz

# 2. Compute the SHA256 checksum using macOS native tool
shasum -a 256 V1.0.0.tar.gz
```

*Copy the 64-character hexadecimal hash output from the `shasum` command.*

---

### Step 4: Update the Formula with the Checksum
1. Open the [brew-ghost.rb](file:///Users/even/Desktop/Projects/Brew-Ghost/Formula/brew-ghost.rb) file.
2. Replace `<SHA256_PLACEHOLDER>` in the `sha256` field with the checksum you generated in Step 3.

---

### Step 5: Publish the Formula to your Tap Repo
1. Clone your `homebrew-tap` repository locally:
   ```bash
   git clone https://github.com/amfi-disable/homebrew-tap.git
   cd homebrew-tap
   ```
2. Create a `Formula` directory if it does not already exist:
   ```bash
   mkdir -p Formula
   ```
3. Copy the updated `brew-ghost.rb` formula into the `Formula/` directory:
   ```bash
   cp /Users/even/Desktop/Projects/Brew-Ghost/Formula/brew-ghost.rb Formula/brew-ghost.rb
   ```
4. Commit and push the formula back to GitHub:
   ```bash
   git add Formula/brew-ghost.rb
   git commit -m "feat: add custom tap formula for brew-ghost"
   git push origin main
   ```

---

## 🎉 Test the Installation
Once the tap repository is updated on GitHub, users (including yourself) can instantly install `brew-ghost` using:

```bash
brew install amfi-disable/tap/brew-ghost
```
