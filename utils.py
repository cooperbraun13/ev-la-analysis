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
  # first we want to query the mariners directly
  raw_statcast_data = statcast(start_dt=start_date, end_dt=end_date, team="SEA")
  
  # only want to keep batted balls that have track exit velocity (ev) and launch angle (la)
  batted_balls = raw_statcast_data[raw_statcast_data["launch_speed"].notna() & raw_statcast_data["launch_angle"].notna()].copy()
  
  # create a cleaner event label and a binary is_hit flag to simplify things
  batted_balls["event_type"] = batted_balls["events"].fillna(batted_balls.get("description", ""))
  batted_balls["is_hit"] = batted_balls["event_type"].str.lower().isin(HIT_EVENTS).astype(int)