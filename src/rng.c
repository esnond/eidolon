#include "rng.h"

#include <math.h>

static uint64_t splitmix64(uint64_t *x)
{
    uint64_t z = (*x += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

void rng_seed(rng_t *r, uint64_t seed)
{
    uint64_t x = seed;
    r->state = splitmix64(&x);
    if (r->state == 0) {
        r->state = 0x9e3779b97f4a7c15ULL;
    }
    r->has_spare = 0;
    r->spare = 0.0;
}

uint64_t rng_next(rng_t *r)
{
    uint64_t x = r->state;
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    r->state = x;
    return x * 2685821657736338717ULL;
}

double rng_uniform(rng_t *r)
{
    return (double)(rng_next(r) >> 11) * 0x1.0p-53;
}

double rng_normal(rng_t *r)
{
    double u;
    double v;
    double s;

    if (r->has_spare) {
        r->has_spare = 0;
        return r->spare;
    }
    do {
        u = 2.0 * rng_uniform(r) - 1.0;
        v = 2.0 * rng_uniform(r) - 1.0;
        s = u * u + v * v;
    } while (s >= 1.0 || s == 0.0);
    s = sqrt(-2.0 * log(s) / s);
    r->spare = v * s;
    r->has_spare = 1;
    return u * s;
}

int rng_poisson(rng_t *r, double lambda)
{
    double limit;
    double p;
    int k;

    if (lambda <= 0.0) {
        return 0;
    }
    limit = exp(-lambda);
    p = 1.0;
    k = 0;
    do {
        k += 1;
        p *= rng_uniform(r);
    } while (p > limit && k < 100);
    return k - 1;
}
