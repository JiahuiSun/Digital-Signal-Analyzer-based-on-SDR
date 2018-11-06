#include <stdio.h>
#include <string.h>
#include "type_CSM.h"
/*拉格朗日内插*/

#define LARGE_INTERP_OS_SIG_LEN 110200     /*输入信号长度最大值*/
#define LARGE_INTERP_NEW_IDX_LEN 58000    /*内插系数长度最大值*/

typedef struct tag_Air_mid_la
{
	d_type		interp_factor;
	d_type		fracst;
	d_type		timeo; 
}Air_mid_la_para;	


//int Large_interp(d_type d_os_sig[], int os_sig_len, d_type d_new_idx[], int new_idx_len, d_type *d_out_sig, int *out_sig_len);
int Large_interp1(d_type d_os_sig_real[], d_type d_os_sig_imag[], int os_sig_len, Air_mid_la_para *p_Air_mid_la_para, d_type *d_out_sig_real, d_type *d_out_sig_imag, int *out_sig_len, d_type *d_out_fracst, int tx_rx_flag);


