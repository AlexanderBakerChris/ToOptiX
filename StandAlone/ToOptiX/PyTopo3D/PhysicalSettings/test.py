from ElementNodes import *

n1 = Node()
n1.x = 10
n1.y = 20
n2 = Node()
n3 = Node()

#e = Element(__elementID=1, __nodeList=[n1, n2, n3], __elementType="Hexa", __elementOrder = 1)
p1 = TetElement()
p1.nodeList = [n1,n2,n3]
a = p1.nodeList[0]
print a.x
print p1.nodeList
