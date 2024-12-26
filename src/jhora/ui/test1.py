create_cyclic_list = lambda row_count, col_count, start: [
    [(start + (i * row_count + j)) % col_count for j in range(col_count)]
    for i in range(row_count)
]

# Example usage
# Generate the first list starting with 0
first_list = create_cyclic_list(12, 7, 0)

# Generate the second list starting with one less than the last value of the last row/col of the first list
start_value = (first_list[-1][-1] - 1) % 7
second_list = create_cyclic_list(12, 7, start_value)

print("First List:")
for row in first_list:
    print(row)

print("\nSecond List:")
for row in second_list:
    print(row)
