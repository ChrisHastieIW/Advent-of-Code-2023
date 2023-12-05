
######################
## Imports

import pandas as pd
import numpy as np

######################
## Functions

## Define function to parse the input into a list
def read_input_to_list(input_file: str) :
  
  ### Ingest file into list
  with open(input_file, 'r') as f:
    list_input = f.read().splitlines()
  
  return list_input

## Define function to parse the inputs into a dataframe of seeds
def parse_input_to_dataframe_seeds(list_input: list):

  list_seeds = list_input[0].split(":")[-1].strip().split(" ")

  df_seeds = pd.DataFrame(list_seeds, columns=["seed_id"]).astype("int64")
  
  return df_seeds

## Define function to parse the inputs into a dataframe of seeds
## defined as ranges, for part 2 of the challenge
def parse_input_to_dataframe_seed_ranges(list_input: list):

  list_seeds = list_input[0].split(":")[-1].strip().split(" ")

  df_seed_ranges = pd.DataFrame(np.array_split(list_seeds, len(list_seeds)/2), columns=["seed_range_start", "seed_range_length"]).astype("int64")
  
  return df_seed_ranges

## Define function to parse the inputs into a dataframe of maps
def parse_input_to_dataframe_maps(list_input: list):

  df_raw = pd.DataFrame(list_input[2:], columns=["raw"])

  df_raw["mapping"] = df_raw.apply(lambda x: x["raw"].split()[0] if x["raw"].endswith("map:") else None, axis=1).fillna(method="ffill")

  df_raw[["mapping_source", "mapping_destination"]] = df_raw['mapping'].str.split("-to-", expand=True)
  df_raw[["destination_range_start", "source_range_start", "range_length"]] = df_raw['raw'].str.split(" ", expand=True)

  df_maps = df_raw.drop(["raw", "mapping"], axis=1).dropna(subset="range_length").astype({"destination_range_start":"int64", "source_range_start":"int64", "range_length":"int64"})

  return df_maps

## Define function to map seeds
def map_seeds(df_seeds: pd.DataFrame, df_maps: pd.DataFrame):

  ### Initial build
  df_seeds_mapped = df_seeds.copy()
  df_seeds_mapped["current_category"] = "seed"
  df_seeds_mapped["current_id"] = df_seeds_mapped["seed_id"]

  for counter in range(len(df_maps["mapping_destination"].unique())):
    df_seeds_mapped = pd.merge(df_seeds_mapped, df_maps, how="inner", left_on = "current_category", right_on = "mapping_source")
    
    df_seeds_mapped["map_match"] = df_seeds_mapped.apply(lambda x: (x["current_id"] >= x["source_range_start"]) and (x["current_id"] < x["source_range_start"] + x["range_length"]), axis=1)
    # df_seeds_mapped["map_match"] = df_seeds_mapped.apply(lambda x: x["current_id"] in range(x["source_range_start"], x["source_range_start"] + x["range_length"]), axis=1)
    
    df_mapping_exists = pd.Series.to_frame(df_seeds_mapped.groupby("current_id")["map_match"].max().rename("mapping_exists"))
    df_seeds_mapped = pd.merge(df_seeds_mapped, df_mapping_exists, how="inner", on = "current_id")

    df_seeds_mapped = pd.concat(
        [
            df_seeds_mapped[(df_seeds_mapped["mapping_exists"] == True) & (df_seeds_mapped["map_match"] == True)]
          , df_seeds_mapped[(df_seeds_mapped["mapping_exists"] == False)].groupby("seed_id").first().reset_index().drop(["destination_range_start", "source_range_start", "range_length"], axis=1)
        ]
      , ignore_index=True
    )

    df_seeds_mapped["current_category"] = df_seeds_mapped["mapping_destination"]
    df_seeds_mapped["current_id"] = df_seeds_mapped.apply(lambda x: x["current_id"] - x["source_range_start"] + x["destination_range_start"] if x["map_match"] == True else x["current_id"], axis=1)

    df_seeds_mapped = df_seeds_mapped[["seed_id", "current_category", "current_id"]]

  return df_seeds_mapped

## Define function to determine if ranges overlap
## whilst trying to be performant and not use range()
def test_overlap(source_range_start, source_range_length, target_range_start, target_range_length):
  source_range_end = source_range_start + source_range_length - 1
  target_range_end = target_range_start + target_range_length - 1
  overlap_found = \
       (source_range_start >= target_range_start and source_range_start <= target_range_end) \
    or (source_range_end >= target_range_start and source_range_end <= target_range_end) \
    or (target_range_start >= source_range_start and target_range_start <= source_range_end) \
    or (target_range_end >= source_range_start and target_range_end <= source_range_end)
  
  return overlap_found

## Define function to determine if ranges overlap
## whilst trying to be performant and not use range()
def find_overlap(source_range_start, source_range_length, target_range_start, target_range_length):
  overlap_found = test_overlap(source_range_start=source_range_start, source_range_length=source_range_length, target_range_start=target_range_start, target_range_length=target_range_length)
  
  if overlap_found == False:
    overlap_range_start = None
    overlap_range_length = None
  else:
    overlap_range_start = max(source_range_start, target_range_start)
    overlap_range_length = min(source_range_start + source_range_length, target_range_start + target_range_length) - overlap_range_start

  return overlap_range_start, overlap_range_length

## Define function to map seed ranges
def map_seed_ranges(df_seed_ranges: pd.DataFrame, df_maps: pd.DataFrame):

  ### Initial build
  df_seed_ranges_mapped = df_seed_ranges.copy()
  df_seed_ranges_mapped["current_range_start"] = df_seed_ranges_mapped["seed_range_start"]
  df_seed_ranges_mapped["current_range_length"] = df_seed_ranges_mapped["seed_range_length"]
  df_seed_ranges_mapped["current_category"] = "seed"

  df_seed_ranges_mapped = df_seed_ranges_mapped[["current_category", "current_range_start", "current_range_length"]]

  for counter in range(len(df_maps["mapping_destination"].unique())):
    df_seed_ranges_mapped = pd.merge(df_seed_ranges_mapped, df_maps, how="inner", left_on = "current_category", right_on = "mapping_source").drop("mapping_source", axis=1)
    
    df_seed_ranges_mapped["overlap_range_start"] = df_seed_ranges_mapped.apply(lambda x: find_overlap(source_range_start = x["current_range_start"], source_range_length = x["current_range_length"], target_range_start = x["source_range_start"], target_range_length = x["range_length"])[0], axis=1).astype("Int64")
    df_seed_ranges_mapped["overlap_range_length"] = df_seed_ranges_mapped.apply(lambda x: find_overlap(source_range_start = x["current_range_start"], source_range_length = x["current_range_length"], target_range_start = x["source_range_start"], target_range_length = x["range_length"])[1], axis=1).astype("Int64")
    
    df_mapping_exists = pd.Series.to_frame(df_seed_ranges_mapped.groupby(["current_range_start", "current_range_length"])["overlap_range_start"].max().notna().rename("mapping_exists"))
    df_seed_ranges_mapped = pd.merge(df_seed_ranges_mapped, df_mapping_exists, how="inner", on = ["current_range_start", "current_range_length"])

    df_seed_ranges_mapped["current_category"] = df_seed_ranges_mapped["mapping_destination"]


    ### Determine components - Unmatched
    df_unmatched_records = df_seed_ranges_mapped[(df_seed_ranges_mapped["mapping_exists"] == False)].groupby(["current_range_start", "current_range_length"]).first().reset_index()[["current_range_start", "current_range_length", "current_category"]]
    
    ### Determine components - Matched all
    df_matched_records_all = df_seed_ranges_mapped[(df_seed_ranges_mapped["mapping_exists"] == True) & (df_seed_ranges_mapped["overlap_range_start"].notna())].copy()
    

    df_matched_records_all["range_before_overlap"] = df_matched_records_all.apply(lambda x: x["overlap_range_start"] - x["current_range_start"], axis=1).astype("int64")
    df_matched_records_all["range_after_overlap"] = df_matched_records_all.apply(lambda x: x["current_range_length"] - x["overlap_range_length"] - x["range_before_overlap"], axis=1).astype("int64")

    ### Determine components - Matched
    df_matched_records = df_matched_records_all.copy()
    df_matched_records["current_range_start"] = (df_matched_records["destination_range_start"] + df_matched_records["overlap_range_start"] - df_matched_records["source_range_start"])
    df_matched_records["current_range_length"] = df_matched_records["overlap_range_length"]
    df_matched_records = df_matched_records[["current_range_start", "current_range_length", "current_category"]]

    ### Determine components - Matched Spillover 1 (before overlap)
    df_matched_record_spillover_1 = df_matched_records_all[df_matched_records_all["range_before_overlap"] > 0].copy()
    df_matched_record_spillover_1["current_range_length"] = df_matched_record_spillover_1["range_before_overlap"] - 1
    df_matched_record_spillover_1 = df_matched_record_spillover_1[["current_range_start", "current_range_length", "current_category"]]
    
    ### Determine components - Matched Spillover 2 (after overlap)
    df_matched_record_spillover_2 = df_matched_records_all[df_matched_records_all["range_after_overlap"] > 0].copy()
    df_matched_record_spillover_2["current_range_start"] = df_matched_record_spillover_2["overlap_range_start"] + df_matched_record_spillover_2["overlap_range_length"] + 1
    df_matched_record_spillover_2["current_range_length"] = df_matched_record_spillover_2["range_after_overlap"]
    df_matched_record_spillover_2 = df_matched_record_spillover_2[["current_range_start", "current_range_length", "current_category"]]

    df_seed_ranges_mapped = pd.concat(
        [
            df_matched_records
          , df_unmatched_records
          , df_matched_record_spillover_1
          , df_matched_record_spillover_2
        ]
      , ignore_index=True
    )

  
    df_seed_ranges_mapped = df_seed_ranges_mapped[["current_category", "current_range_start", "current_range_length"]] \
      .groupby(["current_range_start", "current_range_length"]).first().reset_index()
    
  return df_seed_ranges_mapped

######################
## Part 1

input_file_path = "05/sample_input.txt"
input_file_path = "05/input.txt"

list_input = read_input_to_list(input_file = input_file_path)

df_seeds = parse_input_to_dataframe_seeds(list_input = list_input)
df_maps = parse_input_to_dataframe_maps(list_input = list_input)
df_seeds_mapped = map_seeds(df_seeds = df_seeds, df_maps = df_maps)

### Part 1 result: 51752125
print(f"""Part 1 result: {str(int(df_seeds_mapped["current_id"].min()))}""")

######################
## Part 1

input_file_path = "05/sample_input.txt"
input_file_path = "05/input.txt"

list_input = read_input_to_list(input_file = input_file_path)

df_seed_ranges = parse_input_to_dataframe_seed_ranges(list_input = list_input)
df_maps = parse_input_to_dataframe_maps(list_input = list_input)
df_seed_ranges_mapped = map_seed_ranges(df_seed_ranges = df_seed_ranges, df_maps = df_maps)

### Part 2 result: FAILED with 3244927. Too low.
### Will revisit later.
print(f"""Part 2 result: {str(df_seed_ranges_mapped["current_range_start"].min())}""")
