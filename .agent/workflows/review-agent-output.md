# Workflow: Review Agent Output

Use this workflow if you are acting as the Reviewer Agent or checking another agent's PR/changes.

## Step 1: Check Global Rules
- Are responsibilities separated correctly?
- Were any secrets committed?
- Was permanent email deletion implemented? (Reject if yes).

## Step 2: Check Feature-Specific Rules
- Do predictions include the model version?
- Are explanations human-readable and not overconfident?
- Is user feedback gated by analyst review?

## Step 3: Check Code Quality
- Are route files thin?
- Are UI components reusable?
- Are tests included?

## Step 4: Final Approval
- If any rule is broken, request changes and specify which `.agent/instructions/` file was violated.
- If all checks pass, approve the implementation.
