CC ?= cc
CFLAGS = -std=c99 -pedantic -Wall -Wextra -Werror -O2 -ffp-contract=off
LDFLAGS = -lm
SEED ?= 20261030
VERSION = $(shell cat VERSION)
PY = python3

SRC = src/main.c src/gen.c src/rng.c
OBJ = $(SRC:.c=.o)
BIN = eidolon_gen

all: $(BIN)

$(BIN): $(OBJ)
	$(CC) $(CFLAGS) -o $@ $(OBJ) $(LDFLAGS)

src/%.o: src/%.c src/config.h src/rng.h src/gen.h
	$(CC) $(CFLAGS) -c -o $@ $<

seed.stamp: FORCE
	@echo "$(SEED)" | cmp -s - $@ || echo "$(SEED)" > $@

data/cohort.csv: $(BIN) seed.stamp
	mkdir -p data
	./$(BIN) --seed $(SEED) --out $@

data/chaos.csv: $(BIN) seed.stamp
	mkdir -p data
	./$(BIN) --seed $(SEED) --out $@ --chaos --n1 100 --n2 0 --n3 0 --n4 0

data/g5.csv: $(BIN) seed.stamp
	mkdir -p data
	./$(BIN) --seed $(SEED) --out $@ --n1 200 --n2 150 --n3 150 --n4 100 --n5 150

sanitize:
	$(CC) -std=c99 -pedantic -Wall -Wextra -Werror -O1 -g \
		-fsanitize=address,undefined -ffp-contract=off \
		-o /tmp/eidolon_gen_san $(SRC) $(LDFLAGS)

test: sanitize
	mkdir -p /tmp/eidolon_test
	LD_PRELOAD= /tmp/eidolon_gen_san --seed 7 --out /tmp/eidolon_test/san.csv \
		--days 5 --n1 2 --n2 2 --n3 2 --n4 2
	test -s /tmp/eidolon_test/san.csv

test-python:
	$(PY) -m unittest discover -s tests -v

check: $(BIN)
	sh tools/check_determinism.sh ./$(BIN) $(SEED) --against-published
	sh tools/check_g5.sh ./$(BIN) $(SEED)

manifest: $(BIN) data/cohort.csv data/chaos.csv data/g5.csv check
	sh tools/generate_manifest.sh $(SEED)

analysis: $(BIN) data/cohort.csv data/chaos.csv data/g5.csv
	$(PY) python/eidolon_features.py --csv data/cohort.csv --out-dir results
	$(PY) python/eidolon_models.py --groups 1,2,3,4 --models dummy,logreg,rf,hgb,mlp
	$(PY) python/eidolon_forecast.py --cohort data/cohort.csv --chaos data/chaos.csv --out-dir results
	$(PY) python/eidolon_stats.py
	$(PY) python/eidolon_robustness.py
	$(PY) python/eidolon_features.py --csv data/g5.csv --out-dir results/g5
	$(PY) python/eidolon_models.py --features results/g5/features.csv --out-dir results/g5 --groups 1,5 --models dummy,logreg,rf,hgb,mlp
	$(PY) python/eidolon_corrections.py
	$(PY) python/eidolon_matched.py
	$(PY) python/eidolon_plots.py
	$(PY) python/eidolon_g5_plot.py
	sh tools/generate_manifest.sh $(SEED)

release: manifest
	mkdir -p release
	tar --exclude='./release' --exclude='./refs' --exclude='./.git' \
		--exclude='__pycache__' --exclude='*.o' --exclude='./eidolon_gen' \
		--exclude='./seed.stamp' \
		-czf release/eidolon-v$(VERSION).tar.gz .
	sha256sum release/eidolon-v$(VERSION).tar.gz > release/eidolon-v$(VERSION).sha256

clean:
	rm -f $(OBJ) $(BIN)

FORCE:
.PHONY: all clean test test-python sanitize check manifest analysis release FORCE
