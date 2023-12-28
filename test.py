import matplotlib.pyplot as plt
from collections import Counter

# Sample data
data = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5]  # Your dataset

# Count occurrences of each value
value_counts = Counter(data)

# Separate X and Y values for plotting
x_values = list(value_counts.keys())
y_values = list(value_counts.values())

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
