CC=clang

.PHONY: all
all: compile run

.PHONY: compile
compile: collector.c
	$(CC) -Wall -Wextra -Weverything -Werror -Wno-gnu-binary-literal -O3 -g -lpthread collector.c -o collector

run:
	./collector
