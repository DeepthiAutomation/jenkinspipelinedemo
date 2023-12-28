import pandas as pd
import matplotlib.pyplot as plt

# Read the Excel file into a pandas DataFrame
file_path = 'your_file.xlsx'  # Replace 'your_file.xlsx' with your file path
sheet_name = 'Sheet1'  # Replace 'Sheet1' with your sheet name if different

data = pd.read_excel(file_path, sheet_name=sheet_name)

# Assuming 'Values' is the column name containing your data
value_counts = data['Values'].value_counts()

# Extracting unique values and their counts
x_values = value_counts.index.tolist()
y_values = value_counts.values.tolist()

# Create a mapping of full month names to 3-letter abbreviated names
month_mapping = {
    'January': 'Jan', 'February': 'Feb', 'March': 'Mar', 'April': 'Apr',
    'May': 'May', 'June': 'Jun', 'July': 'Jul', 'August': 'Aug',
    'September': 'Sep', 'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
}

# Sort x_values by the order of abbreviated month names
x_values_sorted = sorted(x_values, key=lambda month: list(month_mapping.keys()).index(month))

# Create a plot of the line chart
plt.plot([month_mapping[month] for month in x_values_sorted], y_values, marker='o', linestyle='-')

# Labeling axes and adding title
plt.xlabel('X-axis (Month)')
plt.ylabel('Y-axis (Count)')
plt.title('Line Chart of Value Counts')

# Show grid (optional)
plt.grid(True)

# Display the chart
plt.show()
