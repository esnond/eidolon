#include "gen.h"

#include <math.h>
#include <stdint.h>

#include "config.h"

static const double PARAM_LO[N_PARAM] = {
    5.0, 17.0, 15.0, 120.0, 0.10, 1.0, 6.0, 0.50,
    0.05, 0.50, 0.10, 0.02, 1500.0, 0.25, 0.30, 0.0,
    0.2, 0.0, -0.01, 0.60, 0.10, 0.60, 0.002, -0.30
};

static const double PARAM_HI[N_PARAM] = {
    11.0, 23.0, 120.0, 900.0, 0.70, 3.5, 25.0, 0.90,
    0.35, 2.00, 0.50, 0.30, 25000.0, 0.90, 1.10, 0.45,
    1.0, 0.4, 0.01, 0.95, 0.40, 0.95, 0.020, 0.30
};

/* 0 chronotype, 1 activity, 2 technology */
static const int PARAM_FACTOR[N_PARAM] = {
    0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 1, 2,
    2, 2, 2, 2, 0, 1, 1, 2, 0, 2, 1, 0
};

static const int ACTION_SECTION[N_ACTION] = {0, 0, 1, 2, 3, 4, 5, 5};

static const int INTENSE_PATTERN[4][N_ACTION] = {
    {0, 1, 2, 3, 4, 5, 6, 7},
    {7, 6, 5, 4, 3, 2, 1, 0},
    {0, 2, 4, 6, 1, 3, 5, 7},
    {3, 1, 4, 0, 7, 5, 6, 2}
};

static double clip(double x, double lo, double hi)
{
    if (x < lo) {
        return lo;
    }
    if (x > hi) {
        return hi;
    }
    return x;
}

static double mask_scalar(const patient_t *pt)
{
    double sum = 0.0;
    int k;

    for (k = 0; k < N_PARAM; k += 1) {
        sum += (pt->p[k] - PARAM_LO[k]) / (PARAM_HI[k] - PARAM_LO[k]);
    }
    return sum / (double)N_PARAM;
}

static void sample_natural_params(rng_t *r, double *p)
{
    double g[3];
    int k;

    g[0] = rng_normal(r);
    g[1] = rng_normal(r);
    g[2] = rng_normal(r);
    for (k = 0; k < N_PARAM; k += 1) {
        double mid = 0.5 * (PARAM_LO[k] + PARAM_HI[k]);
        double sd = (PARAM_HI[k] - PARAM_LO[k]) / 6.0;
        double z = rng_normal(r);
        double val = mid + sd * (0.75 * z + 0.45 * g[PARAM_FACTOR[k]]);
        p[k] = clip(val, PARAM_LO[k], PARAM_HI[k]);
    }
}

static void sample_preferences(rng_t *r, double *pref)
{
    double sum = 0.0;
    int a;

    for (a = 0; a < N_ACTION; a += 1) {
        pref[a] = 0.2 + 1.8 * rng_uniform(r);
        sum += pref[a];
    }
    for (a = 0; a < N_ACTION; a += 1) {
        pref[a] /= sum;
    }
}

void patient_init_natural(rng_t *r, patient_t *pt)
{
    sample_natural_params(r, pt->p);
    sample_preferences(r, pt->pref);
    pt->s = 0.0;
    pt->group = 1;
}

void patient_init_moderate(rng_t *r, patient_t *pt)
{
    int k;

    patient_init_natural(r, pt);
    pt->group = 2;
    for (k = 0; k < N_PARAM; k += 1) {
        double mid = 0.5 * (PARAM_LO[k] + PARAM_HI[k]);
        double jitter = 0.06 * (PARAM_HI[k] - PARAM_LO[k]) * rng_normal(r);
        pt->p[k] = clip(mid + 0.55 * (pt->p[k] - mid) + jitter,
                        PARAM_LO[k], PARAM_HI[k]);
    }
}

void patient_init_intense(patient_t *pt, double s, int group)
{
    int k;
    int a;

    pt->s = s;
    pt->group = group;
    for (k = 0; k < N_PARAM; k += 1) {
        pt->p[k] = PARAM_LO[k] + s * (PARAM_HI[k] - PARAM_LO[k]);
    }
    for (a = 0; a < N_ACTION; a += 1) {
        pt->pref[a] = 1.0 / N_ACTION;
    }
}

static int weighted_action(const patient_t *pt, rng_t *r)
{
    double w[N_ACTION];
    double sum = 0.0;
    double u;
    int a;

    for (a = 0; a < N_ACTION; a += 1) {
        w[a] = pow(pt->pref[a], pt->p[9]);
        sum += w[a];
    }
    u = rng_uniform(r) * sum;
    for (a = 0; a < N_ACTION; a += 1) {
        u -= w[a];
        if (u <= 0.0) {
            return a;
        }
    }
    return N_ACTION - 1;
}

static int choose_action(const patient_t *pt, int prev, int prev2, rng_t *r)
{
    if (prev >= 0 && rng_uniform(r) < pt->p[8]) {
        return prev;
    }
    if (prev >= 0 && rng_uniform(r) < pt->p[7]) {
        return prev;
    }
    if (prev2 >= 0 && rng_uniform(r) < pt->p[11]) {
        return prev2;
    }
    return weighted_action(pt, r);
}

static void build_actions(const patient_t *pt, int n, int *actions, rng_t *r)
{
    int prev = -1;
    int prev2 = -1;
    int j;

    for (j = 0; j < n; j += 1) {
        int a = (j == 0) ? weighted_action(pt, r)
                         : choose_action(pt, prev, prev2, r);
        if (pt->group == 2 && rng_uniform(r) < 0.30) {
            a = (int)(rng_uniform(r) * N_ACTION);
        }
        actions[j] = a;
        prev2 = prev;
        prev = a;
    }
    if (pt->group == 2) {
        for (j = 1; j < n; j += 1) {
            if (rng_uniform(r) < 0.15) {
                int tmp = actions[j - 1];
                actions[j - 1] = actions[j];
                actions[j] = tmp;
            }
        }
    }
}

static void build_intervals(const patient_t *pt, int n, double fib, double chaos,
                            double *iv, rng_t *r)
{
    double sigma = 0.5 * (pt->p[13] + pt->p[14]);
    int j;

    sigma *= (1.5 - pt->p[19]) * chaos;
    iv[0] = 0.0;
    for (j = 1; j < n; j += 1) {
        double base = pt->p[12];
        double val = base * exp(sigma * rng_normal(r));
        double u = rng_uniform(r);
        if (u < pt->p[15]) {
            val *= 0.35;
        } else if (u < 2.0 * pt->p[15]) {
            val *= 2.2;
        }
        val *= fib;
        if (pt->group == 2 && rng_uniform(r) < 0.35) {
            val = base * (0.5 + rng_uniform(r));
        }
        iv[j] = clip(val, MIN_INTERVAL_MS, MAX_INTERVAL_MS);
    }
    if (rng_uniform(r) < pt->p[22] && n > 2) {
        int idx = 1 + (int)(rng_uniform(r) * (n - 1));
        iv[idx] *= 3.0 + 7.0 * rng_uniform(r);
    }
}

static void write_session(FILE *out, int pid, int group, int day, int dow,
                          int sidx, int start_s, int dur_s, int n,
                          const int *actions, const double *iv)
{
    double total = 0.0;
    double max_ms = (double)dur_s * 1000.0;
    double scale;
    double cum = 0.0;
    int j;

    for (j = 1; j < n; j += 1) {
        total += iv[j];
    }
    scale = (total > max_ms && total > 0.0) ? max_ms / total : 1.0;
    for (j = 0; j < n; j += 1) {
        int iv_ms;
        int t_s;
        int repeat;

        if (j > 0) {
            cum += iv[j] * scale;
        }
        t_s = start_s + (int)(cum / 1000.0);
        if (t_s >= SECONDS_PER_DAY) {
            break;
        }
        iv_ms = (j == 0) ? 0 : (int)(iv[j] * scale);
        if (j > 0 && iv_ms < 1) {
            iv_ms = 1;
        }
        repeat = (j > 0 && actions[j] == actions[j - 1]) ? 1 : 0;
        fprintf(out, "%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n",
                pid, group, day, t_s, j + 1, iv_ms, dur_s,
                actions[j], ACTION_SECTION[actions[j]], repeat, sidx, dow,
                dow >= 6 ? 1 : 0);
    }
}

static void emit_natural_session(FILE *out, const patient_t *pt, int pid,
                                 int day, int dow, int sidx, int start_s,
                                 int dur_s, int n, double fib, double chaos,
                                 rng_t *r)
{
    int actions[MAX_ACTIONS];
    double iv[MAX_ACTIONS];

    if (n < 3) {
        n = 3;
    }
    if (n > MAX_ACTIONS) {
        n = MAX_ACTIONS;
    }
    build_actions(pt, n, actions, r);
    build_intervals(pt, n, fib, chaos, iv, r);
    write_session(out, pid, pt->group, day, dow, sidx, start_s, dur_s,
                  n, actions, iv);
}

static void emit_natural_day(FILE *out, const patient_t *pt, int pid, int day,
                             int dow, double fib, double chaos, rng_t *r)
{
    int weekend = (dow >= 6) ? 1 : 0;
    double lam = pt->p[5] * (1.0 + pt->p[17] * (weekend ? 1.0 : -0.3));
    int ns;
    int s;
    int last_end = 0;

    lam *= 1.0 + pt->p[18] * ((double)day - 45.0) / 45.0;
    if (chaos > 1.0) {
        lam *= 1.0 + 0.15 * (chaos - 1.0) * rng_normal(r);
    }
    lam = clip(lam, 0.05, 6.0);
    ns = rng_poisson(r, lam);
    if (ns > MAX_SESSIONS) {
        ns = MAX_SESSIONS;
    }
    if (pt->group == 2 && rng_uniform(r) < 0.30) {
        ns += (rng_uniform(r) < 0.5) ? -1 : 1;
    }
    if (ns < 1) {
        ns = 1;
    }
    for (s = 0; s < ns; s += 1) {
        double center = (s == 0) ? pt->p[0] : pt->p[1];
        double hour = center;
        double dur;
        int n;
        int start_s;

        hour += (pt->p[2] / 60.0) * (0.5 + pt->p[20]) * rng_normal(r);
        hour += pt->p[16] * sin(2.0 * PI * (double)dow / 7.0);
        hour += pt->p[23] * (double)weekend;
        if (chaos > 1.0) {
            hour += (pt->p[2] / 60.0) * 0.5 * (chaos - 1.0) * rng_normal(r);
        }
        if (pt->group == 2 && rng_uniform(r) < 0.70) {
            hour += (rng_uniform(r) * 2.0 - 1.0) * 0.75;
        }
        hour = clip(hour, 0.0, 23.5);
        start_s = (int)(hour * 3600.0);
        if (start_s < last_end + 60) {
            start_s = last_end + 60;
        }
        if (start_s >= SECONDS_PER_DAY - MIN_DURATION_S) {
            break;
        }
        dur = pt->p[3] * exp(pt->p[4] * rng_normal(r));
        if (pt->group == 2) {
            dur *= exp(0.25 * rng_normal(r));
        }
        if (chaos > 1.0) {
            dur *= 1.0 + 0.20 * (chaos - 1.0) * rng_normal(r);
        }
        dur = clip(dur, MIN_DURATION_S, MAX_DURATION_S);
        n = (int)(pt->p[6] * exp(pt->p[10] * rng_normal(r)) + 0.5);
        if (n < 3) {
            n = 3;
        }
        if (n > MAX_ACTIONS) {
            n = MAX_ACTIONS;
        }
        emit_natural_session(out, pt, pid, day, dow, s + 1, start_s,
                             (int)dur, n, fib, chaos, r);
        last_end = start_s + (int)dur;
    }
}

static void emit_intense_session(FILE *out, int pid, int group, int day,
                                 int dow, int sidx, int start_s, int dur_s,
                                 int n, int iv_ms, int pat, int off)
{
    int j;

    for (j = 0; j < n; j += 1) {
        int a = INTENSE_PATTERN[pat][(j + off) % N_ACTION];
        int t_s = start_s + (j * iv_ms) / 1000;
        int repeat = 0;

        if (t_s >= SECONDS_PER_DAY) {
            break;
        }
        if (j > 0) {
            int prev = INTENSE_PATTERN[pat][(j - 1 + off) % N_ACTION];
            repeat = (a == prev) ? 1 : 0;
        }
        fprintf(out, "%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n",
                pid, group, day, t_s, j + 1, j == 0 ? 0 : iv_ms, dur_s,
                a, ACTION_SECTION[a], repeat, sidx, dow, dow >= 6 ? 1 : 0);
    }
}

static void emit_intense_day(FILE *out, const patient_t *pt, int pid, int day,
                             int dow)
{
    double s = pt->s;
    int ns = 1 + (int)(s * 3.0);
    int start = ((int)((6.0 + 12.0 * s) * 2.0)) * 1800;
    int dur = 30 * ((int)((120.0 + 600.0 * s) / 30.0));
    int n = 5 + 5 * ((int)(s * 4.0));
    int iv = 250 * ((int)((1500.0 + 12000.0 * s) / 250.0));
    int pat = (int)(s * 4.0);
    int off = ((int)(s * 8.0)) % N_ACTION;
    int sidx;

    if (ns > 3) {
        ns = 3;
    }
    if (pat > 3) {
        pat = 3;
    }
    for (sidx = 0; sidx < ns; sidx += 1) {
        int st = start + sidx * (dur + 300);
        if (st >= SECONDS_PER_DAY) {
            break;
        }
        emit_intense_session(out, pid, pt->group, day, dow, sidx + 1, st,
                             dur, n, iv, pat, off);
    }
}

void emit_patient(FILE *out, const patient_t *pt, int pid, int days, int chaos,
                  rng_t *r)
{
    double f1 = 0.0;
    double f2 = 0.0;
    double f3 = 0.0;
    double rho = pt->p[21];
    double fib;
    int day;
    patient_t mask;
    int has_mask = (pt->group == 6 || pt->group == 7) ? 1 : 0;

    if (has_mask) {
        patient_init_intense(&mask, mask_scalar(pt), pt->group);
    }
    for (day = 1; day <= days; day += 1) {
        int dow = ((day - 1) % 7) + 1;
        double chaos_mult = 1.0;

        if (pt->group == 3) {
            emit_intense_day(out, pt, pid, day, dow);
            continue;
        }
        if (pt->group == 4) {
            patient_t tmp;
            sample_natural_params(r, tmp.p);
            sample_preferences(r, tmp.pref);
            tmp.s = 0.0;
            tmp.group = 4;
            emit_natural_day(out, &tmp, pid, day, dow, 1.0, 1.0, r);
            continue;
        }
        f1 = rho * f1 + sqrt(1.0 - rho * rho) * rng_normal(r);
        f2 = 0.95 * f2 + sqrt(1.0 - 0.95 * 0.95) * rng_normal(r);
        f3 = 0.99 * f3 + sqrt(1.0 - 0.99 * 0.99) * rng_normal(r);
        fib = exp(0.12 * (f1 + f2 + f3));
        if (chaos) {
            chaos_mult = (day <= 30) ? 1.0 : (day <= 60 ? 1.5 : 2.2);
        }
        if (has_mask && day <= 45) {
            emit_natural_day(out, pt, pid, day, dow, fib, chaos_mult, r);
        } else if (has_mask && pt->group == 6) {
            emit_intense_day(out, &mask, pid, day, dow);
        } else if (has_mask) {
            emit_natural_day(out, &mask, pid, day, dow, fib, 1.0, r);
        } else {
            emit_natural_day(out, pt, pid, day, dow, fib, chaos_mult, r);
        }
    }
}
