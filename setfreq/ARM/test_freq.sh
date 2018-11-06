#!/bin/bash
#########配置方式 sh test_freq.sh rx_int rx_frac tx_int tx_frac 
if(test "$1" -lt 70)
then
echo "This is illegal input!!!"
elif(test "$1" -lt 94)
then
TX_DIV=6
elif(test "$1" -lt 188)
then
TX_DIV=5
elif(test "$1" -lt 375)
then
TX_DIV=4
elif(test "$1" -lt 750)
then
TX_DIV=3
elif(test "$1" -lt 1500)
then
TX_DIV=2
elif(test "$1" -lt 3000)
then
TX_DIV=1
elif(test "$1" -le 6000)
then
TX_DIV=0
else
echo "This is illegal input!!!"
fi

#TX的小数部分计算
FP1=10000
if(test "$3" -lt 70)
then
echo "This is illegal input!!!"
elif(test "$3" -lt 94)
then
RX_DIV=6
elif(test "$3" -lt 188)
then
RX_DIV=5
elif(test "$3" -lt 375)
then
RX_DIV=4
elif(test "$3" -lt 750)
then
RX_DIV=3
elif(test "$3" -lt 1500)
then
RX_DIV=2
elif(test "$3" -lt 3000)
then
RX_DIV=1
elif(test "$3" -le 6000)
then
RX_DIV=0
else
echo "This is illegal input!!!"
fi

#RX的小数部分计算
FP2=10000
DIV=$[TX_DIV+RX_DIV*16]

TX_INTEGER=$[($1*(2**(TX_DIV+1)))/50]
RX_INTEGER=$[($3*(2**(RX_DIV+1)))/50]

TX_FRACTIONAL=$[(8388593*($1*(2**(TX_DIV+1))))/50+(8388593*($2*(2**(TX_DIV+1))))/50/FP1-TX_INTEGER*8388593]
RX_FRACTIONAL=$[(8388593*($3*(2**(RX_DIV+1))))/50+(8388593*($4*(2**(TX_DIV+1))))/50/FP2-RX_INTEGER*8388593]

TX_FRACTIONAL3=$[TX_FRACTIONAL/(2**16)]
TX_FRACTIONAL2=$[(TX_FRACTIONAL-TX_FRACTIONAL3*(2**16))/(2**8)]
TX_FRACTIONAL1=$[TX_FRACTIONAL-TX_FRACTIONAL3*(2**16)-TX_FRACTIONAL2*(2**8)]

RX_FRACTIONAL3=$[RX_FRACTIONAL/(2**16)]
RX_FRACTIONAL2=$[(RX_FRACTIONAL-RX_FRACTIONAL3*(2**16))/(2**8)]
RX_FRACTIONAL1=$[RX_FRACTIONAL-RX_FRACTIONAL3*(2**16)-RX_FRACTIONAL2*(2**8)]

TX_INTEGER2=$[TX_INTEGER/(2**8)]
if(test "$TX_INTEGER2" -eq 0)
then
TX_INTEGER1=$TX_INTEGER
else
TX_INTEGER1=$[TX_INTEGER-TX_INTEGER*(2**8)]
fi

RX_INTEGER2=$[RX_INTEGER/(2**8)]
if(test "$RX_INTEGER2" -eq 0)
then
RX_INTEGER1=$RX_INTEGER
else
RX_INTEGER1=$[RX_INTEGER-RX_INTEGER*(2**8)]
fi

TX_FRACTIONAL3=`printf "%x" $TX_FRACTIONAL3`
TX_FRACTIONAL2=`printf "%x" $TX_FRACTIONAL2`
TX_FRACTIONAL1=`printf "%x" $TX_FRACTIONAL1`
TX_INTEGER2=`printf "%x" $TX_INTEGER2`
TX_INTEGER1=`printf "%x" $TX_INTEGER1`
RX_FRACTIONAL3=`printf "%x" $RX_FRACTIONAL3`
RX_FRACTIONAL2=`printf "%x" $RX_FRACTIONAL2`
RX_FRACTIONAL1=`printf "%x" $RX_FRACTIONAL1`
RX_INTEGER2=`printf "%x" $RX_INTEGER2`
RX_INTEGER1=`printf "%x" $RX_INTEGER1`
DIV=`printf "%x" $DIV`

./ad9361_config -w 233 $TX_FRACTIONAL1
./ad9361_config -w 234 $TX_FRACTIONAL2
./ad9361_config -w 235 $TX_FRACTIONAL3
./ad9361_config -w 232 $TX_INTEGER2
./ad9361_config -w 231 $TX_INTEGER1
./ad9361_config -w 005 $DIV

./ad9361_config -w 273 $RX_FRACTIONAL1
./ad9361_config -w 274 $RX_FRACTIONAL2
./ad9361_config -w 275 $RX_FRACTIONAL3
./ad9361_config -w 272 $RX_INTEGER2
./ad9361_config -w 271 $RX_INTEGER1 
./ad9361_config -w 005 $DIV

