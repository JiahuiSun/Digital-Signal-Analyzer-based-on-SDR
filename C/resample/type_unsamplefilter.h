#include <stdio.h>
#include <string.h>
#include "type_CSM.h"

#define UNSAMPLEFILTER_B2_LEN 25						/* �ϲ���ϵ������*/
#define UNSAMPLEFILTER_STATE_TX_UPFS_COL 24             /* ״ֵ̬��λ���飬����*/
//#define UNSAMPLEFILTER_STATE_TX_UPFS_ROW 3              /* ״ֵ̬��λ���飬����*/
//#define UNSAMPLEFILTER_OS_SIG_LEN 3902					/* �ź��ϲ���ǰ����*/
//#define UNSAMPLEFILTER_DS_SIG_LEN 31216					/* �ź��ϲ����󳤶�*/


#define UNSAMPLEFILTER_STATE_TX_UPFS_ROW 5              /* ״ֵ̬��λ���飬����*/
#define UNSAMPLEFILTER_OS_SIG_LEN 115000					/* �ź��ϲ���ǰ����*/
#define UNSAMPLEFILTER_DS_SIG_LEN 240480 				/* �ź��ϲ����󳤶�*/


/**************************************************************
						�궨�壬�ṹ�嶨��
**************************************************************/

typedef struct tag_Unsamplefilter_Para
{
	int os_N;
	int forward_sim;
	int filter_order;
	int b2_len;
	int b3_len;

	d_type tx_os;
	d_type inter_factor;
	//d_type b2[UNSAMPLEFILTER_B2_LEN];
	//d_type b3[UNSAMPLEFILTER_B2_LEN];
	d_type *b2;
	d_type *b3;
	d_type delay;
	int sig_len;
}Unsamplefilter_Para;