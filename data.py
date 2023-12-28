import pandas as pd
import matplotlib.pyplot as plt

# Read the Excel file into a pandas DataFrame
file_path = 'data.xlsx'  # Replace with your file path
sheet_name = 'Sheet1'    # Replace with your sheet name if different

data = pd.read_excel(file_path, sheet_name=sheet_name)

# Assuming 'Values' is the column name containing your data
value_counts = data['Values'].value_counts()

# Extracting unique values and their counts
x_values = value_counts.index.tolist()
y_values = value_counts.values.tolist()

# Creating the line chart
plt.plot(x_values, y_values, marker='o', linestyle='-')

# Labeling axes and adding title
plt.xlabel('X-axis (Values)')
plt.ylabel('Y-axis (Count)')
plt.title('Line Chart of Value Counts')

# Show grid (optional)
plt.grid(True)

# Display the chart
plt.show()
