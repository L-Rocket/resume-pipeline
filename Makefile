TECTONIC ?= tectonic
PYTHON ?= python3

BUILD_DIR := build
LATEX_DIR := latex

.PHONY: all doctor latex privacy test verify clean

all: verify

doctor:
	$(PYTHON) scripts/doctor.py

latex:
	mkdir -p $(BUILD_DIR)/latex
	$(TECTONIC) --outdir $(BUILD_DIR)/latex $(LATEX_DIR)/resume_full_time.tex
	$(TECTONIC) --outdir $(BUILD_DIR)/latex $(LATEX_DIR)/resume_coop.tex
	$(TECTONIC) --outdir $(BUILD_DIR)/latex $(LATEX_DIR)/resume_cn.tex

privacy:
	$(PYTHON) scripts/check_privacy.py .

test:
	$(PYTHON) -m unittest discover -s tests -v

verify: doctor test privacy latex
	$(PYTHON) scripts/verify_outputs.py $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)
