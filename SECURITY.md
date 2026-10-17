# Privacy and Security

Resume repositories can expose more than a public resume. Source history may contain private addresses, phone numbers, transcripts, application answers, immigration details, or employer portal data.

Before publishing a fork:

1. Start from a fresh repository. Do not copy the `.git` directory from a private resume repository.
2. Run `make privacy` and review every finding.
3. Run `git status --short` and `git diff --cached` before each push.
4. Confirm that generated documents, transcripts, photographs, application records, browser logs, and local configuration files are not staged.
5. Inspect commit history with `git log --stat --all` before changing repository visibility.
6. Enable a secret-scanning service on the remote repository when available.

If private data is published, removing it in a later commit is insufficient. Rotate any exposed credentials, rewrite the affected Git history, and invalidate cached artifacts or releases.

Security reports should avoid including the private value itself. Describe the affected path and data type instead.
