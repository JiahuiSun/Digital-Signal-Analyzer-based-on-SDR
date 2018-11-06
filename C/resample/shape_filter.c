/***********************************************************
Company Name:
	Çå»ªŽóÑ§ÎÞÏßÖÐÐÄ;
Function Name:
	shape_filter;
Function Description:
	³ÉÐÍÂË²šÆ÷£¬¿ÉžœŽøÂË²šÆ÷×ŽÌ¬;
Inputs:
	PD_in_info			
	I_info_len			
	PD_out_shape_filter		
	PD_filter_conf			
	I_conf_len			
	PD_filter_state			
Outputs:
	·µ»Ø0£ºÕý³£
	·µ»Ø1£ºÂË²šÆ÷ÏµÊý³€¶È¹ý³€
	·µ»Ø2£ºÂË²šÆ÷ÏµÊý³€¶È²»ºÏ·š
Notes: ±Ÿº¯Êýµ÷ÓÃµÄº¯ÊýÇåµ¥Œ°ÆäËû
***********************************************************/
#include "shape_filter.h"

int shape_filter(d_type *PD_in_info, int I_info_len, d_type *PD_out_shape_filter, d_type *PD_filter_conf, int I_conf_len, d_type *PD_filter_state)
{
	int i,j;
	int I_conf_len_minus = I_conf_len -1;
	int I_half_conf_len = I_conf_len_minus/2;
	d_type D_conv_add_up;
	d_type PD_tmp_state[MAX_FILTER_CONF_LEN] = {0};

	if (I_conf_len > MAX_FILTER_CONF_LEN)
	{
		return 1;
	}
	if (!(I_conf_len^1))
	{
		return 2;
	}
	
	for (i=-I_conf_len_minus; i<I_info_len-I_conf_len_minus; i++)
	{
		D_conv_add_up = 0;

		for (j=0; j<I_conf_len; j++)
		{
			if ((i+j)<0 || (i+j)>I_info_len-1)
			{
				continue;
			}
			D_conv_add_up += (PD_in_info[i+j] * PD_filter_conf[I_conf_len-1-j]);
		}
		PD_out_shape_filter[i+I_conf_len_minus] = D_conv_add_up;
	}

	for (i=I_info_len-I_conf_len_minus; i<I_info_len; i++)
	{
		D_conv_add_up = 0;

		for (j=0; j<I_conf_len; j++)
		{
			if ((i+j)<0 || (i+j)>I_info_len-1)
			{
				continue;
			}
			D_conv_add_up += (PD_in_info[i+j] * PD_filter_conf[I_conf_len-1-j]);
		}
		PD_tmp_state[i-I_info_len+I_conf_len_minus] = D_conv_add_up;
	}

	for (i=0; i<I_conf_len_minus; i++)
	{
		PD_out_shape_filter[i] += PD_filter_state[i];
		PD_filter_state[i] = PD_tmp_state[i];
	}

	return 0;
}
