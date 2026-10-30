#ifndef EIDOLON_GEN_H
#define EIDOLON_GEN_H

#include <stdio.h>

#include "config.h"
#include "rng.h"

typedef struct {
    double p[N_PARAM];
    double pref[N_ACTION];
    double s;
    int group;
} patient_t;

void patient_init_natural(rng_t *r, patient_t *pt);
void patient_init_moderate(rng_t *r, patient_t *pt);
void patient_init_intense(patient_t *pt, double s, int group);
void emit_patient(FILE *out, const patient_t *pt, int pid, int days, int chaos,
                  rng_t *r);

#endif
