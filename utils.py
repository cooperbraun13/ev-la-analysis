""" 
minimal helper for pulling mariners batted-ball events with pybaseball and writing to a csv
"""

import pandas as pd
from pybaseball import statcast

HIT_EVENTS = {"single", "double", "triple", "home_run"}

def fetch_mariners_bbe_csv(
  # year-month-date format
  start_date: str = "2025-03-28",
  end_date: str = "2025-05-01",
  max_rows: int = 200,
  output_csv: str = "mariners_2025_batted_balls.csv",
) -> pd.DataFrame:
  """ 
  pull statcast data for the date window (mariners only), keep batted balls with ev/la, sort newest to oldest,
  take up to "max_rows", and write to "output_csv". returns the dataframe written
  """
  # first query the mariners directly
  raw_statcast_data = statcast(start_dt=start_date, end_dt=end_date, team="SEA")
  
  # only want to keep batted balls that have track exit velocity (ev) and launch angle (la)
  batted_balls = raw_statcast_data[raw_statcast_data["launch_speed"].notna() & raw_statcast_data["launch_angle"].notna()].copy()
  
  # create a cleaner event label and a binary is_hit flag to simplify things
  batted_balls["event_type"] = batted_balls["events"].fillna(batted_balls.get("description", ""))
  batted_balls["is_hit"] = batted_balls["event_type"].str.lower().isin(HIT_EVENTS).astype(int)
  
  # sort the data by game date (newest first). if available, use pitch number as a secondary criterion/tie-breaker
  sort_cols = ["game_date"]
  if "pitch_number" in batted_balls.columns:
    sort_cols.append("pitch_number")
  batted_balls = batted_balls.sort_values(sort_cols, ascending=False).head(max_rows)
  
  # define the columns to retain in the final dataframe, this ensures the output is clean and relevant to the analysis
  columns_to_keep = [
    "game_date", "home_team", "away_team", "inning", "inning_topbot",
    "batter", "player_name", "player_id", "pitcher", "pitcher_id", "launch_speed", 
    "launch angle", "events", "description", "event_type", "is_hit",
  ]
  
  batted_balls = batted_balls[[column for column in columns_to_keep if column in batted_balls.columns]].copy()
  
  # write to csv file to show data and then return the dataframe
  batted_balls.to_csv(output_csv, index=False)
  return batted_balls