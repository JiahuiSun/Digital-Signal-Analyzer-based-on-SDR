#include "modulate.h"

/***********************************************************
Company Name:
	Tianjin University;
Function Name:
	modulate;
Function Description:
	对信息序列进行BPSK\QPSK\16QAM调制;
Inputs:
	PI_in_mod			:	待调制信息序列数组指针,PI_in_mod[0]为最高位;
	PD_out_mod_real_part:	输出调制后实部信息序列数组指针,PD_out_mod_real_part[0]为最高位;
	PD_out_mod_imag_part:	输出调制后虚部信息序列数组指针,PD_out_mod_imag_part[0]为最高位;
	I_info_len			:	信息序列数组PI_in_mod长度;
	I_mod_order			:	调制符： "1"BPSK,"2"QPSK, "4"16QAM;
Outputs:
	返回0:正常;1:信息序列长度错误;
***********************************************************/


int modulate(int *PI_in_mod,double *PD_out_mod_real_part,double *PD_out_mod_imag_part,int I_info_len,int I_mod_order)
{
	int i,j;
	int I_sym_idx;
	double D_QPSK_real_part[4] = {0.7071067811865475, 0.7071067811865475, -0.7071067811865475, -0.7071067811865475};
	double D_QPSK_imag_part[4] = {0.7071067811865475, -0.7071067811865475, 0.7071067811865475, -0.7071067811865475};
	double D_16QAM_real_part[16] = {-0.9487,-0.3162,0.9487,0.3162,-0.9487,-0.3162,0.9487,0.3162,-0.9487,-0.3162,0.9487,0.3162,
	-0.9487,-0.3162,0.9487,0.3162};
	double D_16QAM_imag_part[16] = {-0.9487,-0.9487,-0.9487,-0.9487,-0.3162,-0.3162,-0.3162,-0.3162,0.9487,0.9487,0.9487,0.9487,
	0.3162,0.3162,0.3162,0.3162};
	
	/*如果长度不正确*/
	if ((I_mod_order == 2 && I_info_len%2 != 0) || (I_mod_order == 4 && I_info_len%4 != 0))
	{
		return 1;
	}
	/*长度正确*/
	else
	{
		if(I_mod_order == 1)
		/*寻找对应实部虚部输出*/
		{	
		
			for(i=0; i<I_info_len; i++)
			{
				PD_out_mod_real_part[i]=1.0-2*PI_in_mod[i];
				PD_out_mod_imag_part[i]=0;
			}
		
		}
		else if (I_mod_order == 2)
		{
			for(i=0,j=0; i<I_info_len; i+=2,j++)
			{
				I_sym_idx = (PI_in_mod[i]<<1) + PI_in_mod[i+1];
				PD_out_mod_real_part[j] = D_QPSK_real_part[I_sym_idx];
				PD_out_mod_imag_part[j] = D_QPSK_imag_part[I_sym_idx];
			}
			
		}
		else if (I_mod_order == 4)
		{
			for(i=0,j=0; i<I_info_len; i+=4,j++)
			{
				I_sym_idx = (PI_in_mod[i]<<3) + (PI_in_mod[i+1]<<2) + (PI_in_mod[i+2]<<1) + PI_in_mod[i+3];
				PD_out_mod_real_part[j] = D_16QAM_real_part[I_sym_idx];
				PD_out_mod_imag_part[j] = D_16QAM_imag_part[I_sym_idx];
			}
			
		}
		return 0;
	}
}
