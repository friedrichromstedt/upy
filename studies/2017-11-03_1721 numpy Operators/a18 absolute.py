from upy2 import u, U
U(1).default()

def ureport(ua):
    return ua.dependencies[0].derivatives

ua = 10 + u(-2)
squ = ua * ua.conj()

print ">>> ua = 10 +- 2"
print ">>> squ = (ua * ua.conj()), nominal, stddev and ureport"
print squ.nominal, squ.stddev, ureport(squ)

uabs = squ ** 0.5
print "uabs = squ ** 0.5, nominal, stddev and ureport"
print uabs.nominal, uabs.stddev, ureport(uabs)
