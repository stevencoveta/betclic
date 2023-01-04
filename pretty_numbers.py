import math 

millnames = ['','k','M']

def prettify(n):
    n = float(n)
    if (n > 100000) & (n < 1000000):
        millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
        return '{:.3f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
    if n > 1000000:
        millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
        return '{:.3f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
    else: 
        millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
        return '{:.3f}{}'.format(n / 10**(3 * millidx), millnames[millidx])