#! /usr/bin/env python
from __future__ import with_statement
from math import sqrt
import csv
import argparse

#
# Class representing a sudoku grid
#

class Sudoku:
    def __init__(self, n_row = 9, n_col = 9, values = []):
        """Initialize an n x m (9x9) sudoku grid."""
        self.n_row = n_row
        self.n_col = n_col
        self.rank = int(sqrt(n_col))
        self.values = values

    def __str__(self):
        """Print representation of the sudoku"""
        print_sud = []

        for row in range(self.n_row):
            # Header bar
            print_sud.append("\t" + "-"*2*self.n_col + "-\n")
            
            print_sud.append("\t")

            for col in range(self.n_col):
                val = self.values[row*self.n_col + col]
                print_sud.append("|{}".format(val))

            print_sud.append("|\n")

         # Footer bar
        print_sud.append("\t" + "-"*2*self.n_col + "-")

        # Combine all the pieces into one pretty presentation
        return "".join(print_sud)

    def fetch_row(self,ind):
        """Get all elements in a specified row"""

        start = ind * self.n_col
        return self.values[start : start + self.n_col]

    def fetch_rows(self):
        """Generator to get all puzzle rows"""

        for i in range(self.n_row):
            yield self.fetch_row(i)

    def fetch_col(self,ind):
        """Get all elements in a specified column"""

        col = []
        for i in range(self.n_row):
            col.append(self.values[i * self.n_col + ind])
        return col

    def fetch_cols(self):
        """Generator to get all puzzle columns"""

        for i in range(self.n_col):
            yield self.fetch_col(i)

    def fetch_block(self,ind):
        """Get all elements in a specified block"""

        # Counting by row starting from the top left
        # calculate the block location within the overall puzzle
        base_row = ind // self.rank * self.rank
        base_col = ind % self.rank * self.rank

        block = []
        for i in range(self.rank):
            for j in range(self.rank):
                row_ind = i+base_row
                col_ind = j+base_col
                block.append(self.values[row_ind * self.n_col + col_ind])
        return block

    def fetch_blocks(self):
        """Generator to get all puzzle blocks"""

        for i in range(self.n_col):
            yield self.fetch_block(i)

    def check_properties(self):
        """Verify that the complete grid has all the properties of a sudoku"""

        # Base case: there are still zeros
        if 0 in self.values:
            return False

        # The valid digits are 1:n_col+1
        valid_set = set(range(1,self.n_col+1))
        
        # Check all rows, cols, and blocks
        row_status = all([valid_set == set(row) for row in self.fetch_rows()])
        col_status = all([valid_set == set(col) for col in self.fetch_cols()])
        block_status = all([valid_set == set(block) for block in self.fetch_blocks()])

        # There have to be no conflicts for the puzzle to be considered solved
        return all(row_status,col_status,block_status)


    def solve_backtrack(self):
        """Solve the sudoku using the backtracking method"""

        # Base case: the puzzle is already solved
        if 0 not in self.values:
            print("The puzzle is already solved.")
            return False

        return True

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
    # Assume that everything that's not a digit is a missing value
    values = [int(val) if val.isdigit() else 0 for row in inp_vals for val in row]
    return Sudoku(n_row,n_col,values)

def write_output_file(sudoku,file_name):
    """Save the CSV representation of a sudoku grid"""

    sol_name = "solution_"+file_name
    try:
        with open(sol_name,'wb') as sud_out:
            sud = csv.writer(sud_out,lineterminator="\n")
            for row in range(sudoku.n_row):
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
    args = arg_parser.parse_args()

    # Instantiate the sudoku
    sudoku = parse_input_file(args.filename)
    if not sudoku:
        print("Please try again.")
        return

    print("The initial configuration of the puzzle:")
    print(sudoku)

    # Run the solver to find the solution
    #result = sudoku.solve_backtrack()

    # Verify the solution and write it to file
    valid_solution = sudoku.check_properties()
    if not valid_solution:
        print("The solver failed to find an optimal solution.")

    else:
        write_output_file(sudoku,args.filename)
        print("The final configuration of the puzzle:")
        print(sudoku)
        

if __name__ == "__main__":
    main()