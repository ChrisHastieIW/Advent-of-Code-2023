
######################
## Imports

import re

######################
## Shared code

### Determine input file location
input_file_path = "01\sample_input.txt"
input_file_path = "01\sample_input_2.txt"
input_file_path = "01\input.txt"

### Read file into list
with open(input_file_path, "r") as my_file:
  list_strings = my_file.read().splitlines()

######################
## Part 1

### Use nested list comprehension to receive the list of numbers
list_numbers = [
  
  ### Combine the first and last digits and convert to int
  int(digit_list[0] + digit_list[-1])
  
  ### Parse list for digits
  for digit_list in [re.findall(r"\d", x) for x in list_strings]
]

### Sum the numbers
result = sum(list_numbers)

print(f"Part 1 result: {str(result)}")

######################
## Part 2

### Map string digits
number_mappings = {
    "one": "1"
  , "two": "2"
  , "three": "3"
  , "four": "4"
  , "five": "5"
  , "six": "6"
  , "seven": "7"
  , "eight": "8"
  , "nine": "9"
}

### Create string of possible values for regex match
regex_match_string = r'(\d|' + "|".join(number_mappings.keys()) + ")"

### To ensure entries such as "twone" return both "two" and "one",
### regex matching needs to allow for overlaps by using a positive lookahead
overlapping_regex_match_string = "(?=" + regex_match_string + ")"

### Use nested list comprehension to receive the list of numbers
list_numbers_2 = [
  
  ### Combine the first and last digits and convert to int
  int(converted_digit_list[0] + converted_digit_list[-1]) 
  
  for converted_digit_list in [
    ### Convert digits to ints
    [number_mappings[digit] if digit in number_mappings.keys() else digit for digit in digit_list]

    ### Parse list for digits, now allowing for digits written as strings
    ### and allowing for overlaps so entries such as "twone" return both "two" and "one"
    for digit_list in [re.findall(overlapping_regex_match_string, x) for x in list_strings]
  ]
]

### Sum the numbers
result_2 = sum(list_numbers_2)

print(f"Part 2 result: {str(result_2)}")
