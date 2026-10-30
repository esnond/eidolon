#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"
#include "gen.h"
#include "rng.h"

static int parse_int(const char *text, int lo, int hi, int *out)
{
    char *end = NULL;
    long val;

    errno = 0;
    val = strtol(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0' || val < lo || val > hi) {
        return 0;
    }
    *out = (int)val;
    return 1;
}

static int parse_seed(const char *text, uint64_t *out)
{
    char *end = NULL;
    unsigned long long val;

    errno = 0;
    val = strtoull(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0') {
        return 0;
    }
    *out = (uint64_t)val;
    return 1;
}

static void usage(const char *prog)
{
    fprintf(stderr,
            "usage: %s [--seed N] [--out PATH] [--days N] "
            "[--n1 N] [--n2 N] [--n3 N] [--n4 N] [--n5 N] [--chaos]\n", prog);
}

int main(int argc, char **argv)
{
    uint64_t seed = DEFAULT_SEED;
    const char *out_path = "data/cohort.csv";
    int days = DEFAULT_DAYS;
    int counts[7] = {DEFAULT_N1, DEFAULT_N2, DEFAULT_N3, DEFAULT_N4, DEFAULT_N5, DEFAULT_N6, DEFAULT_N7};
    int chaos = 0;
    int i;
    int pid = 0;
    int g;
    FILE *out;
    rng_t rng;

    for (i = 1; i < argc; i += 1) {
        if (strcmp(argv[i], "--seed") == 0 && i + 1 < argc) {
            if (!parse_seed(argv[i + 1], &seed)) {
                usage(argv[0]);
                return 2;
            }
            i += 1;
        } else if (strcmp(argv[i], "--out") == 0 && i + 1 < argc) {
            out_path = argv[i + 1];
            i += 1;
        } else if (strcmp(argv[i], "--days") == 0 && i + 1 < argc) {
            if (!parse_int(argv[i + 1], 1, MAX_DAYS, &days)) {
                usage(argv[0]);
                return 2;
            }
            i += 1;
        } else if (strcmp(argv[i], "--n1") == 0 && i + 1 < argc) {
            if (!parse_int(argv[i + 1], 0, 10000, &counts[0])) {
                usage(argv[0]);
                return 2;
            }
            i += 1;
        } else if (strcmp(argv[i], "--n2") == 0 && i + 1 < argc) {
            if (!parse_int(argv[i + 1], 0, 10000, &counts[1])) {
                usage(argv[0]);
                return 2;
            }
            i += 1;
        } else if (strcmp(argv[i], "--n3") == 0 && i + 1 < argc) {
            if (!parse_int(argv[i + 1], 0, 10000, &counts[2])) {
                usage(argv[0]);
                return 2;
            }
            i += 1;
        } else if (strcmp(argv[i], "--n4") == 0 && i + 1 < argc) {
            if (!parse_int(argv[i + 1], 0, 10000, &counts[3])) {
                usage(argv[0]);
                return 2;
            }
            i += 1;
        } else if (strcmp(argv[i], "--n5") == 0 && i + 1 < argc) {
            if (!parse_int(argv[i + 1], 0, 10000, &counts[4])) {
                usage(argv[0]);
                return 2;
            }
            i += 1;
        } else if (strcmp(argv[i], "--n6") == 0 && i + 1 < argc) {
            if (!parse_int(argv[i + 1], 0, 10000, &counts[5])) {
                usage(argv[0]);
                return 2;
            }
            i += 1;
        } else if (strcmp(argv[i], "--n7") == 0 && i + 1 < argc) {
            if (!parse_int(argv[i + 1], 0, 10000, &counts[6])) {
                usage(argv[0]);
                return 2;
            }
            i += 1;
        } else if (strcmp(argv[i], "--chaos") == 0) {
            chaos = 1;
        } else {
            usage(argv[0]);
            return 2;
        }
    }
    out = fopen(out_path, "w");
    if (out == NULL) {
        fprintf(stderr, "cannot open %s\n", out_path);
        return 1;
    }
    setvbuf(out, NULL, _IOFBF, 1 << 20);
    fputs(CSV_HEADER, out);
    rng_seed(&rng, seed);
    for (g = 0; g < 7; g += 1) {
        for (i = 0; i < counts[g]; i += 1) {
            patient_t pt;
            if (g == 0) {
                patient_init_natural(&rng, &pt);
            } else if (g == 1) {
                patient_init_moderate(&rng, &pt);
            } else if (g == 2) {
                double s = ((double)i + 0.5) / (double)counts[2];
                patient_init_intense(&pt, s, 3);
            } else if (g == 3) {
                memset(&pt, 0, sizeof(pt));
                pt.p[21] = 0.5;
                pt.group = 4;
            } else if (g == 4) {
                double s = ((double)i + 0.5) / (double)counts[4];
                patient_init_intense(&pt, s, 5);
            } else {
                patient_init_natural(&rng, &pt);
                pt.group = g + 1;
            }
            emit_patient(out, &pt, pid, days, chaos, &rng);
            pid += 1;
        }
    }
    if (fclose(out) != 0) {
        fprintf(stderr, "close failed\n");
        return 1;
    }
    return 0;
}
