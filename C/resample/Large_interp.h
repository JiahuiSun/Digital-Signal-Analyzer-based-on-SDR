#include <stdio.h>
#include <string.h>
#include "type_CSM.h"
/*拉格朗日内插*/

#define LARGE_INTERP_OS_SIG_LEN 110200     /*输入信号长度最大值*/
#define LARGE_INTERP_NEW_IDX_LEN 115000    /*内插系数长度最大值*/

int Large_interp(d_type d_os_sig[], int os_sig_len, d_type d_new_idx[], int new_idx_len, d_type *d_out_sig, int *out_sig_len);


