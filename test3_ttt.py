import area
import ttt
import myvtk
import math
import vtk

# rotate by cos/sin. from emc2 gcodemodule.cc
def rotate(x, y,  c,  s):
    tx = x * c - y * s;
    y = x * s + y * c;
    x = tx;
    return [x,y]

# return a list of points corresponding to an arc
def arc_pts(  pt1, pt2, r, cen,cw): # (start, end, radius, center, cw )
    # draw arc as many line-segments
    #start = pt1-cen
    #end = pt2-cen
    theta1 = math.atan2( pt1[0]-cen[0], pt1[1]-cen[1])
    theta2 = math.atan2( pt2[0]-cen[0], pt2[1]-cen[1])
    alfa=[] # the list of angles
    #da=0.1
    CIRCLE_FUZZ = 1e-9
    # idea from emc2 / cutsim g-code interp G2/G3
    if (cw == False ): 
        while ( (theta2 - theta1) > -CIRCLE_FUZZ): 
            theta2 -= 2*math.pi
    else:
        while( (theta2 - theta1) < CIRCLE_FUZZ): 
            theta2 += 2*math.pi
    
    dtheta = theta2-theta1
    arclength = r*dtheta
    dlength =  arclength/10 # draw as 10 segments
    
    steps = int( float(arclength) / float(dlength))
    rsteps = float(1)/float(steps)
    dc = math.cos(-dtheta*rsteps) # delta-cos  
    ds = math.sin(-dtheta*rsteps) # delta-sin
    
    previous = pt1
    tr = [pt1[0]-cen[0], pt1[1]-cen[1]]
    pts=[]
    for i in range(steps):
        #f = (i+1) * rsteps #; // varies from 1/rsteps..1 (?)
        #theta = theta1 + i* dtheta
        tr = rotate(tr[0], tr[1], dc, ds) #; // rotate center-start vector by a small amount
        x = cen[0] + tr[0] 
        y = cen[1] + tr[1] 
        
        current = [ x, y ] #ovd.Point(x,y)
        pts.extend( [previous, current] )
        previous = current 
    return pts

# draw offset loops    
def drawOffsets2(myscreen, ofs):
    # draw loops
    nloop = 0
    lineColor = myvtk.lgreen
    arcColor = myvtk.green #grass
    ofs_points=[]
    for lop in ofs:
        points=[]
        n = 0
        N = len(lop)
        first_point=[]
        previous=[]
        for p in lop:
            # p[0] is the Point
            # p[1] is -1 for lines, and r for arcs
            # p[2] is center,  for arcs
            # p[3] is cw/ccw flag, for arcs
            if n==0: # don't draw anything on the first iteration
                previous=p[0]
            else:
                cw=p[3]
                cen=p[2]
                r=p[1]
                pt=p[0]
                if r==-1: # r=-1 means line-segment
                    points.extend( [previous,pt] )
                else: # otherwise we have an arc
                    points.extend( arc_pts( previous, pt, r,cen,cw) )
                previous=pt
            n=n+1
        ofs_points.append(points)
        #print "rendered loop ",nloop, " with ", len(lop), " points"
        nloop = nloop+1
        
    # now draw each loop with polydata
    oPoints = vtk.vtkPoints()
    lineCells=vtk.vtkCellArray()
    #self.colorLUT = vtk.vtkLookupTable()
    print len(ofs_points)," loops to render:"
    idx = 0
    last_idx = 0
        
    for of in ofs_points:
        epts  = of 
        segs=[]
        first = 1
        print " loop with ", len(epts)," points"
        for p in epts:
            oPoints.InsertNextPoint( p[0], p[1], 0)
            if first==0:
                seg = [last_idx,idx]
                segs.append(seg)
            first = 0
            last_idx = idx
            idx = idx + 1
            
        # create line and cells
        for seg in segs:
            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, seg[0])
            line.GetPointIds().SetId(1, seg[1])
            #print " indexes: ", seg[0]," to ",seg[1]
            lineCells.InsertNextCell(line)
    
    linePolyData = vtk.vtkPolyData()
    linePolyData.SetPoints(oPoints)
    linePolyData.SetLines(lineCells)
    linePolyData.Modified() 
    linePolyData.Update()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInput(linePolyData)
    edge_actor = vtk.vtkActor()
    edge_actor.SetMapper(mapper)
    edge_actor.GetProperty().SetColor( myvtk.lgreen)
    myscreen.addActor( edge_actor )

def ttt_segments():
    wr = ttt.SEG_Writer()
    wr.scale=1
    wr.arc = False
    wr.conic = False
    wr.cubic = False
    s3 = ttt.ttt("T",wr)
    segs = wr.get_segments()
    #segs.reverse()
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

def drawLoops(myscreen,loops,loopColor):
    # draw the loops
    nloop = 0
    for lop in loops:
        n = 0
        N = len(lop)
        first_point=[]
        previous=[]
        for p in lop:
            if n==0: # don't draw anything on the first iteration
                previous=p 
                first_point = p
            elif n== (N-1): # the last point
                myscreen.addActor( myvtk.Line(p1=(previous[0],previous[1],0),p2=(p[0],p[1],0),color=loopColor) ) # the normal line
                # and a line from p to the first point
                myscreen.addActor( myvtk.Line(p1=(p[0],p[1],0),p2=(first_point[0],first_point[1],0),color=loopColor) )
            else:
                myscreen.addActor( myvtk.Line(p1=(previous[0],previous[1],0),p2=(p[0],p[1],0),color=loopColor) )
                previous=p
            n=n+1
        print "rendered loop ",nloop, " with ", len(lop), " points"
        nloop = nloop+1
        
if __name__ == "__main__":  
    segs = ttt_segments() # get segments from ttt
    a = area.Area()
    a = segments_to_area(segs,a)    # insert segments into area

    a.Offset(-200) # produce an offset

    print "offset has ", len(a.getCurves())," polylines"
    for cr in a.getCurves():
        print "polyline has ",len(cr.getVertices())," verices"
        for v in cr.getVertices():
            print "t=",v.type,
            print "p = ",v.p.x ," ", v.p.y,
            print "c = ",v.c.x ," ", v.c.y
    w=1024
    h=1024
    myscreen = myvtk.VTKScreen(width=w, height=h) 
    scale=1
    far = 10000
    camPos = far
    zmult = 3
    myscreen.camera.SetPosition(0, -camPos/float(1000), zmult*camPos) 
    myscreen.camera.SetClippingRange(-(zmult+1)*camPos,(zmult+1)*camPos)
    myscreen.camera.SetFocalPoint(0.0, 0, 0)
    
    # draw the geometry from ttt
    drawLoops(myscreen, segs, myvtk.yellow)
    
    # create openvoronoi-style offset list
    # p[0] is the Point
    # p[1] is -1 for lines, and r for arcs
    # p[2] is center,  for arcs
    # p[3] is cw/ccw flag, for arcs
    loops = []
    for cr in a.getCurves():
        print "polyline has ",len(cr.getVertices())," verices"
        loop = []
        for v in cr.getVertices():
            print "t=",v.type,
            print "p = ",v.p.x ," ", v.p.y,
            print "c = ",v.c.x ," ", v.c.y
            if v.type == 0: 
                p = [v.p.x, v.p.y] # line-segment
                pt = [p, -1, [0,0], False]
                loop.append(pt)
            elif v.type == -1 or v.type == +1:
                p = [v.p.x, v.p.y]
                c = [v.c.x, v.c.y]
                r = math.sqrt( (v.p.x-v.c.x)*(v.p.x-v.c.x) + (v.p.y-v.c.y)*(v.p.y-v.c.y) )
                cw = False
                if v.type == -1:
                    cw = False
                else:
                    cw = True
                pt = [p, r, c, cw]
                loop.append(pt)
                #pass
        loops.append(loop)

    # draw the offset produced by libarea
    drawOffsets2(myscreen, loops)
    
    
    print "PYTHON All DONE."
    myscreen.render()   
    myscreen.iren.Start()
