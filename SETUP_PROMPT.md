# One Prompt Setup

Copy everything inside the following block into a terminal-capable coding agent. The agent must have permission to run commands on your computer.

```text
Set up the Resume Pipeline repository on this computer from start to finish.

Repository: https://github.com/L-Rocket/resume-pipeline.git
Preferred local directory name: resume-pipeline

Goal:
- Install the minimum required tools.
- Clone the repository with Git.
- Run its built-in environment checks.
- Compile and verify every resume PDF.
- Leave me with the exact local repository path and the commands I should use next.

Required commands after setup:
- git
- make
- python3 version 3.9 or newer
- tectonic
- pdfinfo

Safety rules:
1. Detect the operating system, architecture, shell, existing package managers, and already-installed tools before changing anything.
2. Support macOS and Ubuntu, including Ubuntu under WSL. On native Windows, prefer WSL Ubuntu. If enabling WSL requires a restart, explain the exact next step and stop cleanly.
3. Use official operating-system package managers or the installation methods documented by the tool's official project. Do not pipe a downloaded script directly into a shell. Do not disable TLS, signature checks, Gatekeeper, antivirus, or other security controls.
4. Explain any command that requires administrator privileges before running it. Let the normal password or approval prompt appear; never request that I send you a password or token in chat.
5. Do not overwrite files, delete an existing directory, reset a repository, discard local changes, or force-push.
6. If the target directory already exists:
   - if it is a clean clone of the specified repository, update it only with `git pull --ff-only`;
   - if it has local changes, a different remote, or is not a Git repository, stop and explain the conflict.
7. Do not create a public repository and do not upload personal resume content.
8. Use non-interactive installation flags only when they do not bypass required consent or security review.

Installation guidance:
- On macOS, verify the Xcode Command Line Tools for Git and Make. If Homebrew is already available, use it for Tectonic and Poppler. If Homebrew or the Command Line Tools must be installed, use their official installation flow and explain any interactive step.
- On Ubuntu or WSL Ubuntu, use APT for Git, Make, Python, certificates, curl, and Poppler. Install Tectonic using a current official binary or another installation method documented by the Tectonic project. Verify the downloaded release when checksums are provided.
- Do not install a full TeX Live or MacTeX distribution unless Tectonic cannot be installed and you first explain the size and tradeoff.

Execution plan:
1. Print the detected platform and which required commands are missing.
2. Install only the missing requirements.
3. Verify each requirement with its version command.
4. Clone the repository using Git, or safely fast-forward an existing clean clone.
5. Enter the repository and run `make doctor`.
6. Run `make verify` and fix setup-related failures without changing resume content.
7. Confirm that these files exist and that each contains exactly one page:
   - build/latex/resume_full_time.pdf
   - build/latex/resume_coop.pdf
   - build/latex/resume_cn.pdf
8. Run `git status --short`. The source working tree must remain clean; ignored build outputs are expected.
9. Report:
   - the absolute repository path;
   - installed tool versions;
   - verification result;
   - any warnings that still matter;
   - the next commands: `make latex`, `make verify`, and `make privacy`.

Do the work now. Ask me only when an administrator approval, restart, unsupported platform, or existing-file conflict prevents safe continuation.
```
