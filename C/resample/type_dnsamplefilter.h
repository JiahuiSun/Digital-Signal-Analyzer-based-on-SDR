#include <stdio.h>
//#include <math.h>
#include <string.h>
#include "type_CSM.h"

#define DNSAMPLEFILTER_B_LEN 25								/* �²���ϵ������*/
#define DNSAMPLEFILTER_STATE_RX_DNFS_COL 24					/* ״ֵ̬��λ���飬����*/
#define DNSAMPLEFILTER_STATE_RX_DNFS_ROW 5					/* ״ֵ̬��λ���飬����*/
#define DNSAMPLEFILTER_OS_SIG_LEN 240480						/* �ź��²���ǰ����*/
#define DNSAMPLEFILTER_DS_SIG_LEN 7515						/* �ź��²����󳤶�*/

/**************************************************************
						�궨�壬�ṹ�嶨��
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
