---
description: Pulls a remote branch and reviews backend changes against development
---

# Pull and Review Backend Changes

Arguments:
1. BRANCH_NAME: The name of the branch to review
2. GITLAB_TOKEN: The GitLab token (available as $2, useful if needed for API calls or auth, though not explicitly used in git commands here)

## Step 1: Update Development Branch
```bash
git checkout development
git pull origin development
```

## Step 2: Checkout and Pull Target Branch
```bash
git checkout $1
git pull origin $1
```

## Step 3: List Commits on Branch
```bash
echo "Commits on $1 that are not in development:"
git log development..$1 --oneline
```

## Step 4: Review Changes
// turbo
```bash
# This command outputs the diff for the LLM to read. 
# The instruction below tells the LLM how to process this output.
git diff development...$1
```

INSTRUCTION: 
You are an expert Python and Backend reviewer with deep knowledge of Docker and GitLab CI. Review the code changes output by the `git diff` command above.
Focus your review on:
1.  **Python Best Practices**: Check for pythonic code, type hinting, proper error handling, and efficient data structures.
2.  **Backend Architecture**: Evaluate API design, database interactions, and overall system scalability.
3.  **Docker & CI/CD**: Scrutinize Dockerfiles and `.gitlab-ci.yml` changes for best practices, build efficiency, and security.
4.  **Code Quality**: Look for readability, maintainability, formatting (PEP 8), and adherence to DRY principles.
5.  **Security**: Check for SQL injection, hardcoded secrets, insecure dependencies, and proper authentication/authorization handling.

Provide a concise summary of the changes followed by your detailed feedback.
