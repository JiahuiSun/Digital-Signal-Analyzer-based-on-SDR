#include <stdio.h>
//#include <math.h>
#include <string.h>
#include "type_CSM.h"

#define DNSAMPLEFILTER_B_LEN 25								/* 下采样系数长度*/
#define DNSAMPLEFILTER_STATE_RX_DNFS_COL 24					/* 状态值二位数组，列数*/
#define DNSAMPLEFILTER_STATE_RX_DNFS_ROW 5					/* 状态值二位数组，行数*/
#define DNSAMPLEFILTER_OS_SIG_LEN 240480						/* 信号下采样前长度*/
#define DNSAMPLEFILTER_DS_SIG_LEN 7515						/* 信号下采样后长度*/

/**************************************************************
						宏定义，结构体定义
**************************************************************/

typedef struct tag_Dnsamplefilter_Para
{
	int os_N;
	int filter_order;
	int b2_len;
	int b3_len;
	//d_type b2[DNSAMPLEFILTER_B_LEN];
	//d_type b3[DNSAMPLEFILTER_B_LEN];
	d_type *b2;
	d_type *b3;
	int forward_sim;
}Dnsamplefilter_Para;
