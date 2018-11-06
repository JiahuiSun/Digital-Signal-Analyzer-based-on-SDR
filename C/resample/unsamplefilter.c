/***********************************************************
Company Name:
	清华大学无线中心;
Function Name:
	unsamplefilter;
Function Description:
	上采样
Inputs:
	d_os_sig									：输入信号序列地址
	os_sig_len									：输入信号序列长度
	P_unsamplefilter_parameter->os_N            : 输入，
	P_unsamplefilter_parameter->filter_order	: 滤波器阶数
	P_unsamplefilter_parameter->b2				：输入滤波器系数b2
	P_unsamplefilter_parameter->b3              : 输入滤波器系数b3
	P_unsamplefilter_parameter->forward_sim		：发送方向 1为前向，0为返向
	P_unsamplefilter_parameter_b2_len			：输入滤波器系数b2长度
	P_unsamplefilter_parameter_b3_len			：输入滤波器系数b3长度

	d_state_rx_dnfs								：输入输出，状态值，二维数组
	state_tx_upfs_row							：输入输出，状态值，数组行数
	state_tx_upfs_clo							：输入输出，状态值，数组列数

	d_ds_sig								    ：输出信号序列地址
	ds_sig_len									：输出信号序列长度
Outputs:
	返回0：正常
	返回1：输入信号长度超设定最大值
	返回2：输入b2长度超过设定最大值
	返回3：输入b3长度超过设定最大值
	返回4：状态值行数超过设定最大值
	返回5：状态值列数超过设定最大值
	返回6：no this case happen
	返回7：no this case happen
Notes: 
**************************************************************************/

#include "unsamplefilter.h"

int unsamplefilter(d_type d_os_sig[], int os_sig_len, Unsamplefilter_Para *P_unsamplefilter_parameter , d_type *d_state_tx_upfs, int state_tx_upfs_row, int state_tx_upfs_col, d_type *d_ds_sig, int *ds_sig_len)
{
	int i,j;
	int i_os;
	int i_os_N;
	int result;
	int i_sig_len;
	int i_dat_pos;

	d_type *state_tx_upfs_tmp;
	d_type d_delay;
	d_type d_lenpersym;
	d_type d_tmp_sig[UNSAMPLEFILTER_DS_SIG_LEN];
	d_type d_params_b[UNSAMPLEFILTER_B2_LEN];
	d_type d_sig_ov[UNSAMPLEFILTER_DS_SIG_LEN];
 
	if (os_sig_len > UNSAMPLEFILTER_OS_SIG_LEN)
	{
		return 1;
	}

	if (P_unsamplefilter_parameter->b2_len > UNSAMPLEFILTER_B2_LEN)
	{
		return 2;
	}

	if (P_unsamplefilter_parameter->b3_len > UNSAMPLEFILTER_B2_LEN)
	{
		return 3;
	}

	if (state_tx_upfs_row > UNSAMPLEFILTER_STATE_TX_UPFS_ROW)
	{
		return 4;
	}

	if (state_tx_upfs_col > UNSAMPLEFILTER_STATE_TX_UPFS_COL)
	{
		return 5;
	}

	// added by GAO 20150519
	d_delay = P_unsamplefilter_parameter->delay;
	i_sig_len = P_unsamplefilter_parameter->sig_len;
	//printf("Input %f, %d: \n", d_delay, i_sig_len);

	for (i=0; i<os_sig_len; i++)
	{
		d_tmp_sig[i] = d_os_sig[i];
	}

	i_os_N = P_unsamplefilter_parameter->os_N;

	for (i=0; i<P_unsamplefilter_parameter->filter_order; i++)
	{
		if (i_os_N % 2==0)
		{
			i_os = 2;
			for (j=0; j<P_unsamplefilter_parameter->b2_len; j++)
			{
				d_params_b[j] = P_unsamplefilter_parameter->b2[j];
			}
		}
		else if (i_os_N % 3==0)
		{
			i_os = 3;
			for (j=0; j<P_unsamplefilter_parameter->b3_len; j++)
			{
				d_params_b[j] = P_unsamplefilter_parameter->b3[j];
			}
		}
		else if (i_os_N == 1)
			return 2;
		else
			return 3;

		i_os_N = i_os_N / i_os;
		
		for (j=0; j<os_sig_len; j++)
		{
			d_sig_ov[j*i_os] = d_tmp_sig[j]; 
			d_sig_ov[j*i_os+1] = 0;
		}

		os_sig_len = os_sig_len * i_os;
		state_tx_upfs_tmp = d_state_tx_upfs + state_tx_upfs_col*i;     /*将每一个行的首地址赋给state_tx_upfs_tmp*/
		result = shape_filter(d_sig_ov, os_sig_len, d_tmp_sig, d_params_b, UNSAMPLEFILTER_B2_LEN, state_tx_upfs_tmp);

		if (P_unsamplefilter_parameter->forward_sim == 0)
		{
			for (j=0; j<state_tx_upfs_col; j++)
			{
				//d_tmp_sig[os_sig_len - 1 + (i+1)*j] = d_state_tx_upfs[i*state_tx_upfs_col+j];
				d_tmp_sig[os_sig_len + j] = d_state_tx_upfs[i*state_tx_upfs_col+j];
			}
			//added by GAO 20150519
			os_sig_len = os_sig_len + state_tx_upfs_col;
			d_delay = i_os * d_delay + P_unsamplefilter_parameter->b2_len-1;
			i_sig_len = i_os * i_sig_len;
			//printf("sig_len = %d\n",os_sig_len);
		}
	}

	if (P_unsamplefilter_parameter->forward_sim == 1)
	{
		for (j=0; j<os_sig_len; j++)
		{
			d_ds_sig[j] = d_tmp_sig[j];
		}
		*ds_sig_len = os_sig_len;
	}
	else
	{
		d_lenpersym = P_unsamplefilter_parameter->os_N * P_unsamplefilter_parameter->tx_os / P_unsamplefilter_parameter->inter_factor;
		//printf("d_delay,d_lenpersym = %f, %f\n",d_delay,d_lenpersym);
		for (j=0; j<i_sig_len; j++)
		{
			i_dat_pos = floor((d_delay - d_lenpersym)/2) + j;
			d_ds_sig[j] = d_tmp_sig[i_dat_pos];
			
		}

		//printf("Output %f, %d:\n", d_delay, i_sig_len);
		//d_delay = 0;
		//i_sig_len = 0;
		*ds_sig_len = i_sig_len;
	}
	return 0;
}
