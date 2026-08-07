# Bootstrap + Git sequence

The local project directory is currently assumed to be empty:

```text
E:\Github\istatistik
```

## 1. Create a clean `main` baseline

Run in PowerShell **before copying the Topic 01 package**:

```powershell
cd E:\Github\istatistik

git init
git branch -M main

"# İKT 207 İstatistik" | Set-Content -Encoding UTF8 README.md

git add README.md
git commit -m "chore: initialize statistics repository"
```

If a GitHub repository has already been created, add its remote now:

```powershell
git remote add origin https://github.com/[KULLANICI]/[REPO].git
```

Do not invent this URL; replace the placeholders with the actual repository path.

## 2. Create the Topic 01 branch

```powershell
git switch -c feature/konu01-app-foundation
```

Now copy/extract the contents of the Topic 01 package directly into:

```text
E:\Github\istatistik
```

Allow the package README to replace the one-line baseline README.

## 3. Create the Python environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## 4. Automated validation

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall app.py core topics tests
git diff --check
```

All three commands should complete cleanly before staging files.

## 5. Manual Streamlit review

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Use `KONU01_REVIEW_CHECKLIST.md` for the visual/behavioral review.

## 6. Commit only after the manual review

```powershell
git status --short

git add `
  .gitignore `
  .github `
  README.md `
  BOOTSTRAP_AND_GIT.md `
  KONU01_REVIEW_CHECKLIST.md `
  app.py `
  assets `
  core `
  docs `
  requirements.txt `
  requirements-dev.txt `
  tests `
  topics

git status --short
git diff --cached --check

git commit -m "feat: add Topic 01 and application foundation"
```

Do not push yet if a manual UI issue remains.
