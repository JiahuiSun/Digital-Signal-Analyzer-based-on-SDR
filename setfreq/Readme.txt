cd ARM
sftp root@10.0.77.112
put ParaSet.py /tmp     #把要用的程序通过socket传进ARM里
put test_freq.sh /tmp
put ad9361_config /tmp
(ctrl+D)
ssh root@10.0.77.112
cd /tmp
python ParaSat.py       #在ARM端启动接收中心频点的线程

PC                      #这是测试用的，咱们不需要
ParaSetCliSock.py: you must use for parameter setting
ParaSetTest.py: just an example for how to use ParaSetCliSock.py


# 一下所有是我FM用的，也就是在ARM上直接修改频点
Change tx/rx frequency on ARM:
cd /ARM
sftp root@10.0.77.112
put test_freq.sh /tmp
put ad9361_config /tmp
(ctrl+D: exit from sftp)
ssh root@10.0.77.112
cd /tmp

./test_freq.sh 1995 0000 2000 0000 # rx_freq = 1995MHz, tx_freq = 2000MHz
chmod +x ad9361_config获取权限
用ls -l查看权限
要么是：./test_freq.sh ……
要么是：sh test_freq.sh ……stfp
rx_freq和tx_freq的范围是70-3G，不能超过范围。

