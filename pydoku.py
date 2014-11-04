#! /usr/bin/env python
from __future__ import with_statement
from math import sqrt
import csv
import argparse

#
# Class representing a sudoku grid
#

class Sudoku:
    def __init__(self, n_row = 9, n_col = 9):
        """Initialize an n x m (9x9) sudoku grid."""
        self.n_row = n_row
        self.n_col = n_col
        self.rank = int(sqrt(n_col))

        # Array of grid values
        self.values = [0 for i in xrange(n_row*n_col)]

        # Dict of possible values that a square can take
        self.choices = dict((ind,range(1,n_col+1)) for ind in xrange(n_row*n_col))

        # Dict of indices that are neighbors of
        self.peers = dict((ind,self.find_peers(ind)) for ind in xrange(n_row*n_col))

    def __str__(self):
        """Print representation of the sudoku."""
        print_sud = []

        for row in xrange(self.n_row):
            # Header bar
            print_sud.append("\t" + "-"*2*self.n_col + "-\n")
            
            print_sud.append("\t")

            for col in xrange(self.n_col):
                val = self.values[row*self.n_col + col]
                print_sud.append("|{}".format(val))

            print_sud.append("|\n")

         # Footer bar
        print_sud.append("\t" + "-"*2*self.n_col + "-")

        # Combine all the pieces into one pretty presentation
        return "".join(print_sud)

    def fetch_row(self,ind):
        """Get all elements in a specified row."""

        start = ind * self.n_col
        return self.values[start : start + self.n_col]

    def fetch_rows(self):
        """Generator to get all puzzle rows."""

        for i in xrange(self.n_row):
            yield self.fetch_row(i)

    def fetch_col(self,ind):
        """Get all elements in a specified column."""

        return [self.values[r*self.n_col + ind] for r in xrange(self.n_row)]

    def fetch_cols(self):
        """Generator to get all puzzle columns."""

        for i in xrange(self.n_col):
            yield self.fetch_col(i)

    def fetch_block(self,ind):
        """Get all elements in a specified block."""

        # Counting by row starting from the top left
        # calculate the block location within the overall puzzle
        base_row = ind // self.rank * self.rank
        base_col = ind % self.rank * self.rank

        block = []
        for i in xrange(self.rank):
            for j in xrange(self.rank):
                row_ind = i+base_row
                col_ind = j+base_col
                block.append(self.values[row_ind * self.n_col + col_ind])
        return block

    def fetch_blocks(self):
        """Generator to get all puzzle blocks."""

        for i in xrange(self.n_col):
            yield self.fetch_block(i)

    def check_properties(self):
        """Verify that the complete grid has all the properties of a sudoku."""

        # Base case: there are still zeros
        if 0 in self.values:
            return False

        # The valid digits are 1:n_col+1
        valid_set = set(range(1,self.n_col+1))
        
        # Check all rows, cols, and blocks
        row_status = all(valid_set == set(row) for row in self.fetch_rows())
        col_status = all(valid_set == set(col) for col in self.fetch_cols())
        block_status = all(valid_set == set(block) for block in self.fetch_blocks())

        # There have to be no conflicts for the puzzle to be considered solved
        return all([row_status,col_status,block_status])

    def assign_value(self,ind,val):
        """Assign a value to the grid specified by the index"""

        #print("Assigning {} to {}".format(val,ind))

        if len(self.choices[ind]) == 1 and self.choices[ind][0] == val:
            #print("Already assigned")
            return True

        # Make a copy of the choices and exclude the current value
        bad_vals = list(self.choices[ind])
        if val in bad_vals:
            bad_vals.remove(val)
        else:
            #Something is wrong if the value I am setting is not one of the choices
            return False 

        # Assigning a value means removing all but that value from choices
        if all(self.cull_choices(ind,bad_val) for bad_val in bad_vals):
            return True
        else:
            return False

    def update_grid_values(self):
        """Update the values list when choices are narrowed down to a single value"""
        for i in range(self.n_col*self.n_col):
            if len(self.choices[i]) == 1:
                self.values[i] = self.choices[i][0]

    def cull_choices(self,ind,val):
        """Remove val as one of the possible choices for grid[ind]"""

        #print("Removing {} from {}".format(val,ind))

        # Can't eliminate what's not there
        if val not in self.choices[ind]:
            return True

        # If we only have one possible choice already
        # removing it would lead to an inconsistency
        if len(self.choices[ind]) == 1:
            return False

        # Eliminate the option
        self.choices[ind].remove(val)

        # One choice left = eliminate it from the neighbors
        if len(self.choices[ind]) == 1:
            best_val = self.choices[ind][0]
            if not all(self.cull_choices(peer,best_val) for peer in self.peers[ind]):
                return False

        # Having eliminated val from _this_ ind perhaps now we can find a place for it
        # Look through the row, col and block to see if there is a spot
        peers = [self.find_row_peers(ind), self.find_col_peers(ind), self.find_block_peers(ind)]
        for peer in peers:
            spots = [spot for spot in peer if val in self.choices[spot]]

            # There should definitely be at least one spot in a peer group for the eliminated value
            if len(spots) == 0:
               return False

            # If there is only one spot for the eliminated value, plug it in
            elif len(spots)==1:
                #print("Just removed {} from {}".format(val,ind))
                #print("Found a spot for {} in {}".format(val,spots[0]))
                if not self.assign_value(spots[0],val):
                    return False

        # All constraints are propagated and holes filled
        return True

    # TODO: This is hideous logic and needs to be refactored

    def find_row_peers(self,ind):
        """Calculate a list of row peers"""

        row_ind = ind // self.n_col
        row_peers =  range(row_ind * self.n_col, (row_ind+1) * self.n_col)
        row_peers.remove(ind)
        return row_peers

    def find_col_peers(self,ind):
        """Calculate a list of column peers"""
        
        col_ind = ind % self.n_col
        col_peers = [r*self.n_col + col_ind for r in xrange(self.n_row)]
        col_peers.remove(ind)
        return col_peers

    def find_block_peers(self,ind):
        """Calculate a list of block peers"""

        block_ind = (ind // self.n_col // self.rank) * self.rank + (ind % self.n_col // self.rank)
        block_peers = []
        for i in xrange(self.rank):
            for j in xrange(self.rank):
                row_ind = i + block_ind // self.rank * self.rank
                col_ind = j + block_ind % self.rank * self.rank
                block_peers.append(row_ind * self.n_col + col_ind)
        block_peers.remove(ind)
        return block_peers

    def find_peers(self, ind):
        """Calculate a list of indices of the cells peering with the present index"""

        # Combine all peer indices into a set
        return set(self.find_col_peers(ind) + self.find_row_peers(ind) + self.find_block_peers(ind))


    def solve_backtrack(self):
        """Solve the sudoku using the backtracking method."""

        # Base case: the puzzle is already solved
        if 0 not in self.values:
            print("The provided puzzle has no missing slots.")
            return True

        # TODO: Finish the solver implementation
        return False

#
# Helper functions for reading and writing CSVs
#

def parse_input_file(file_name):
    """Read in the CSV with ASCII sudoku."""

    inp_vals = []
    try:
        with open(file_name,'rb') as sud_inp:
            sud = csv.reader(sud_inp,delimiter=",")
            for line in sud:
                inp_vals.append(line)

    except IOError:
        print("Error: the specified file doesn't exist.")
        return None

    # Set the dimensions
    n_row = len(inp_vals)
    n_col = len(inp_vals[1])

    # Sudokus have to be square and of dim N^2
    if(n_row < 4 or n_row != n_col or not sqrt(n_row).is_integer()):
        print("Error: incorrect format for a sudoku.")
        return None

    # Need to convert the strings into digits
    # Assume that everything that's not a valid digit is a missing value
    values = [int(val) if val.isdigit() and int(val) <= n_col else 0 for row in inp_vals for val in row]

    # Instantiate a puzzle to solve
    sudoku = Sudoku(n_row,n_col)

    # Assign the values
    for ind,val in enumerate(values):
        if val != 0:
            sudoku.values[ind] = val
            if not sudoku.assign_value(ind,val):
                print("Error: placement conflict in the provided configuration")
                return None

    return sudoku

def write_output_file(sudoku,file_name):
    """Save the CSV representation of a sudoku grid."""

    sol_name = "solution_"+file_name
    try:
        with open(sol_name,'wb') as sud_out:
            sud = csv.writer(sud_out,lineterminator="\n")
            for row in xrange(sudoku.n_row):
                start = row * sudoku.n_col
                row_vals = sudoku.values[start : start + sudoku.n_col]
                sud.writerow(row_vals)

    except IOError:
        print("Error: unable to save the puzzle solution.")

#
# Main: read in the input configuration and solve the sudoku
#

def main():

    # Parse the argument for the solver
    arg_parser = argparse.ArgumentParser(
                    description="PyDoku: python sudoku solver")
    
    arg_parser.add_argument("filename", help="input 9x9 CSV with 0 for missing values")

    arg_parser.add_argument("-v",help="Print out intermediate representations of the sudoku to stdout",
                            action="store_true",default=False)

    args = arg_parser.parse_args()

    # Say hello
    print("Thank you for using PuDoKu, a python sudoku solver.")

    # Instantiate the sudoku
    sudoku = parse_input_file(args.filename)
    if not sudoku:
        print("Could not instantiate a sudoku. Please try again.")
        return

    if(args.v):
        print("The initial configuration of the puzzle:")
        print(sudoku)

    # Update the display following intial constraint propagation
    sudoku.update_grid_values()

    # Check if the simple constraints already solved the puzzle
    # Run the solver to find the solution if needed
    if not sudoku.check_properties():
        sudoku.solve_backtrack()

    #print(sudoku)

    # If the solver has returned but the puzzle is not complete something wonky happened
    if not sudoku.check_properties():
        print("The solver failed to find an optimal solution.")
        print("Please try again with a simpler puzzle.")

    else:
        write_output_file(sudoku,args.filename)

        if(args.v):
            print("The final configuration of the puzzle:")
            print(sudoku)

        print("The solver has completed. Please find the solution in " + "solution_" + args.filename)
        
if __name__ == "__main__":
    main()
