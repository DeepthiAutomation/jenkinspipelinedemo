import pandas as pd

# Load data from Excel file (replace 'your_file.xlsx' with your actual file path)
file_path = 'your_file.xlsx'
df = pd.read_excel(file_path)

# Assuming the columns are named 'Column1', 'Column2', and 'Column3'.
# You can replace them with your actual column names or use column indices like df.iloc[:, 0] for the first column.

# Create a new column by joining Column1 and Column2, and appending Column3
df['Formatted'] = df.apply(lambda row: f"[{row['Column1']}-{row['Column2']}] {row['Column3']}", axis=1)

# Print the formatted data
print(df['Formatted'])

# Optionally save the formatted column to a new Excel file
df.to_excel('formatted_output.xlsx', index=False)
