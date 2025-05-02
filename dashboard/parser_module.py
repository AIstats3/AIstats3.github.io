import pandas as pd
import numpy as np

def seconds_to_time_format(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{int(minutes)}:{int(seconds):02d}"
def minutes_to_time_format(minutes_float):
    ##Get total seconds
    total_seconds = int(minutes_float * 60)
    
    ##Calculate minutes and seconds
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    
    ##Format as mm:ss
    return f"{minutes:02}:{seconds:02}"

def get_points(event):
    if 'm' in event:
        return 0  # Discount misses
    elif 't' in event:
        return 3  # Threes
    elif any(x in event for x in ['l', 'r']):
        return 2  # Layups and middies
    elif 'f' in event:
        return 1  # Free throws
    return 0  # Non-scoring events

def readgame(csv_path):
    events = pd.read_csv(csv_path, dtype={
        'year': 'int64',
        'month': 'int64',
        'day': 'int64',
        'hour': 'int64',
        'minute': 'int64',
        'second': 'int64',
        'period': 'string',
        'player': 'string',
        'event': 'string',
        'time on shotclock': 'int64',
        'player1': 'string',
        'player2': 'string',
        'player3': 'string',
        'player4': 'string',
        'player5': 'string',
        'opponent': 'string'
    })

    events['Time_seconds'] = 60 * events['minute'] + events['second']
    events['Time'] = events['Time_seconds'].apply(seconds_to_time_format)
    events['Con_points'] = 0
    events['Opp_points'] = 0

    con_score = 0
    opp_score = 0
    for i, row in events.iterrows():
        points = get_points(row['event'])
        if row['player'] == "-1":
            opp_score += points
        elif row['player'] != "0":
            con_score += points
        events.at[i, 'Con_points'] = con_score
        events.at[i, 'Opp_points'] = opp_score

    events['Score_margin'] = events['Con_points'] - events['Opp_points']

    def adjust_time(row):
        period_offsets = {
            'q2': 600, 'q3': 1200, 'q4': 1800,
            'OT': 2400, 'OT2': 2700, 'OT3': 3000
        }
        return row['Time_elapsed'] + period_offsets.get(row['period'], 0)

    events['Time_elapsed'] = events.apply(
        lambda row: (600 - row['Time_seconds']) if not row['period'].startswith('OT') else (300 - row['Time_seconds']),
        axis=1
    )
    events['Time_elapsed'] = events.apply(adjust_time, axis=1)
    events['game'] = f"{events['year'][0]}-{events['month'][0]}-{events['day'][0]}-{events['opponent'][0]}"
    events['Lineup'] = events[['player1', 'player2', 'player3', 'player4', 'player5']].apply(lambda row: sorted(list(row)), axis=1)

    periods = len(events['period'].unique())
    end_time = {5: 2700, 6: 3000, 7: 3300}.get(periods, 2400)
    end_row = pd.DataFrame({
        'Lineup': [np.nan],
        'Time': ['0:00'],
        'period': [np.nan],
        'event': ['sub'],
        'Con_points': [np.nan],
        'Opp_points': [np.nan],
        'Score_margin': [np.nan],
        'Time_elapsed': [end_time],
        'game': [np.nan]
    })
    events = pd.concat([events, end_row], ignore_index=True).ffill()

    return events

def get_rotation_df(events):
    subs_df = events.loc[events['event'] == 'sub', [
        'game', 'Lineup', 'period', 'Con_points', 'Opp_points',
        'Score_margin', 'Time', 'Time_elapsed'
    ]].copy()
    subs_df.reset_index(drop=True, inplace=True)

    subs_df[['Con_points', 'Opp_points', 'Score_margin']] = subs_df[['Con_points', 'Opp_points', 'Score_margin']].shift(-1)
    subs_df[['Time_out', 'Time_out_elapsed']] = subs_df[['Time', 'Time_elapsed']].shift(-1)

    subs_df['+/-'] = subs_df['Score_margin'] - subs_df['Score_margin'].shift(1)
    subs_df.loc[0, '+/-'] = subs_df.loc[0, 'Score_margin']

    subs_df.drop(index=len(subs_df) - 1, inplace=True)

    subs_df.rename(columns={'Time': 'Time_in', 'Time_elapsed': 'Time_in_elapsed'}, inplace=True)
    subs_df[['Time_in_elapsed', 'Time_out_elapsed']] /= 60
    subs_df['Shift_length'] = subs_df['Time_out_elapsed'] - subs_df['Time_in_elapsed']
    subs_df['+/-'] = subs_df['+/-'].astype(int)

    return subs_df

def compute_lineup_stats(csv_paths):
    all_rotation_dfs = []
    for path in csv_paths:
        events = readgame(path)
        rotation_df = get_rotation_df(events)
        all_rotation_dfs.append(rotation_df)

    combined = pd.concat(all_rotation_dfs, ignore_index=True)
    grouped = combined.groupby(combined['Lineup'].apply(tuple))[['+/-', 'Shift_length']].sum().reset_index()
    return grouped