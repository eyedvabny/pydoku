#! /usr/bin/env python
from __future__ import with_statement
from math import sqrt
import csv
import argparse

class Sudoku:
    def __init__(self, n_row = 9, n_col = 9, values = []):
        """Initialize an n x m (9x9) sudoku grid."""
        self.n_row = n_row
        self.n_col = n_col
        self.values = values

    def __str__(self):
        """Print representation of the sudoku"""
        print_sud = []

        for row in range(self.n_row):
            # Header bar
            print_sud.append("\t" + "-"*2*self.n_col + "-\n")
            
            print_sud.append("\t")
            for col in range(self.n_col):
                val = self.values[row*self.n_row + col]
                print_sud.append("|{}".format(val))
            print_sud.append("|\n")

         # Footer bar
        print_sud.append("\t" + "-"*2*self.n_col + "-")

        return "".join(print_sud)

    def get_value(self,row,col):
        """Return the element at specified location."""
        return self.values[row*self.n_row + col]

def parse_input_file(file_name):
    """Read in the CSV with ASCII sudoku."""
    inp_vals = []
    try:
        with open(file_name,'r') as sud_inp:
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
    if(n_row < 2 or n_row != n_col or not sqrt(n_row).is_integer()):
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
        with open(sol_name,'w') as sud_out:
            sud = csv.writer(sud_out)
            for row in range(sudoku.n_row):
                row_vals = sudoku.values[row*sudoku.n_row : row*sudoku.n_row + sudoku.n_col]
                sud.writerow(row_vals)

    except IOError:
        print("Error: unable to save the puzzle solution.")

def main():

    # Parse the argument for the solver
    arg_parser = argparse.ArgumentParser(
                    description="PyDoku: python sudoku solver")
    arg_parser.add_argument("filename", help="input 9x9 CSV with 0 for missing values")
    args = arg_parser.parse_args()

    # Instantiate the sudoku
    sudoku = parse_input_file(args.filename)
    if(not sudoku):
        print("Please try again.")
        return

    print("The initial configuration of the puzzle:")
    print(sudoku)

    write_output_file(sudoku,args.filename)

if __name__ == "__main__":
    main()