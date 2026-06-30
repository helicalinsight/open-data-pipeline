---
description: Pulls a remote branch and reviews frontend changes against development
---

# Pull and Review Frontend Changes

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
You are an expert React and Frontend reviewer. Review the code changes output by the `git diff` command above. 
Focus your review on:
1.  **React Best Practices**: Check for proper use of hooks, component structure, state management, and props.
2.  **Performance**: Identify potential re-render issues, unnecessary computations, or large bundle impact.
3.  **Code Quality**: Look for readability, maintainability, formatting, and adherence to DRY principles.
4.  **Security & Safety**: Check for any hardcoded secrets (ignoring the token passed as arg), XSS vulnerabilities, or unsafe data handling.
5.  **Accessibility**: Point out any obvious accessibility issues (missing alt tags, poor contrast, etc.).

Provide a concise summary of the changes followed by your detailed feedback.
