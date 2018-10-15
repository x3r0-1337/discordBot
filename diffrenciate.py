"""
Takes a polynomial and point as an inpt and gives out te derivative at tat point
"""
import re
class diffrenciate:
    def __init__(self,polynomial,point):
        self.equation=polynomial
        self.point=point

        def differentiate(self,self.equation,self.point):
            pattern2=re.compile(r"([+-])?(\d+)?x(\^)?(\d+)?")
            match2=pattern2.finditer(self.equation)
            s=0
            for x in match2:
                if x.group(1)=="+" or x.group(1)==None:
                    if x.group(2)!=None and x.group(4)!=None:
                        s+=int(x.group(2))*(int(x.group(4)))*(self.point**(int(x.group(4))-1))
                    elif x.group(2)==None and x.group(4)!=None:
                        s+=(self.point**(int(x.group(4))-1))*(int(x.group(4)))
                    elif x.group(2)!=None and x.group(4)==None:
                        s+=int(x.group(2))
                    elif x.group(2)==None and x.group(4)==None:
                        s+=1
                elif x.group(1)=="-":
                    if x.group(2)!=None and x.group(4)!=None:
                        s-=int(x.group(2))*(int(x.group(4)))*(self.point**(int(x.group(4))-1))
                    elif x.group(2)==None and x.group(4)!=None:
                        s-=self.point**(int(x.group(4))-1)*(int(x.group(4)))
                    elif x.group(2)!=None and x.group(4)==None:
                        s-=int(x.group(2))
                    elif x.group(2)==None and x.group(4)==None:
                        s-=1
