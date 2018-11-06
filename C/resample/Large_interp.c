/***********************************************************
Company Name:
	�廪��ѧ��������;
Function Name:
	Large_interp;
Function Description:
	;���������ڲ�
Inputs:
	d_os_sig					   �� �����ź�
	os_sig_len                     �� �����źų���
	d_new_idx					   :  �ڲ�ϵ��
	new_idx_len                    �� �ڲ�ϵ������

	d_out_sig					   :  ����ź�
	out_sig_len					   �� ����źų���
Outputs:
	����0��������
	����1�������źų��ȳ����趨���ֵ��
	����2������new_idx�ĳ��ȳ����趨���ֵ��
	����3���±�ֵ���������źų���

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
