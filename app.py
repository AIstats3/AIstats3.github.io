from flask import Flask, render_template, request, jsonify
import os
from dashboard.parser_module import readgame, get_rotation_df, minutes_to_time_format
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    game_folder = os.path.join('dashboard', 'games')
    game_files = sorted(f for f in os.listdir(game_folder) if f.endswith('.csv'))
    return render_template('index.html', game_files=game_files)

@app.route('/lineup-stats', methods=['POST'])
def lineup_stats():
    data = request.get_json()
    selected_files = data.get('files', [])
    if not selected_files:
        return jsonify([])

    all_dfs = []
    for file in selected_files:
        file_path = os.path.join('dashboard', 'games', file)
        game_data = readgame(file_path)
        rotation_df = get_rotation_df(game_data)
        rotation_df['game'] = file.replace('.csv', '')
        all_dfs.append(rotation_df)

    if not all_dfs:
        return jsonify([])

    combined_df = pd.concat(all_dfs)
    combined_df['Lineup'] = combined_df['Lineup'].apply(tuple)
    grouped = combined_df.groupby('Lineup').agg({
        'Shift_length': 'sum',
        '+/-': 'sum'
    }).reset_index()

    grouped['Shift_length'] = grouped['Shift_length'].round(2)
    grouped['+/-'] = grouped['+/-'].round(1)
    grouped.sort_values(by='Shift_length', ascending=False, inplace=True)
    grouped['Shift_length'] = grouped['Shift_length'].apply(minutes_to_time_format)
    return grouped.to_json(orient='records')

if __name__ == '__main__':
    app.run(debug=True)
