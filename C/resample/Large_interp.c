/***********************************************************
Company Name:
	清华大学无线中心;
Function Name:
	Large_interp;
Function Description:
	;拉格朗日内插
Inputs:
	d_os_sig					   ： 输入信号
	os_sig_len                     ： 输入信号长度
	d_new_idx					   :  内插系数
	new_idx_len                    ： 内插系数长度

	d_out_sig					   :  输出信号
	out_sig_len					   ： 输出信号长度
Outputs:
	返回0：正常；
	返回1：输入信号长度超出设定最大值；
	返回2：输入new_idx的长度超出设定最大值；
	返回3：下标值超过输入信号长度

Notes: 
**************************************************************************/
#include "Large_interp.h"

int Large_interp(d_type d_os_sig[], int os_sig_len, d_type d_new_idx[], int new_idx_len, d_type *d_out_sig, int *out_sig_len)
{
	int i = 0;
	int i_num;
	int i_num_tmp;

	d_type d_frac;
	d_type d_params = 1.0/3;
	d_type d_c0;
	d_type d_tmp1;
	d_type d_tmp2;
	d_type d_c1;
	d_type d_c2;
	d_type d_c3;
	d_type d_mult1;
	d_type d_mult2;
	d_type d_mult3;

	if (os_sig_len > LARGE_INTERP_OS_SIG_LEN)
	{
		return 1;
	}

	if (new_idx_len > LARGE_INTERP_NEW_IDX_LEN)
	{
		return 2;
	}

	for (i=0; i<new_idx_len; i++)
	{
		i_num_tmp = floorf(d_new_idx[i]);
		d_frac = d_new_idx[i] - i_num_tmp;
		i_num = i_num_tmp - 1;

		if (i_num > os_sig_len)
		{
			return 3;
		}

		d_c0 = d_os_sig[i_num];
		d_tmp1 = d_params * d_os_sig[i_num - 1];
		d_tmp2 = d_params * d_os_sig[i_num + 2];

		d_c1 = d_os_sig[i_num + 1] - d_tmp1 - d_os_sig[i_num]/2 - d_tmp2/2;
		d_c2 = (d_os_sig[i_num - 1] + d_os_sig[i_num + 1])/2 - d_os_sig[i_num];
		d_c3 = d_params/2 * (d_os_sig[i_num + 2] - d_os_sig[i_num - 1]) + (d_os_sig[i_num] - d_os_sig[i_num + 1])/2;
			
		d_mult1 = d_c3 * d_frac;
		d_mult2 = (d_mult1 + d_c2) * d_frac;
		d_mult3 = (d_mult2 + d_c1) * d_frac;

		d_out_sig[i] = d_mult3 + d_c0;
	}

	*out_sig_len = new_idx_len;

	return 0;
}
