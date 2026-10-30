#ifndef EIDOLON_RNG_H
#define EIDOLON_RNG_H

#include <stdint.h>

typedef struct {
    uint64_t state;
    int has_spare;
    double spare;
} rng_t;

void rng_seed(rng_t *r, uint64_t seed);
uint64_t rng_next(rng_t *r);
double rng_uniform(rng_t *r);
double rng_normal(rng_t *r);
int rng_poisson(rng_t *r, double lambda);

#endif
