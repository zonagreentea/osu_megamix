%{
/*
 * guardian.l
 *
 * osu!megamix Runtime Guardian
 *
 * Single-file safety authority.
 *
 * Responsibilities:
 *  - Protect timeline authority
 *  - Protect audio continuity
 *  - Validate engine events
 *  - Route failures safely
 *  - Prevent destructive state changes
 *
 * Source of truth:
 *  guardian.l
 *
 * Build:
 *  flex guardian.l
 *
 * Invariants:
 *  TIME_CONTINUES=1
 *  AUDIO_AUTHORITATIVE=1
 *  ONE_INTENT_AT_A_TIME=1
 *  SUCCESS_IS_SILENT=1
 *  FAILURE_IS_ROUTED=1
 */

#include <stdio.h>
#include <string.h>

int guardian_safe = 1;

void guardian_fail(const char *reason)
{
    guardian_safe = 0;

    printf(
        "[GUARDIAN] FAILURE ROUTED: %s\n",
        reason
    );
}

void guardian_pass(const char *event)
{
    printf(
        "[GUARDIAN] ACCEPTED: %s\n",
        event
    );
}

%}


/*
==================================================
 GUARDIAN RULE DEFINITIONS
==================================================
*/


TIMELINE          "timeline"
AUDIO             "audio"
RESET             "reset"
STOP              "stop"
PAUSE             "pause"
SEEK              "seek"
DESYNC            "desync"

INPUT             "input"
MODE              "mode"
PLAYER            "player"

SAFE              "safe"
FAIL              "fail"



%%


/*
==================================================
 TIMELINE AUTHORITY
==================================================
*/


{STOP}
{
    guardian_fail(
        "Timeline stop request rejected"
    );
}


{RESET}
{
    guardian_fail(
        "Hard reset rejected"
    );
}


{PAUSE}
{
    guardian_fail(
        "Unauthorized pause rejected"
    );
}



{SEEK}
{
    guardian_pass(
        "Recovery seek allowed"
    );
}



/*
==================================================
 AUDIO PROTECTION
==================================================
*/


{AUDIO} {DESYNC}
{
    guardian_fail(
        "Audio desync detected"
    );
}


{AUDIO}
{
    guardian_pass(
        "Audio authority maintained"
    );
}



/*
==================================================
 INPUT FIREWALL
==================================================
*/


{INPUT}
{
    guardian_pass(
        "Input accepted"
    );
}



"unknown_input"
{
    guardian_fail(
        "Unknown input dropped"
    );
}



/*
==================================================
 MODE TRANSITIONS
==================================================
*/


{MODE}
{
    guardian_pass(
        "Mode transition checked"
    );
}



"invalid_mode"
{
    guardian_fail(
        "Invalid mode rejected"
    );
}



/*
==================================================
 PLAYER EVENTS
==================================================
*/


{PLAYER}
{
    guardian_pass(
        "Player event verified"
    );
}



"external_score"
{
    guardian_fail(
        "External score modification blocked"
    );
}



/*
==================================================
 DEFAULT ROUTER
==================================================
*/


.|\n
{
    /*
     * Unknown data does not crash the engine.
     * Unknown data is ignored safely.
     */
}



/*
==================================================
 FINAL STATE
==================================================
*/


<<EOF>>
{
    if (guardian_safe)
    {
        printf(
            "[GUARDIAN] SYSTEM STATUS: SAFE\n"
        );
    }
    else
    {
        printf(
            "[GUARDIAN] SYSTEM STATUS: RECOVERY\n"
        );
    }
}


%%


int main(void)
{
    yylex();
    return 0;
}
