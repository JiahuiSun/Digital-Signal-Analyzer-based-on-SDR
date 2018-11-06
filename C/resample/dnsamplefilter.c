/***********************************************************
Company Name:
	�廪��ѧ��������;
Function Name:
	dnsamplefilter;
Function Description:
	�²���
Inputs:
	d_os_sig									�����룬�ź�
	os_sig_len									�����룬�źų���
	P_dnsamplefilter_parameter->os_N            : ���룬
	P_dnsamplefilter_parameter->filter_order	: ���룬
	P_dnsamplefilter_parameter->b2				�����룬����ϵ��
	P_dnsamplefilter_parameter->b3              : ���룬����ϵ��
	P_dnsamplefilter_parameter->forward_sim		�����룬
	P_dnsamplefilter_parameter_b2_len			�����룬ϵ������
	P_dnsamplefilter_parameter_b3_len			�����룬ϵ������

	d_state_rx_dnfs								�����������״ֵ̬����ά����
	state_rx_dnfs_row							�����������״ֵ̬����������
	state_rx_dnfs_clo							�����������״ֵ̬����������

	d_ds_sig								    ��������������ź�
	ds_sig_len									������źų���
Outputs:
	����0������
	����1�������źų��ȳ��趨���ֵ
	����2������b2���ȳ����趨���ֵ
	����3������b3���ȳ����趨���ֵ
	����4��״ֵ̬���������趨���ֵ
	����5��״ֵ̬���������趨���ֵ
	����6��no this case happen
	����7��no this case happen

Notes: 
**************************************************************************/

#include "dnsamplefilter.h"

int dnsamplefilter(d_type d_os_sig[],int os_sig_len, Dnsamplefilter_Para *P_dnsamplefilter_parameter, d_type *d_state_rx_dnfs, int state_rx_dnfs_row, int state_rx_dnfs_col, d_type *d_ds_sig, int *ds_sig_len)
{
	int i,j;
	int i_os;
	int i_result;
	int i_os_N;

	d_type *state_tx_upfs_tmp;
	d_type d_params_b[DNSAMPLEFILTER_B_LEN];
	d_type d_ds_sig_tmp[DNSAMPLEFILTER_OS_SIG_LEN];
	d_type d_sig_ov[DNSAMPLEFILTER_OS_SIG_LEN];

	if (os_sig_len > DNSAMPLEFILTER_OS_SIG_LEN)
	{
		return 1;
	}
	
	if (P_dnsamplefilter_parameter->b2_len > DNSAMPLEFILTER_B_LEN)
	{
		return 2;
	}

	if (P_dnsamplefilter_parameter->b3_len > DNSAMPLEFILTER_B_LEN)
	{
		return 3;
	}

	if (state_rx_dnfs_row > DNSAMPLEFILTER_STATE_RX_DNFS_ROW)
	{
		return 4;
	}

	if (state_rx_dnfs_col > DNSAMPLEFILTER_STATE_RX_DNFS_COL)
	{
		return 5;
	}

	for (i=0; i<os_sig_len; i++)
	{
		d_ds_sig_tmp[i] = d_os_sig[i];
	}

	i_os_N = P_dnsamplefilter_parameter->os_N;

	for (i=0; i<(P_dnsamplefilter_parameter->filter_order); i++)
	{
		if ((i_os_N) % 2 == 0)
		{
			i_os = 2;
			for (j=0; j<P_dnsamplefilter_parameter->b2_len; j++)
			{
				d_params_b[j] = P_dnsamplefilter_parameter->b2[j];
			}
		}
		else if ((i_os_N) % 3 == 0)
		{
			i_os = 3;
			for (j=0; j<P_dnsamplefilter_parameter->b2_len; j++)
			{
				d_params_b[j] = P_dnsamplefilter_parameter->b3[j];
			}
		}
		else if ((i_os_N) == 1)
			return 6;
		else
			return 7;

		i_os_N = (i_os_N) / i_os;
		state_tx_upfs_tmp = (d_state_rx_dnfs + state_rx_dnfs_col*i);     /*��ÿһ���е��׵�ַ����state_tx_upfs_tmp*/
		i_result = shape_filter(d_ds_sig_tmp, os_sig_len, d_sig_ov, d_params_b, P_dnsamplefilter_parameter->b2_len, state_tx_upfs_tmp);

		if (P_dnsamplefilter_parameter->forward_sim == 0)
		{
			for (j=0; j<state_rx_dnfs_col; j++)
			{
				d_ds_sig_tmp[os_sig_len + (i+1)*j] = d_state_rx_dnfs[i*state_rx_dnfs_col+j];
			}
		}

		for (j=0; j<os_sig_len; j=j+i_os)
		{
			d_ds_sig_tmp[j/i_os]=d_sig_ov[j];
		}

		os_sig_len = os_sig_len / i_os;
	}

	for (i=0; i<os_sig_len; i++)
	{
		d_ds_sig[i] = d_ds_sig_tmp[i];
	}
	*ds_sig_len = os_sig_len;
	return 0;
}

int dnsamplefilter_offset(d_type d_os_sig[],int os_sig_len, Dnsamplefilter_Para *P_dnsamplefilter_parameter, d_type *d_state_rx_dnfs, int state_rx_dnfs_row, int state_rx_dnfs_col, d_type *d_ds_sig, int offset, int *ds_sig_len)
{
	int i,j;
	int i_os;
	int i_result;
	int i_os_N;

	d_type *state_tx_upfs_tmp;
	d_type d_params_b[DNSAMPLEFILTER_B_LEN];
	d_type d_ds_sig_tmp[DNSAMPLEFILTER_OS_SIG_LEN];
	d_type d_sig_ov[DNSAMPLEFILTER_OS_SIG_LEN];

	if (os_sig_len > DNSAMPLEFILTER_OS_SIG_LEN)
	{
		return 1;
	}
	
	if (P_dnsamplefilter_parameter->b2_len > DNSAMPLEFILTER_B_LEN)
	{
		return 2;
	}

	if (P_dnsamplefilter_parameter->b3_len > DNSAMPLEFILTER_B_LEN)
	{
		return 3;
	}

	if (state_rx_dnfs_row > DNSAMPLEFILTER_STATE_RX_DNFS_ROW)
	{
		return 4;
	}

	if (state_rx_dnfs_col > DNSAMPLEFILTER_STATE_RX_DNFS_COL)
	{
		return 5;
	}

	for (i=0; i<os_sig_len; i++)
	{
		d_ds_sig_tmp[i] = d_os_sig[i];
	}

	i_os_N = P_dnsamplefilter_parameter->os_N;

	for (i=0; i<(P_dnsamplefilter_parameter->filter_order); i++)
	{
		if ((i_os_N) % 2 == 0)
		{
			i_os = 2;
			for (j=0; j<P_dnsamplefilter_parameter->b2_len; j++)
			{
				d_params_b[j] = P_dnsamplefilter_parameter->b2[j];
			}
		}
		else if ((i_os_N) % 3 == 0)
		{
			i_os = 3;
			for (j=0; j<P_dnsamplefilter_parameter->b2_len; j++)
			{
				d_params_b[j] = P_dnsamplefilter_parameter->b3[j];
			}
		}
		else if ((i_os_N) == 1)
			return 6;
		else
			return 7;

		i_os_N = (i_os_N) / i_os;
		state_tx_upfs_tmp = (d_state_rx_dnfs + state_rx_dnfs_col*i);     /*��ÿһ���е��׵�ַ����state_tx_upfs_tmp*/
		i_result = shape_filter(d_ds_sig_tmp, os_sig_len, d_sig_ov, d_params_b, P_dnsamplefilter_parameter->b2_len, state_tx_upfs_tmp);

		if (P_dnsamplefilter_parameter->forward_sim == 0)
		{
			for (j=0; j<state_rx_dnfs_col; j++)
			{
				d_ds_sig_tmp[os_sig_len + (i+1)*j] = d_state_rx_dnfs[i*state_rx_dnfs_col+j];
			}
		}

		for (j=0; j<os_sig_len; j=j+i_os)
		{
			d_ds_sig_tmp[j/i_os]=d_sig_ov[j];
		}

		os_sig_len = os_sig_len / i_os;
	}

	for (i=0; i<os_sig_len; i++)
	{
		d_ds_sig[i+offset] = d_ds_sig_tmp[i];
	}
	*ds_sig_len = os_sig_len;
	return 0;
}