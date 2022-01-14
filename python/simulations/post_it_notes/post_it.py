'''
Post-it simulations: An Experiment by Ziqing Ye
Background: post-it notes are designed in an Nx2 matrix: N rows of stickers,
each row consisted of two different colors, one on each side. In each row,
only one color will be flipped up for pulling while the other was hidden below,
and the available color alternates. Once you pull out a sheet of color A, 
a sheet of color B will pop up, etc.
Goal: Try to use the colors as evenly as possible
...
Basic rules:
1. Each row contains exactly two piles.
2. In each and every row, there is exactly one pullable (P) pile and exactly one
unpullable (x) pile (cannot be the same pile).
3. only piles marked "P" are can be pulled from. After one pull, the pile's remaining
sheet count decrements by 1, and that pile's status became "x" (unpullable). On the
other hand, the opposite pile in the same row become "P" (pullable).
4. When a post-it packet is first created, every pile has the same number of sheets,
and the pullable ("P") tabs are all on the same (say left) side.
As long as those base rules are obeyed, we can create arbitrary post-it notes with
arbitrary (even) number of colors and sheet counts.
'''

import numpy as np
import random

class PostIt:
    def __init__(self, num_colors, sheets_per_pile):
        "num_colors should be even, both params should be integers"
        self.rows = int(num_colors / 2)
        self.sheets = int(sheets_per_pile)
        #to save space, just use two 2D arrays instead of nested classes
        self.counts = np.full((self.rows, 2), self.sheets, dtype=int)
        self.status = np.zeros((self.rows, 2)) #0 for unpullable, 1 for pullable
        self.status[:,0] = 1 #for a new pack, all the left sides are up
        self.numup = [self.rows, 0] #number of up piles in each column, left col first up
        self.exhausted = False

    def __str__(self):
        return np.array2string(self.status)

    def draw(self, row):
        "draws from the currently pullable pile in the designated row"
        #omit col parameter b/c only one choice, had to pull the "up" tab in each row
        if (self.exhausted == True):
            print("Pack already reached terminal state")
            return
        rowid = int(row - 1) #row index
        colid = int(1 - self.status[rowid][0]) #if left col's status is 1, then colid = 0, vice versa
        assert(rowid < self.rows) #unnecessary sanity checks
        assert(colid < 2)
        assert(self.status[rowid][colid] == 1)
        self.counts[rowid][colid] -= 1 #decrement count
        if (self.counts[rowid][colid] == 0):
            self.status[rowid][colid] == -1 #-1 when no more left
            self.check_terminal(rowid, colid)
        self.status[rowid][colid]= 1 - self.status[rowid][colid] #change statuses
        self.status[rowid][int(1-colid)]= 1 - self.status[rowid][int(1-colid)]
        self.numup[colid] -= 1 #change numup count in each column
        self.numup[int(1-colid)] += 1
        #print(self) #print results


    def check_terminal(self, rowid, colid):
        "checks whether all other elements are smaller than or equal to 1"
        assert(self.counts[rowid][colid] == 0)
        self.exhausted = True #the main point of this simulation is to see whether evenly pulled
        #so we consider it game over when one of them is exhausted (since no point in further pulls)
        result = np.all((self.counts>=0) == (self.counts<=1)) #true if "even" scenario
        if (result == True):
            print("you win")
        else:
            print("You lose")
        print(self.counts)

    def pull_on_first_row(self):
        while (self.exhausted == False):
            self.draw(1)

    def pull_randomly(self):
        while (self.exhausted == False):
            self.draw(random.randint(0, int(self.rows-1)))

    def reset(self):
        self.counts = np.full((self.rows, 2), self.sheets, dtype=int)
        self.status = np.zeros((self.rows, 2)) #0 for unpullable, 1 for pullable
        self.status[:,0] = 1 #for a new pack, all the left sides are up
        self.numup = [self.rows, 0] #number of up piles in each column, left col first up
        self.exhausted = False

    def peek_thickness(self):
        print(self.counts)
