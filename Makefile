TECTONIC ?= tectonic
XELATEX ?= xelatex
PYTHON ?= python3

BUILD_DIR := build
LATEX_DIR := latex

.PHONY: all latex privacy test verify clean

all: verify

latex:
	mkdir -p $(BUILD_DIR)/latex
	$(TECTONIC) --outdir $(BUILD_DIR)/latex $(LATEX_DIR)/resume_full_time.tex
	$(TECTONIC) --outdir $(BUILD_DIR)/latex $(LATEX_DIR)/resume_coop.tex
	$(XELATEX) -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR)/latex $(LATEX_DIR)/resume_cn.tex

privacy:
	$(PYTHON) scripts/check_privacy.py .

test:
	$(PYTHON) -m unittest discover -s tests -v

verify: test privacy latex
	$(PYTHON) scripts/verify_outputs.py $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)
