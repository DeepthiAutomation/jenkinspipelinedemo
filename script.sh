#!/bin/bash

# Input file containing words to search for
input_file="words.txt"

# File to search within
search_file="data.txt"

# Loop through each line in the input file
while IFS= read -r word
do
    # Use grep to search for the word in the search file
    grep "$word" "$search_file"
done < "$input_file"
