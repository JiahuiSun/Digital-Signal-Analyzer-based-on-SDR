#include <stdio.h>
//#include <math.h>
#include <tgmath.h>
#include <string.h>
#include <malloc.h>
#include <stdlib.h>
#include <stdio.h>
//#include <math.h>
#include <tgmath.h>
#include <string.h>
#include <malloc.h>
#include <stdlib.h>

int modulate(int *PI_in_mod,double *PD_out_mod_real_part,double *PD_out_mod_imag_part,int I_info_len , int I_mod_order);
int ModFSK(int *PI_in_mod, long int *freq_set, int sample_per_sym, double *PD_out_mod_real_part,int I_info_len,int I_mod_order);
