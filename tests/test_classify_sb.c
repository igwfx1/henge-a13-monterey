#include "classify.h"

#include <stdio.h>

int main(void) {
    /* SB is a system barrier and must reach the translator's host fallback. */
    const uint32_t sb = 0xd50330ffu;
    HvInsnKind kind = hv_classify(sb);
    if (kind != HV_INSN_BARRIER) {
        fprintf(stderr, "SB classified as %s, expected barrier\n", hv_insn_kind_name(kind));
        return 1;
    }
    puts("SB classification: PASS");
    return 0;
}
