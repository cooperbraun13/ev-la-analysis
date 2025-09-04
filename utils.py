"""
minimal helper for pulling cal raleigh batted-ball events with pybaseball and writing a csv
"""

import pandas as pd
from pybaseball import statcast_batter

HIT_EVENTS = {"single", "double", "triple", "home_run"}
# mlbam id for cal raleigh
CAL_RALEIGH_ID = 663728

def fetch_cal_raleigh_bbe_csv(
    start_date: str = "2025-05-01",
    end_date: str = "2025-05-28",
    max_rows: int = 200,
    output_csv: str = "cal_raleigh_may_batted_balls.csv",
) -> pd.DataFrame:
    """
    pull statcast data for cal raleigh for the date window, keep batted balls with exit velocity (ev) and launch angle (la),
    sort newest to oldest, take up to "max_rows", and write to "output_csv". returns the dataframe.
    """
    # query batter-specific statcast data
    raw_data = statcast_batter(start_dt=start_date, end_dt=end_date, player_id=CAL_RALEIGH_ID)

    # if no data or something goes wrong, still create an empty csv with expected columns and return
    if raw_data is None or raw_data.empty:
        empty = pd.DataFrame(
            columns=[
                "game_date", "home_team", "away_team", "inning", "inning_topbot",
                "batter", "pitcher", "launch_speed", "launch_angle",
                "events", "description", "event_type", "is_hit",
            ]
        )
        empty.to_csv(output_csv, index=False)
        return empty

    # keep only batted balls that have ev and la
    batted_balls = raw_data[raw_data["launch_speed"].notna() & raw_data["launch_angle"].notna()].copy()

    # create a cleaner event label and a binary hit flag (1 is a hit, 0 is not a hit)
    batted_balls["event_type"] = batted_balls["events"].fillna(batted_balls.get("description", ""))
    batted_balls["is_hit"] = batted_balls["event_type"].str.lower().isin(HIT_EVENTS).astype(int)

    # sort latest first (use pitch_number as a tie-breaker if present)
    sort_cols = ["game_date"]
    if "pitch_number" in batted_balls.columns:
        sort_cols.append("pitch_number")
    filtered_batted_balls = batted_balls.sort_values(sort_cols, ascending=False).head(max_rows)

    # keep relevant columns
    columns_to_keep = [
        "game_date", "home_team", "away_team", "inning", "inning_topbot",
        "batter", "pitcher", "launch_speed", "launch_angle",
        "events", "description", "event_type", "is_hit",
    ]
    final_df = filtered_batted_balls[[c for c in columns_to_keep if c in filtered_batted_balls.columns]].copy()

    final_df.to_csv(output_csv, index=False)
    return final_df