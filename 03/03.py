
######################
## Imports

import numpy as np
import re
import itertools
import pandas as pd

######################
## Functions

## Define function to parse the input into an array
def parse_input(input_file: str) :
  
  ### Ingest file into list
  with open(input_file, 'r') as f:
    input_list = f.read().splitlines()

  ### Determine height and width of array
  height = len(input_list)
  width = len(input_list[0])

  array_input = np.empty([height, width], dtype=str)

  for height_position in range(height) :
    for width_position in range(width) :
      array_input[height_position, width_position] = input_list[height_position][width_position]

  return array_input

######################
## Part 1

array_input = parse_input(input_file = "03/sample_input.txt")
array_input = parse_input(input_file = "03/input.txt")

### Find symbols in input
symbols = [x for x in list(np.unique(array_input)) if x != "." and not re.match(r"\d", x)]
symbol_positions = np.argwhere(np.isin(array_input, symbols)).tolist()

### Find all positions which are within 1 of a symbol
symbol_range_positions = np.unique(
    [
      position
      for symbol_position in symbol_positions
      for position in
      list(itertools.product(
          range(symbol_position[0] - 1, symbol_position[0] + 2)
        , range(symbol_position[1] - 1, symbol_position[1] + 2)
      ))
    ]
  , axis=1
)
set_symbol_range_positions = set([tuple(x) for x in symbol_range_positions])

### Find positions of numbers in input
numbers = [x for x in list(np.unique(array_input)) if re.match(r"\d", x)]
number_positions = np.argwhere(np.isin(array_input, numbers))

### Create a set of data for all numbers in the schematic.
### I wanted to find a way to do this without loops but spent
### too long trying to find one, so gave up and used a loop.
list_numbers_data = []
temp_current_number_string = ""
temp_current_number_positions_list = []
for index, number_position in enumerate(number_positions.tolist()) :
  if len(temp_current_number_positions_list) == 0 \
    or (
      number_position[0] == temp_current_number_positions_list[-1][0] \
      and number_position[1] == temp_current_number_positions_list[-1][1] + 1
    ) \
      :
    temp_current_number_positions_list.append(number_position)
    temp_current_number_string += array_input[tuple(number_position)]
  else:
    list_numbers_data.append({
        "number": int(temp_current_number_string)
      , "positions_list": temp_current_number_positions_list
    })
    temp_current_number_positions_list = [number_position]
    temp_current_number_string = array_input[tuple(number_position)]
### Append final values
list_numbers_data.append({
    "number": int(temp_current_number_string)
  , "positions_list": temp_current_number_positions_list
})

### Build dataframe of numbers and determine if the positions
### ever overlaps with the symbol range positions
df_numbers = pd.DataFrame(list_numbers_data)
df_numbers["positions_list_as_set_of_tuples"] = df_numbers.apply(lambda x: set([tuple(y) for y in x["positions_list"]]), 1)
df_numbers["is_part_number"] = df_numbers.apply(lambda x: any(set.intersection(x["positions_list_as_set_of_tuples"], set_symbol_range_positions)), 1)

### Determine part numbers
df_part_numbers = df_numbers[df_numbers["is_part_number"]]

### Part 1 result
print(f"""Part 1 result: {str(df_part_numbers["number"].sum())}""")

######################
## Part 2

### Find gears in input
gear_positions = np.argwhere(np.isin(array_input, ["*"]))

### Create a set of data for all gears in the schematic.
### I wanted to find a way to do this without loops but spent
### too long trying to find one, so gave up and used a loop.
list_gears_data = []
for index, gear_position in enumerate(gear_positions.tolist()) :
  gear_range_positions = list(itertools.product(
      range(gear_position[0] - 1, gear_position[0] + 2)
    , range(gear_position[1] - 1, gear_position[1] + 2)
  ))
  set_gear_range_positions = set([tuple(x) for x in gear_range_positions])
  list_positions_of_numbers_near_gear = [set.intersection(set_gear_range_positions, x) for x in df_part_numbers["positions_list_as_set_of_tuples"] if set.intersection(set_gear_range_positions, x)]
  if len(list_positions_of_numbers_near_gear) == 2:
    list_gears_data.append({
        "gear_id": index
      , "gear_position": gear_position
      , "list_positions_of_numbers_near_gear": list_positions_of_numbers_near_gear
      , "set_of_tuples_of_positions_of_numbers_near_gear": set([y for x in list_positions_of_numbers_near_gear for y in list(x)])
    })

### Build dataframe of gears
df_gears = pd.DataFrame(list_gears_data)

### Build dataframe of gears and parts
df_gears_and_parts = df_gears.merge(df_part_numbers, how='cross')

df_gears_and_parts["is_aligned"] = df_gears_and_parts.apply(lambda x: any(set.intersection(x["set_of_tuples_of_positions_of_numbers_near_gear"], x["positions_list_as_set_of_tuples"])), axis=1)

df_aligned_gears_and_parts = df_gears_and_parts[df_gears_and_parts["is_aligned"]][["gear_id", "number"]]

df_aligned_gears_and_parts_aggregated = df_aligned_gears_and_parts.groupby("gear_id", as_index=False).prod().rename(columns={"number": "ratio"})


### Part 2 result
print(f"""Part 2 result: {str(df_aligned_gears_and_parts_aggregated["ratio"].sum())}""")
