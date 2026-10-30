#ifndef EIDOLON_CONFIG_H
#define EIDOLON_CONFIG_H

/* frozen experiment constants; runtime overrides only for documented cli flags */
#define N_PARAM 24
#define N_ACTION 8
#define N_SECTION 6
#define MAX_DAYS 365
#define MAX_SESSIONS 8
#define MAX_ACTIONS 80
#define SECONDS_PER_DAY 86400
#define DEFAULT_SEED 20261030ULL
#define DEFAULT_DAYS 90
#define DEFAULT_N1 200
#define DEFAULT_N2 150
#define DEFAULT_N3 150
#define DEFAULT_N4 100
#define DEFAULT_N5 0
#define DEFAULT_N6 0
#define DEFAULT_N7 0
#define MIN_INTERVAL_MS 250
#define MAX_INTERVAL_MS 600000
#define MIN_DURATION_S 60
#define MAX_DURATION_S 3600
#define PI 3.14159265358979323846

/* csv schema v1, frozen; see readme */
#define CSV_HEADER "patient_id,group,day,t_s,action_seq,interval_ms,session_dur_s,action_id,section_id,is_repeat,session_idx,day_of_week,is_weekend\n"

#endif
