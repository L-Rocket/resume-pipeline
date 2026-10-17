TECTONIC ?= tectonic
XELATEX ?= xelatex
UV ?= uv
PYTHON ?= python3
SOFFICE ?= soffice

BUILD_DIR := build
LATEX_DIR := latex

.PHONY: all latex docx word-pdf privacy test verify clean

all: latex docx privacy

latex:
	mkdir -p $(BUILD_DIR)/latex
	$(TECTONIC) --outdir $(BUILD_DIR)/latex $(LATEX_DIR)/resume_full_time.tex
	$(TECTONIC) --outdir $(BUILD_DIR)/latex $(LATEX_DIR)/resume_coop.tex
	$(XELATEX) -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR)/latex $(LATEX_DIR)/resume_cn.tex

docx:
	mkdir -p $(BUILD_DIR)/docx
	$(UV) run --no-project --with python-docx==1.2.0 --quiet python scripts/build_word_resumes.py

word-pdf: docx
	mkdir -p $(BUILD_DIR)/word-pdf
	$(SOFFICE) --headless --convert-to pdf:writer_pdf_Export --outdir $(BUILD_DIR)/word-pdf $(BUILD_DIR)/docx/resume_full_time.docx $(BUILD_DIR)/docx/resume_coop.docx

privacy:
	$(PYTHON) scripts/check_privacy.py .

test:
	$(UV) run --no-project --with python-docx==1.2.0 --quiet python -m unittest discover -s tests -v

verify: test privacy latex word-pdf
	$(PYTHON) scripts/verify_outputs.py $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)
