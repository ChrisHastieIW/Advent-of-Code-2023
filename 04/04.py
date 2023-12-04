
######################
## Imports

import pandas as pd

######################
## Functions

## Define function to parse the input into a list
def read_input_to_list(input_file: str) :
  
  ### Ingest file into list
  with open(input_file, 'r') as f:
    list_input = f.read().splitlines()
  
  return list_input

## Define function to transform the raw input into a DataFrame
def parse_input_to_dataframe(list_input: list) :
  
  df_cards = pd.DataFrame(list_input, columns=["raw"])

  df_cards["id"] = df_cards.apply(lambda x: int(x["raw"].split(":")[0].split(" ")[-1]), axis=1)
  df_cards["winning_numbers"] = df_cards.apply(lambda x: [int(y) for y in x["raw"].split(":")[1].strip().split("|")[0].strip().split()], axis=1)
  df_cards["numbers_you_have"] = df_cards.apply(lambda x: [int(y) for y in x["raw"].split(":")[1].strip().split("|")[1].strip().split()], axis=1)
  df_cards["your_winning_numbers"] = df_cards.apply(lambda x: list(set.intersection(set(x["winning_numbers"]), set(x["numbers_you_have"]))), axis=1)
  df_cards["your_winning_numbers_count"] = df_cards.apply(lambda x: len(x["your_winning_numbers"]), axis=1)
  df_cards["points"] = df_cards.apply(lambda x: 0 if x["your_winning_numbers_count"] == 0 else pow(2, x["your_winning_numbers_count"] - 1), axis=1)

  df_cards.set_index("id", inplace=True, drop=False)
  
  return df_cards[["id", "winning_numbers", "numbers_you_have", "your_winning_numbers", "your_winning_numbers_count", "points"]]

## Define function that will act recursively to count the scratchcards
def count_scratchcards(df_cards: pd.DataFrame, card_id: int):
  additional_scratchcard_count_from_df = df_cards[df_cards["id"] == card_id]["additional_scratchcard_count"].iloc[0]
  if additional_scratchcard_count_from_df is not None :
    return additional_scratchcard_count_from_df
  else :
    current_scratchcard_winning_numbers_count = df_cards[df_cards["id"] == card_id]["your_winning_numbers_count"].iloc[0]
    if current_scratchcard_winning_numbers_count > 0 :
      new_scratchcard_ids = range(card_id + 1, card_id + 1 + current_scratchcard_winning_numbers_count)
      additional_scratchcard_count = len(new_scratchcard_ids)
      for new_scratchcard_id in new_scratchcard_ids:
        additional_scratchcard_count += count_scratchcards(df_cards=df_cards, card_id = new_scratchcard_id)
    else:
      additional_scratchcard_count = 0
    return additional_scratchcard_count



######################
## Part 1

input_file_path = "04/sample_input.txt"
input_file_path = "04/input.txt"

list_input = read_input_to_list(input_file = input_file_path)

df_cards = parse_input_to_dataframe(list_input = list_input)

### Part 1 result
print(f"""Part 1 result: {str(df_cards["points"].sum())}""")

######################
## Part 2 - Introducing recursion and it's only day 4!

### Initial values
df_cards["additional_scratchcards"] = df_cards.apply(lambda x: list(range(x["id"] + 1, x["id"] + 1 + x["your_winning_numbers_count"])), axis=1)
df_cards["additional_scratchcard_count"] = None

### Go backwards up the dataframe to solve smaller nests first
for x in range(len(df_cards), 0, -1) :
  df_cards.at[x, "additional_scratchcard_count"] = count_scratchcards(df_cards = df_cards, card_id = df_cards.loc[x]["id"])

### Total count
df_cards["total_scratchcard_count"] = df_cards["additional_scratchcard_count"] + 1

### Part 2 result
print(f"""Part 2 result: {str(df_cards["total_scratchcard_count"].sum())}""")
