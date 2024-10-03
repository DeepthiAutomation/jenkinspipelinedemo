import pandas as pd
from openpyxl import load_workbook

# Function to handle merged cells and only use the first row value
def unmerge_and_fill_first_row_only(excel_file, sheet_name):
    # Load the workbook and the specific sheet
    wb = load_workbook(excel_file)
    ws = wb[sheet_name]
    
    # Copy the merged cells ranges to a list (to avoid set size change issue)
    merged_cells_ranges = list(ws.merged_cells.ranges)
    
    # Iterate through the copied list of merged cell ranges
    for merged_cell in merged_cells_ranges:
        # Unmerge each cell
        ws.unmerge_cells(str(merged_cell))
        
        # Get the top-left cell value of the merged range (only first row)
        top_left_cell_value = ws.cell(row=merged_cell.min_row, column=merged_cell.min_col).value
        
        # Fill only the top-left cell and leave others blank
        for row in ws.iter_rows(min_row=merged_cell.min_row, max_row=merged_cell.max_row,
                                min_col=merged_cell.min_col, max_col=merged_cell.max_col):
            for cell in row:
                if cell.row == merged_cell.min_row and cell.column == merged_cell.min_col:
                    # Keep the top-left value
                    cell.value = top_left_cell_value
                else:
                    # Set all other cells to None (empty)
                    cell.value = None
    
    # Save the modified workbook after unmerging and filling cells
    modified_file = 'unmerged_filled_first_row_only.xlsx'
    wb.save(modified_file)
    
    # Load the modified Excel into a pandas DataFrame
    df = pd.read_excel(modified_file, sheet_name=sheet_name)
    
    # Save the modified DataFrame back to an Excel file if needed
    df.to_excel('unmerged_filled_first_row_only_processed.xlsx', index=False)
    print(f"Unmerged cells (first row values only) saved to: 'unmerged_filled_first_row_only_processed.xlsx'")
    
    return df

# Example usage
excel_file = 'your_excel_file.xlsx'
sheet_name = 'Sheet1'

# Process the Excel sheet
df = unmerge_and_fill_first_row_only(excel_file, sheet_name)

# Display the modified DataFrame
print(df)
