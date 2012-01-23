import area
import ttt

def ttt_segments():
    wr = ttt.SEG_Writer()
    wr.scale=1
    wr.arc = False
    wr.conic = False
    wr.cubic = False
    s3 = ttt.ttt("LT",wr)
    segs = wr.get_segments()
    return segs

def segments_to_area(segs,a):
    polylines = []
    print "segs has ",len(segs), " polylines "
    for pts in segs:
        print len(pts)," points in polyline"
        polyline=[]
        for pt in pts:
            polyline.append( area.Point( pt[0], pt[1] ) )
        polylines.append(polyline)

    curves = []
    for poly in polylines:
        c = area.Curve()
        for n in range(len(poly)):
            if n==0:
                previous = len(poly)-1
            else:
                previous = n-1
            v = area.Vertex(0, poly[previous], poly[n], 0)
            c.append(v)
        curves.append(c)
    for c in curves:
        a.append(c)
    return a

if __name__ == "__main__":  
    segs = ttt_segments()
    a = area.Area()
    a = segments_to_area(segs,a)    

    a.Offset(-1)

    print "offset has ", len(a.getCurves())," polylines"
    for cr in a.getCurves():
        print "polyline has ",len(cr.getVertices())," verices"
        for v in cr.getVertices():
            print "t=",v.type,
            print "p = ",v.p.x ," ", v.p.y,
            print "c = ",v.c.x ," ", v.c.y
