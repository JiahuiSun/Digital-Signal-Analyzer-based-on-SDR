#include <stdio.h>
#include <math.h>
#include <string.h>

#include "type_unsamplefilter.h"
#include "shape_filter.h"

#include "type_CSM.h"


/*ÉÏ²ÉÑù*/
int unsamplefilter(d_type d_os_sig[], int os_sig_len, Unsamplefilter_Para *P_unsamplefilter_parameter , d_type *d_state_tx_upfs, int state_tx_upfs_row, int state_tx_upfs_col, d_type *d_ds_sig, int *ds_sig_len);
