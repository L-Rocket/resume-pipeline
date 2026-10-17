# Resume Pipeline

A privacy-first, bilingual, LaTeX-first resume template for application-ready PDFs.

## One-prompt setup

Git is part of this workflow, but you do not need to install or configure the toolchain manually. Open a terminal-capable coding agent, copy the complete prompt from [SETUP_PROMPT.md](SETUP_PROMPT.md), and send it unchanged.

The agent will:

1. identify your operating system;
2. install Git, Make, Python, Tectonic, and `pdfinfo` using trusted package sources;
3. clone this repository without overwriting an existing directory;
4. run the environment doctor; and
5. compile and verify all three one-page PDFs.

The supported beginner path is macOS or Ubuntu, including Ubuntu under WSL. Installation pauses when administrator approval, a restart, or a decision about existing files is required.

The repository contains:

- two English one-page variants for full-time and co-op applications;
- one Chinese LaTeX resume;
- a pre-publication privacy check; and
- CI checks that reject common secrets, private application records, transcripts, and accidental personal data.

All committed content is fictional placeholder material. Replace it locally with your own verified facts. Generated files are ignored by Git so a public fork can keep source templates open while personal outputs stay local.

## Quick start

Requirements:

- Git
- Make
- Tectonic for all PDFs
- Python 3.9 or later
- `pdfinfo` for one-page output verification

Build everything:

```bash
make all
```

Build or verify the PDFs:

```bash
make latex
make doctor
make verify
```

Outputs are written to `build/` and are intentionally not tracked.

## Initialize your own repository

The safest way to use this project with personal resume content is to create a private working repository from a clean checkout. Do not merge in the Git history of an existing resume repository, because deleted files and old commits may still expose private information.

### Clone this repository

```bash
git clone https://github.com/L-Rocket/resume-pipeline.git my-resume
cd my-resume
git remote rename origin upstream
git remote add origin git@github.com:YOUR-ACCOUNT/my-resume.git
git push -u origin main
```

Create `YOUR-ACCOUNT/my-resume` as a private repository before the final push if your customized sources will contain real contact details or employment history.

### Start with fresh history

If you want the files without this repository's commit history:

```bash
git clone --depth 1 https://github.com/L-Rocket/resume-pipeline.git my-resume
cd my-resume
rm -rf .git
git init -b main
git add .
git commit -m "Initialize resume workspace"
```

Run the privacy check before connecting the new repository to a public remote:

```bash
make privacy
```

### Publish a sanitized template with GitHub CLI

Only use this flow for placeholder or intentionally public content:

```bash
make test
make privacy
gh repo create YOUR-ACCOUNT/your-template-name \
  --public \
  --source=. \
  --remote=origin \
  --push
```

For a personal resume repository, replace `--public` with `--private`.

## Customize the templates

Edit these source files:

- `latex/resume_full_time.tex`
- `latex/resume_coop.tex`
- `latex/resume_cn.tex`
- `reference/resume_master_en.md`
- `reference/resume_master_cn.md`

The English templates share these commands:

```tex
\resumeEducation{school}{dates}{degree}{location}{detail}
\resumeHeading{organization or project}{role or technologies}{dates}{location}
\resumeItem{achievement}
\skillItem{label}{skills}
```

Keep reusable layout commands in `latex/resume_style.tex` so the full-time and co-op variants remain visually consistent.

## Privacy model

This project is designed to prevent the most common resume-repository leaks:

- generated PDFs and document artifacts are ignored;
- application trackers, transcripts, photographs, browser captures, and application folders are blocked;
- non-example email addresses and phone numbers are rejected by the privacy check;
- local absolute paths and common secret formats are rejected; and
- the example repository starts with fresh Git history rather than inheriting a private repository's commits.

Run this before every push:

```bash
make privacy
```

The scanner is a guardrail, not a guarantee. Review staged changes and Git history before making a repository public. See [SECURITY.md](SECURITY.md) for the release checklist.

## Repository layout

```text
latex/       LaTeX sources and shared style
reference/   comprehensive bilingual content-bank templates
scripts/     privacy and generated-output checks
tests/       privacy-check tests
build/       generated artifacts, ignored by Git
```

## License

MIT. See [LICENSE](LICENSE).
