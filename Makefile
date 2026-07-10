# msdocs-tokenizer study — resumable harness (plan.md §22).
# Every target is safe to re-run; stages skip when inputs are unchanged.

UV ?= uv
RUN := $(UV) run
PROFILE ?= pilot

.DEFAULT_GOAL := help
.PHONY: help setup doctor test inventory research \
        acquire-pilot audit-pilot train-pilot evaluate-pilot pilot \
        acquire-full train-all evaluate-all benchmark-runtime analyze report verify clean-derived

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Create/refresh the uv environment
	$(UV) sync

doctor: ## Environment + budget preflight
	bash scripts/doctor.sh

test: ## Run the test suite (no network)
	$(RUN) pytest -q -m "not network"

inventory: ## MicrosoftDocs repo inventory (gh)
	$(RUN) msdocs-tok inventory

research: ## Regenerate research artifacts index
	@echo "Research artifacts live under research/ (curated). See research/LITERATURE_REVIEW.md"

# ---- Pilot (32 MiB, 16K) ----
acquire-pilot: ## Acquire + pin pilot sources
	$(RUN) msdocs-tok acquire --profile pilot

audit-pilot: ## Clean, dedupe, split, byte-match pilot corpora
	$(RUN) msdocs-tok audit --profile pilot

train-pilot: ## Train 16K General/Azure/Mixed
	$(RUN) msdocs-tok train --profile pilot

evaluate-pilot: ## Evaluate pilot tokenizers + baselines
	$(RUN) msdocs-tok evaluate --profile pilot

pilot: ## Full pilot chain + gate
	$(RUN) msdocs-tok run-pilot

# ---- Full matrix (256 MiB, 8K/16K/32K) ----
acquire-full: ## Acquire full-profile sources
	$(RUN) msdocs-tok acquire --profile full

audit-full: ## Build full-profile corpora
	$(RUN) msdocs-tok audit --profile full

train-all: ## Train the nine controlled tokenizers
	$(RUN) msdocs-tok train --profile full

evaluate-all: ## Evaluate the full matrix
	$(RUN) msdocs-tok evaluate --profile full

# ---- Analysis + reporting ----
benchmark-runtime: ## Serialized CPU runtime benchmark
	$(RUN) msdocs-tok benchmark --profile $(PROFILE)

analyze: ## Paired bootstrap + figures
	$(RUN) msdocs-tok analyze --profile $(PROFILE)

report: ## FINAL_REPORT.md + notebooks
	$(RUN) msdocs-tok report --profile $(PROFILE)

verify: ## Independent verification gate
	$(RUN) msdocs-tok verify --profile $(PROFILE)

clean-derived: ## Remove derived data + results (keeps manifests + configs)
	rm -rf data/raw data/normalized data/segments data/splits data/evaluation data/audit data/.stages
	rm -rf results/raw results/processed results/tables results/figures
	@echo "Derived artifacts removed. Sources + manifests + configs preserved."

# ---- Publication + arXiv preparation (plan-2.md) ----
.PHONY: verify-claims figures paper paper-check arxiv-package publication-audit publication-docs publication-verify

verify-claims: ## Verify every registered numeric claim against its source file
	$(RUN) python scripts/verify_claims.py

figures: ## Regenerate publication figures (PNG + PDF) from committed source tables
	$(RUN) python scripts/make_figures.py

paper: ## Compile the arXiv manuscript
	$(MAKE) -C paper paper

paper-check: ## Citation/reference/link/claim/LaTeX checks on the paper
	$(MAKE) -C paper check

arxiv-package: ## Build a clean arXiv source archive (does NOT submit)
	$(MAKE) -C paper arxiv

publication-verify: ## Full publication gate (verify + claims + links + figures + paper)
	$(RUN) python scripts/publication_verify.py
