from tkinter import Tk, BOTH, Canvas
from time import sleep
import random

class Window:
    
    def __init__(self,width,height):
        self.width = width
        self.height = height
        #create a root widget using Tk() and save it as a data member
        self.root = Tk()
        self.root.geometry(f"{self.width}x{self.height}")
        #set widget.title to something
        self.root.title("Maze Maker")
        #attach window "x" to close method
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        #create a Canvas and save it as a data member
        self.background = Canvas(self.root,width = self.width,height = self.height)
        #Pack the canvas to be drawn
        self.background.pack()

    #create a bool that represents the window running = False
    is_window_running = False

    def redraw(self):
        self.root.update_idletasks()
        self.root.update()

    def wait_for_close(self):
        print("running")
        self.is_window_running = True
        while self.is_window_running:
            self.redraw()
    
    def close(self):
        self.is_window_running = False
        self.root.quit()
        self.root.destroy()
        print("Shutting Down")

    def draw_line(self, line, fill_color):
        line.draw(self.background,fill_color)

class Point:
    def __init__(self,x,y):
        self.x = x
        self.y = y

class Line:
    def __init__(self,point_a, point_b):
        self.a = point_a
        self.b = point_b

    def draw(self,canvas,fill_color):
        canvas.create_line(self.a.x,self.a.y,self.b.x,self.b.y, fill = fill_color, width = 2)
        canvas.pack()

class Cell:
    def __init__(self, top_left, bottom_right, window = None):
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self._top_left = top_left
        self._bottom_right = bottom_right
        self._win = window
        self.visited = False

    def draw(self):
        #my badckground appears to be gray85. There's probably a way to pull that info in case that's not a static default
        if self.has_left_wall:
            self._win.draw_line(Line(self._top_left,Point(self._top_left.x,self._bottom_right.y)),"black")
        else:
            self._win.draw_line(Line(self._top_left,Point(self._top_left.x,self._bottom_right.y)),"gray85")
        if self.has_right_wall:
            self._win.draw_line(Line(Point(self._bottom_right.x,self._top_left.y),self._bottom_right),"black")
        else:
            self._win.draw_line(Line(Point(self._bottom_right.x,self._top_left.y),self._bottom_right),"gray85")
        if self.has_top_wall:
            self._win.draw_line(Line(self._top_left,Point(self._bottom_right.x,self._top_left.y)),"black")
        else:
            self._win.draw_line(Line(self._top_left,Point(self._bottom_right.x,self._top_left.y)),"gray85")
        if self.has_bottom_wall:
            self._win.draw_line(Line(Point(self._top_left.x,self._bottom_right.y), self._bottom_right),"black")
        else:
            self._win.draw_line(Line(Point(self._top_left.x,self._bottom_right.y), self._bottom_right),"gray85")

    def draw_move(self, to_cell, undo = False):
        start_point = Point((self._bottom_right.x + self._top_left.x)//2,(self._bottom_right.y + self._top_left.y)//2)
        end_point = Point((to_cell._bottom_right.x + to_cell._top_left.x)//2,(to_cell._bottom_right.y + to_cell._top_left.y)//2)
        whole_line = Line(start_point,end_point)
        if undo:
            self._win.draw_line(whole_line,"gray")
        else:
            self._win.draw_line(whole_line,"red")

class Maze:
    def __init__(self, num_rows, num_cols, cell_size, window, seed = None, upper_left = Point(10,10)):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size = cell_size
        self._win = window
        self.upper_left = upper_left
        self._seed = random.seed(seed)
        self._create_cells()

    def _create_cells(self):
        self._cells = []
        for i in range(0,self.num_cols):
            self._cells.append([])
            for j in range(0,self.num_rows):
                current_upper = Point(self.upper_left.x + i*self.cell_size,self.upper_left.y + j*self.cell_size)
                current_lower = Point(current_upper.x + self.cell_size,current_upper.y + self.cell_size)
                self._cells[i].append(Cell(current_upper,current_lower,self._win))
                #self._cells[i].append(Cell(current_upper,current_lower))
        
        self._break_entrance_and_exit()

        for list in self._cells:
            for cell in list:
                cell.draw()
                self._animate()

        self._break_walls_r(0,0)
        self._reset_cells_visited()

    def _break_walls_r(self, i, j):
        self._cells[i][j].visited = True

        while True:
            unvisited_neighbors = []
            num_u_n = 0

            #is left available:
            if i > 0 and not self._cells[i-1][j].visited:
                unvisited_neighbors.append([i-1,j])
                num_u_n += 1
            #is right available:
            if i < self.num_cols - 1 and not self._cells[i+1][j].visited:
                unvisited_neighbors.append([i+1,j])
                num_u_n += 1
            #is up available:
            if j > 0 and not self._cells[i][j-1].visited:
                unvisited_neighbors.append([i,j-1])
                num_u_n += 1
            #is down available:
            if j < self.num_rows - 1 and not self._cells[i][j+1].visited:
                unvisited_neighbors.append([i,j+1])
                num_u_n += 1

            if num_u_n < 1:
                self._cells[i][j].draw()
                self._animate()
                return
            
            moving_to = unvisited_neighbors[random.randrange(num_u_n)]

            #left
            if moving_to[0] < i:
                self._cells[i][j].has_left_wall = False
                self._cells[i-1][j].has_right_wall = False
            #right
            if moving_to[0] > i:
                self._cells[i][j].has_right_wall = False
                self._cells[i+1][j].has_left_wall = False
            #top
            if moving_to[1] < j:
                self._cells[i][j].has_top_wall = False
                self._cells[i][j-1].has_bottom_wall = False
            #bottom
            if moving_to[1] > j:
                self._cells[i][j].has_bottom_wall = False
                self._cells[i][j+1].has_top_wall = False

            self._break_walls_r(moving_to[0],moving_to[1])

    def _reset_cells_visited(self):
        for list in self._cells:
            for cell in list:
                cell.visited = False

    def _animate(self):
        self._win.redraw()
        sleep(.05)

    def _break_entrance_and_exit(self):
        entrance = self._cells[0][0]
        exit = self._cells[len(self._cells)-1][len(self._cells[0])-1]
        entrance.has_top_wall = False
        exit.has_bottom_wall = False

    def solve(self):
        return self._solve_r(0,0)

    def _solve_r(self,i, j):
        self._animate()
        self._cells[i][j].visited = True

        if i == self.num_cols - 1 and j == self.num_rows - 1:
            return True
        
        #is left available:
        if i > 0 and not self._cells[i][j].has_left_wall and not self._cells[i-1][j].visited:
            self._cells[i][j].draw_move(self._cells[i-1][j])
            if self._solve_r(i-1,j):
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i-1][j], True)
        #is right available:
        if i < self.num_cols - 1 and not self._cells[i][j].has_right_wall and not self._cells[i+1][j].visited:
            self._cells[i][j].draw_move(self._cells[i+1][j])
            if self._solve_r(i+1,j):
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i+1][j], True)
        #is up available:
        if j > 0 and not self._cells[i][j].has_top_wall and not self._cells[i][j-1].visited:
            self._cells[i][j].draw_move(self._cells[i][j-1])
            if self._solve_r(i,j-1):
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i][j-1], True)
        #is down available:
        if j < self.num_rows - 1 and not self._cells[i][j].has_bottom_wall and not self._cells[i][j+1].visited:
            self._cells[i][j].draw_move(self._cells[i][j+1])
            if self._solve_r(i,j+1):
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i][j+1], True)

        return False

def main():
    my_window = Window(1600,1200)

    my_cells = Maze(3,3,200,my_window)

    my_cells.solve()

    my_cells = Maze(11,15,100,my_window)

    my_cells.solve()

    my_window.wait_for_close()

main()