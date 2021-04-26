
import re

def isnumber(s):
     print(s+' isdigit: ',s.isdigit())
     print(s+' isdecimal: ',s.isdecimal())
     print(s+' isnumeric: ',s.isnumeric())
     
if __name__ =='__main__':
    str = ' 686a'
    res14 = re.search("[0-9]{3}",str)
    print(res14)
    if res14:
        print(res14.group()) #<_sre.SRE_Match object; span=(3, 7), match='HKJU'>
    
    
    str = 'aa boolean23'
    res14 = re.search("boolean[0-9]{1,3}",str)
    print(res14)
    if res14:
        print(res14.group()) #<_sre.SRE_Match object; span=(3, 7), match='HKJU'>
    
    str = 'AF'
    res14 = re.search("[A-Z]{1}",str)
    print(res14)
    if res14:
        print(res14.group()) #<_sre.SRE_Match object; span=(3, 7), match='HKJU'>
    
