
######################
## Imports

from math import prod

######################
## Shared code

### Determine input file location
input_file_path = "02\sample_input.txt"
input_file_path = "02\input.txt"

### Read file into list
with open(input_file_path, "r") as my_file:
  list_games = my_file.read().splitlines()

### Use list and dict comprehension to split
### the games into a structure
list_game_details = [
  {
      "id": int(game.split(": ")[0].split(" ")[-1])
    , "sets": [
        {
          x.split(" ")[-1]: int(x.split(" ")[0])
          for x in set.split(", ")
        }
        for set in game.split(": ")[-1].split("; ")
      ]
  }
  for game in list_games
]

######################
## Part 1

### limits
limits = {
    "red": 12
  , "green": 13
  , "blue": 14
}

### List comprehension for entries that pass validation
list_valid_games = [
  game
  for game in list_game_details 
  if all([
    all([
      game_set[key] <= limits[key]
      for key in game_set.keys()
    ])
    for game_set in game["sets"]
  ])
]

### Sum the ids
result = sum([game["id"] for game in list_valid_games])

print(f"Part 1 result: {str(result)}")


######################
## Part 2

### More list comprehension to find the max count
### of each colour in the set, which is the power
list_games_with_powers = [
  {
      "id": game["id"]
    , "sets": game["sets"]
    , "powers": [
        max([
            game_set[colour]
            for game_set in game["sets"]
            if colour in game_set.keys()
          ])
        for colour in limits
      ]
  }
  for game in list_game_details
]

### Sum the powers products
result_2 = sum([prod(game["powers"]) for game in list_games_with_powers])

print(f"Part 2 result: {str(result_2)}")