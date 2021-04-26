# drag.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D


class DraggablePoint:

    # http://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively

    lock = None #  only one can be animated at a time

    def __init__(self, parent, body_part, x=0.1, y=0.1, size=0.1):

        self.parent = parent
        self.point = patches.Ellipse((x, y), size, size, fc='r', alpha=0.5, edgecolor='r') if body_part != 'head' else patches.Ellipse((x, y), 2*size, 2*size, fc='r', alpha=0.5, edgecolor='r')
        self.x = x
        self.y = y
        parent.fig.axes[0].add_patch(self.point)
        self.press = None
        self.background = None
        self.body_part = body_part
        self.connect()
        
        # if another point already exist we draw a line
        if self.parent.list_points[body_part]:
            line_x = [self.parent.list_points[body_part][-1].x, self.x]
            line_y = [self.parent.list_points[body_part][-1].y, self.y]

            self.line = Line2D(line_x, line_y, color='r', alpha=0.5)
            parent.fig.axes[0].add_line(self.line)

        elif self.body_part == 'head':
            self.line = Line2D([0,0], [0,0], color='r', alpha=0.5)
            parent.fig.axes[0].add_line(self.line)


    def connect(self):

        'connect to all the events we need'

        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)


    def on_press(self, event):

        if event.inaxes != self.point.axes: return
        if DraggablePoint.lock is not None: return
        contains, attrd = self.point.contains(event)
        if not contains: return
        self.press = (self.point.center), event.xdata, event.ydata
        DraggablePoint.lock = self

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.point.figure.canvas
        axes = self.point.axes
        self.point.set_animated(True)
        
        # TODO also the line of some other points needs to be released
        point_number =  self.parent.list_points[self.body_part].index(self)

        if self.body_part == 'head':
            self.line.set_animated(True)
        
        elif self == self.parent.list_points[self.body_part][0]:
            self.parent.list_points[self.body_part][1].line.set_animated(True)            
        elif self == self.parent.list_points[self.body_part][-1]:
            self.line.set_animated(True)            
        else:
            self.line.set_animated(True)            
            self.parent.list_points[self.body_part][point_number+1].line.set_animated(True)                
            
            
            
        
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.point.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self.point)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)


    def on_motion(self, event):

        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.point.axes: return
        self.point.center, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.point.center = (self.point.center[0]+dx, self.point.center[1]+dy)

        canvas = self.point.figure.canvas
        axes = self.point.axes

        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self.point)
        
        point_number =  self.parent.list_points[self.body_part].index(self)
        self.x = self.point.center[0]
        self.y = self.point.center[1]
        

        if self.body_part == 'head':
            axes.draw_artist(self.line)    
        
        # We check if the point is A or B        
        elif self == self.parent.list_points[self.body_part][0]:
            # or we draw the other line of the point
            self.parent.list_points[self.body_part][1].line.set_animated(True)
            axes.draw_artist(self.parent.list_points[self.body_part][1].line)
        
        elif self == self.parent.list_points[self.body_part][-1]:
            # we draw the line of the point            
            axes.draw_artist(self.line)    

        else:
            # we draw the line of the point
            axes.draw_artist(self.line)
            #self.parent.list_points[self.body_part][point_number+1].line.set_animated(True)
            axes.draw_artist(self.parent.list_points[self.body_part][point_number+1].line)
            
        
        if self.body_part == 'head':
            print('moved head')
        elif self == self.parent.list_points[self.body_part][0]:
            # The first point is especial because it has no line
            line_x = [self.x, self.parent.list_points[self.body_part][1].x]
            line_y = [self.y, self.parent.list_points[self.body_part][1].y]      
            # this is were the line is updated
            self.parent.list_points[self.body_part][1].line.set_data(line_x, line_y)
            
        elif self == self.parent.list_points[self.body_part][-1]:
            line_x = [self.parent.list_points[self.body_part][-2].x, self.x]
            line_y = [self.parent.list_points[self.body_part][-2].y, self.y]
            self.line.set_data(line_x, line_y)        
        else:
            # The first point is especial because it has no line
            line_x = [self.x, self.parent.list_points[self.body_part][point_number+1].x]
            line_y = [self.y, self.parent.list_points[self.body_part][point_number+1].y]      
            # this is were the line is updated
            self.parent.list_points[self.body_part][point_number+1].line.set_data(line_x, line_y)
            
            line_x = [self.parent.list_points[self.body_part][point_number-1].x, self.x]
            line_y = [self.parent.list_points[self.body_part][point_number-1].y, self.y]
            self.line.set_data(line_x, line_y)        

        # blit just the redrawn area
        canvas.blit(axes.bbox)


    def on_release(self, event):

        'on release we reset the press data'
        if DraggablePoint.lock is not self:
            return

        self.press = None
        DraggablePoint.lock = None

        # turn off the rect animation property and reset the background
        self.point.set_animated(False)
        
        point_number =  self.parent.list_points[self.body_part].index(self)

        if self.body_part == 'head':
            self.line.set_animated(False) 

        elif self == self.parent.list_points[self.body_part][0]:
            self.parent.list_points[self.body_part][1].line.set_animated(False)            
        elif self == self.parent.list_points[self.body_part][-1]:
            self.line.set_animated(False)            
        else:
            self.line.set_animated(False)            
            self.parent.list_points[self.body_part][point_number+1].line.set_animated(False)       
            

        self.background = None

        # redraw the full figure
        self.point.figure.canvas.draw()

        self.x = self.point.center[0]
        self.y = self.point.center[1]

    def disconnect(self):

        'disconnect all the stored connection ids'

        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)
