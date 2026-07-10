# Paper build (plan-2.md §12, §22). Portable pdflatex + bibtex; no network.
LATEX = pdflatex -interaction=nonstopmode -halt-on-error -file-line-error
BIBTEX = bibtex
BUILD = arxiv/build
UV = uv

.PHONY: paper tables check arxiv clean

tables: ## Regenerate LaTeX tables from committed result files + claim registry
	$(UV) run python ../scripts/make_tables.py

paper: tables ## Compile the manuscript to arxiv/build/main.pdf
	mkdir -p $(BUILD)
	$(LATEX) -output-directory=$(BUILD) main.tex
	$(BIBTEX) $(BUILD)/main
	$(LATEX) -output-directory=$(BUILD) main.tex
	$(LATEX) -output-directory=$(BUILD) main.tex
	@echo "Built $(BUILD)/main.pdf"

check: ## Citation/reference/undefined checks on the last build
	$(UV) run python ../scripts/paper_check.py

arxiv: paper ## Assemble a clean arXiv source archive (does NOT submit)
	$(UV) run python ../scripts/make_arxiv_package.py

clean:
	rm -rf $(BUILD)
