# 📦 Step-by-Step Release Protocol (`v1.0.0`)

Follow this guide to package, hash, and publish releases of `Brew-Ghost` to your custom Homebrew Tap.

---

## 🛠 Prerequisites

Ensure you have created two public GitHub repositories:

1. `https://github.com/AMFI-Disable/Brew-Ghost` (holds the application code)
2. `https://github.com/AMFI-Disable/Homebrew-Tap` (holds your custom formula)

---

## 📋 Release Checklist

### Step 1: Push Source Code To GitHub

Ensure all application files (`ghost.py`, `readme.md`, etc.) are committed and pushed to the main branch of your `Brew-Ghost` repository:

```bash
cd /Users/even/Desktop/Projects/Tooling/Brew-Ghost
git add .
git commit -m "feat: publish initial release"
git push origin main
```

---

### Step 2: Create A GitHub Release (Tarball Generation)

1. Navigate to your `Brew-Ghost` repository page on GitHub.
2. On the right-hand sidebar, click **Releases** -> **Draft a new release**.
3. Under **Choose a tag**, enter `v1.0.0`.
4. Leave the Target as `main`.
5. Set the Title as `v1.0.0`.
6. Click **Publish release**.
7. GitHub will automatically package the source code and attach the release archive.

---

### Step 3: Compute The SHA-256 Checksum On macOS

Download the release archive via GitHub CLI and calculate its cryptographic hash:

```bash
# 1. Download the release archive using gh CLI
gh release download v1.0.0 --repo AMFI-Disable/Brew-Ghost --archive=tar.gz

# 2. Compute the SHA256 checksum using macOS native tool
shasum -a 256 Brew-Ghost-1.0.0.tar.gz
```

*Copy the 64-character hexadecimal hash output from the `shasum` command.*

---

### Step 4: Update The Formula With The Checksum

1. Open the [brew-ghost.rb](formula/brew-ghost.rb) file.
2. Replace `<SHA256_PLACEHOLDER>` in the `sha256` field with the checksum you generated in Step 3.

---

### Step 5: Publish The Formula To Your Tap Repo

1. Clone your `Homebrew-Tap` repository locally:

   ```bash
   git clone https://github.com/AMFI-Disable/Homebrew-Tap.git
   cd Homebrew-Tap
   ```

2. Create a `formula` directory if it does not already exist:

   ```bash
   mkdir -p formula
   ```

3. Copy the updated `brew-ghost.rb` formula into the `formula/` directory:

   ```bash
   cp /Users/even/Desktop/Projects/Tooling/Brew-Ghost/formula/brew-ghost.rb formula/brew-ghost.rb
   ```

4. Commit and push the formula back to GitHub:

   ```bash
   git add formula/brew-ghost.rb
   git commit -m "feat: add tap formula"
   git push origin main
   ```

---

## 🎉 Test The Installation

Once the tap repository is updated on GitHub, users (including yourself) can instantly install `Brew-Ghost` using:

```bash
brew install AMFI-Disable/tap/brew-ghost
```
