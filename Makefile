.PHONY: gui cli test dataset

gui:
	./Clips-6.3/run.sh

cli:
	clips -f2 0_main.clp

test:
	@for f in tests/input/*.in; do \
		echo "Running $$(basename $$f)..."; \
		clips -f2 0_main.clp < "$$f" > "tests/output/$$(basename $${f%.in}).out"; \
	done

dataset:
	python3 ./utils/dataset.py 150 2_instancias.clp

