# Print the original array and the rounded exponential array
print("Base Array:")
print(Mat_A)

print("\n")

print("Exp array")
rounded_exp_array = np.round(Mat_A, decimals=2)
print(rounded_exp_array)

print("\n")

# Set print options to suppress scientific notation
np.set_printoptions(suppress=True)

print("\nExponential Array (Rounded):")
print(np.array2string(Mat_A, formatter={'float_kind': lambda x: "%.2f" % x}))
