#include <stdio.h>
//#include <math.h>
#include <tgmath.h>
#include <string.h>
#include <malloc.h>
#include <stdlib.h>

/***********************************************************
Function Name:
	CSM_amplifier;
Function Description:
	���ȷŴ�;
Inputs:
	PD_in_amplifier_real_part		������˫������Ϣ����ʵ����
	PD_in_amplifier_imag_part		������˫������Ϣ�����鲿��
	I_info_len						�����볤�ȣ�
	PS_out_amplifier_real_part		�����short��Ϣ���У�
	D_ampli_mult					��������
	I_max_bits						������޷�ֵ�������Ϣ����λ����
	B_normalize_flag				����һ����־λ��1Ϊ��һ��
	B_top_bit_zero_flag				: ���bit�����־λ��1Ϊ����
Outputs:
	����0������
	����1����Ϣ���Ȳ��Ϸ�
	����2�������źŲ��Ϸ�
***********************************************************/
int	CSM_amplifier(double *PD_in_amplifier_real_part, double *PD_in_amplifier_imag_part, int I_info_len, short *PS_out_amplifier_real_part, short *PS_out_amplifier_imag_part, double D_ampli_mult, int I_max_bits, int B_normalize_flag)
{
	int i,result;
	short int_max_num;
	short int_min_num;
	double double_max_num;
	double double_min_num;
	short int_max_num_top_bit_zero;
	short int_min_num_top_bit_zero;
	double D_mult_result_real_part;
	double D_mult_result_imag_part;
	double D_out_average;
	double D_average_sqrt;

	/*���λ��*/
	if(I_max_bits > 16)
	{
		return 1;
	}

	/*����ֵ*/
	int_max_num = (1<<(I_max_bits-1)) - 1;
	int_min_num = -(1<<(I_max_bits-1));
	double_max_num = (double)int_max_num;
	double_min_num = (double)int_min_num;
	int_max_num_top_bit_zero = int_max_num & 0x7FFF;
	int_min_num_top_bit_zero = int_min_num & 0x7FFF;


	/*��һ��*/
	if (B_normalize_flag)
	{
		result = CSM_average(PD_in_amplifier_real_part, PD_in_amplifier_imag_part, I_info_len, &D_out_average);
		
		if(D_out_average<(1e-8) && D_out_average>-(1e-8))
		{
			return 2;
		}
		
		D_average_sqrt = sqrt(D_out_average);
		//printf("mean_amp = %f\n", D_average_sqrt);
		for (i=0; i<I_info_len; i++)
		{
			D_mult_result_real_part = PD_in_amplifier_real_part[i] / D_average_sqrt * D_ampli_mult;
			D_mult_result_imag_part = PD_in_amplifier_imag_part[i] / D_average_sqrt * D_ampli_mult;

			/*ʵ���޷����*/
			if(D_mult_result_real_part < double_max_num && D_mult_result_real_part > double_min_num)
			{
				PS_out_amplifier_real_part[i] = (short)D_mult_result_real_part;
			}
			else if(D_mult_result_real_part < double_min_num)
			{
				PS_out_amplifier_real_part[i] = int_min_num_top_bit_zero;
			}
			else
			{
				PS_out_amplifier_real_part[i] = int_max_num_top_bit_zero;
			}
			/*�鲿�޷����*/
			if(D_mult_result_imag_part < double_max_num && D_mult_result_imag_part > double_min_num)
			{
				PS_out_amplifier_imag_part[i] = (short)D_mult_result_imag_part;
				
			}
			else if(D_mult_result_imag_part < double_min_num)
			{
				PS_out_amplifier_imag_part[i] = int_min_num_top_bit_zero;
			}
			else
			{
				PS_out_amplifier_imag_part[i] = int_max_num_top_bit_zero;
			}

		}
	}
	else
	{

		if (D_ampli_mult<1+(1e-8) && D_ampli_mult>1-(1e-8))
		{
			for (i=0; i<I_info_len; i++)
			{
				/*ʵ���޷����*/
				if(PD_in_amplifier_real_part[i] < double_max_num && PD_in_amplifier_real_part[i]> double_min_num)
				{
					PS_out_amplifier_real_part[i] = (short)PD_in_amplifier_real_part[i];
				}
				else if(PD_in_amplifier_real_part[i] < double_min_num)
				{
					PS_out_amplifier_real_part[i] = int_min_num_top_bit_zero;
				}
				else
				{
					PS_out_amplifier_real_part[i] = int_max_num_top_bit_zero;
				}
				/*�鲿�޷����*/
				if(PD_in_amplifier_imag_part[i] < double_max_num && PD_in_amplifier_imag_part[i] > double_min_num)
				{
					PS_out_amplifier_imag_part[i] = (short)PD_in_amplifier_imag_part[i];
				
				}
				else if(PD_in_amplifier_imag_part[i] < double_min_num)
				{
					PS_out_amplifier_imag_part[i] = int_min_num_top_bit_zero;
				}
				else
				{
					PS_out_amplifier_imag_part[i] = int_max_num_top_bit_zero;
				}
			}
		}
		else
		{
			for (i=0; i<I_info_len; i++)
			{
				D_mult_result_real_part = PD_in_amplifier_real_part[i] * D_ampli_mult;
				D_mult_result_imag_part = PD_in_amplifier_imag_part[i] * D_ampli_mult;

				/*ʵ���޷����*/
				if(D_mult_result_real_part < double_max_num && D_mult_result_real_part > double_min_num)
				{
					PS_out_amplifier_real_part[i] = (short)D_mult_result_real_part;
				}
				else if(D_mult_result_real_part < double_min_num)
				{
					PS_out_amplifier_real_part[i] = int_min_num_top_bit_zero;
				}
				else
				{
					PS_out_amplifier_real_part[i] = int_max_num_top_bit_zero;
				}
				/*�鲿�޷����*/
				if(D_mult_result_imag_part < double_max_num && D_mult_result_imag_part > double_min_num)
				{
					PS_out_amplifier_imag_part[i] = (short)D_mult_result_imag_part;
				
				}
				else if(D_mult_result_imag_part < double_min_num)
				{
					PS_out_amplifier_imag_part[i] = int_min_num_top_bit_zero;
				}
				else
				{
					PS_out_amplifier_imag_part[i] = int_max_num_top_bit_zero;
				}
			}
		}
	}


	return 0;
}

int CSM_average(double *PD_in_average_real_part, double *PD_in_average_imag_part, int I_info_len, double *PD_out_average)
{
	int		i;
	double	D_sig_square = 0;
	double	D_sig_square_sum = 0;

	if(I_info_len < 1)
	{
		return 1;
	}

	/*������ƽ���ۼ�*/
	for(i=0; i<I_info_len; i++)
	{
		D_sig_square = PD_in_average_real_part[i]*PD_in_average_real_part[i] + PD_in_average_imag_part[i]*PD_in_average_imag_part[i];
		D_sig_square_sum += D_sig_square;
	}

	//printf("I_info_len, total_power = %d, %f\n", I_info_len, D_sig_square_sum);

	/*ƽ���������*/
	*PD_out_average = D_sig_square_sum/(I_info_len);

	return 0;
}

/***********************************************************
Function Name:
	CSM_data_combiner;
Function Description:
	���ݺϲ�;
Inputs:
	PS_in_data_real_part	������short��Ϣ����ʵ��(����1��2��3��4)��
	PS_in_data_imag_part	������short��Ϣ�����鲿(����5��6��7��8)��
	PS_out_data_combined	�����short�ϲ������Ϣ����(����1��5��2��6��3��7��4��8)��
	I_info_len				���������Ϣ���г��ȣ���ʵ�����ȣ�
Outputs:
	����0������
***********************************************************/

int CSM_data_combiner(short *PS_in_data_real_part, short *PS_in_data_imag_part, short *PS_out_data_combined, int I_info_len)
{
	int i;

	for(i=0; i<I_info_len; i++)
	{
		PS_out_data_combined[2*i] = PS_in_data_real_part[i];
		PS_out_data_combined[2*i + 1] = PS_in_data_imag_part[i];
	}

	return 0;
}

/***********************************************************
Function Name:
	CSM_data_separater;
Function Description:
	���ݷ���;
Inputs:
	PS_in_data_combined		������short��Ϣ����ָ��(����1��5��2��6��3��7��4��8)��
	PD_out_data_real_part	�����double��Ϣ����ʵ��ָ��(����1.0��2.0��3.0��4.0)��
	PD_out_data_imag_part	������double��Ϣ�����鲿ָ��(����5.0��6.0��7.0��8.0)��
	I_info_len				���������Ϣ���г��ȣ���ʵ�����ȣ�
Outputs:
	����0������
***********************************************************/

int CSM_data_separater(short *PS_in_data_combined, double *PD_out_data_real_part, double *PD_out_data_imag_part, int I_info_len)
{
	int i;

	for(i=0; i<I_info_len; i++)
	{
		PD_out_data_real_part[i] = (double)PS_in_data_combined[2*i];
		PD_out_data_imag_part[i] = (double)PS_in_data_combined[2*i+1];
	}

	return 0;
}
