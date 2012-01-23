import area

p1 = area.Point(0,0)
p2 = area.Point(100,0)
p3 = area.Point(100,100)
p4 = area.Point(0,100)

# type: 0=line,1=ccw arc,-1=cw arc,
typ = 0
v1 = area.Vertex(typ,p1,p2,0)
v2 = area.Vertex(typ,p2,p3,0)
v3 = area.Vertex(typ,p3,p4,0)
v4 = area.Vertex(typ,p4,p1,0)

c = area.Curve()
c.append(v1)
c.append(v2)
c.append(v3)
c.append(v4)

#for vertex in c.getVertices():
#    print vertex

a = area.Area()
a.append(c)
#area.print_area(a)
a2 = a.Offset(-4.2)
#area.print_area(a)
#print a.getCurves()
#print a2
for cr in a.getCurves():
    #print cr
    for v in cr.getVertices():
        print "t=",v.type,
        print "p = ",v.p.x ," ", v.p.y,
        print "c = ",v.c.x ," ", v.c.y
        #print v.x," ",v.y
        #dir(v)
        #print v.p
        #print v.q
