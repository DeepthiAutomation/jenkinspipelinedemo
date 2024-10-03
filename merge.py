import pandas as pd
from openpyxl import load_workbook

# Function to handle merged cells and take only the first word from the second column
def unmerge_and_fill(excel_file, sheet_name):
    # Load the workbook and the specific sheet
    wb = load_workbook(excel_file)
    ws = wb[sheet_name]
    
    # Copy the merged cells ranges to a list (to avoid set size change issue)
    merged_cells_ranges = list(ws.merged_cells.ranges)
    
    # Iterate through the copied list of merged cell ranges
    for merged_cell in merged_cells_ranges:
        # Unmerge each cell
        ws.unmerge_cells(str(merged_cell))
        
        # Get the top-left cell value of the merged range
        top_left_cell_value = ws.cell(row=merged_cell.min_row, column=merged_cell.min_col).value
        
        # Fill the unmerged cells with the top-left cell value
        for row in ws.iter_rows(min_row=merged_cell.min_row, max_row=merged_cell.max_row,
                                min_col=merged_cell.min_col, max_col=merged_cell.max_col):
            for cell in row:
                cell.value = top_left_cell_value
    
    # Save the modified workbook after unmerging
