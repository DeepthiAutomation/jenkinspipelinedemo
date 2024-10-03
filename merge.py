import pandas as pd
from openpyxl import load_workbook

# Function to handle merged cells
def unmerge_and_fill(excel_file, sheet_name):
    # Load the workbook and the specific sheet
    wb = load_workbook(excel_file)
    ws = wb[sheet_name]
    
    # Iterate through all merged cells
    for merged_cell in ws.merged_cells.ranges:
        # Unmerge each cell
        ws.unmerge_cells(str(merged_cell))
        
        # Get the top-left cell value of the merged range
        top_left_cell_value = ws[merged_cell.min_row][merged_cell.min_col - 1].value
        
        # Fill the unmerged cells with the top-left cell value
        for row in ws.iter_rows(min_row=merged_cell.min_row, max_row=merged_cell.max_row,
                                min_col=merged_cell.min_col, max_col=merged_cell.max_col):
            for cell in row:
                cell.value = top_left_cell_value
    
    # Save the modified workbook if needed
    modified_file = 'unmerged_filled.xlsx'
    wb.save(modified_file)
    print(f"Unmerged and filled cells saved to: {modified_file}")
    
    # Return a pandas DataFrame for further manipulation
    return pd.read_excel(modified_file, sheet_name=sheet_name)

# Example usage
excel_file = 'your_excel_file.xlsx'
sheet_name = 'Sheet1'

# Process the Excel sheet
df = unmerge_and_fill(excel_file, sheet_name)

# Display the modified DataFrame
print(df)
