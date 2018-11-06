
def set_para(rx_freq):
    freq = str(a)
    if '.' in freq:
        tmp_str = freq.split('.')
        zero_num = 4-len(tmp_str[1])
        freq = freq + zero_num*'0'
    else:
        freq = freq + '.0000'
        
    print freq

a = 1995.123
set_para(a)
