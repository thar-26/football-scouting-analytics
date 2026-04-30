import pandas as pd
import numpy as np

DATA_PATH = "./"

def load_all_data():
    print("Loading dataset...")
    players = pd.read_csv(f"{DATA_PATH}players.csv")
    valuations = pd.read_csv(f"{DATA_PATH}player_valuations.csv")
    appearances = pd.read_csv(f"{DATA_PATH}appearances.csv")
    games = pd.read_csv(f"{DATA_PATH}games.csv")
    clubs = pd.read_csv(f"{DATA_PATH}clubs.csv")
    competitions = pd.read_csv(f"{DATA_PATH}competitions.csv")
    transfers = pd.read_csv(f"{DATA_PATH}transfers.csv")
    print(f"Players: {len(players)}")
    print(f"Valuations: {len(valuations)}")
    print(f"Appearances: {len(appearances)}")
    print(f"Transfers: {len(transfers)}")
    return players, valuations, appearances, games, clubs, competitions, transfers

def build_player_profiles():
    players, valuations, appearances, games, clubs, competitions, transfers = load_all_data()

    # Get latest market value per player
    latest_valuations = valuations.sort_values('date').groupby('player_id').last().reset_index()
    latest_valuations = latest_valuations[['player_id', 'market_value_in_eur']]

    # Aggregate appearance stats per player
    print("Aggregating player stats...")
    player_stats = appearances.groupby('player_id').agg(
        total_appearances=('game_id', 'count'),
        total_goals=('goals', 'sum'),
        total_assists=('assists', 'sum'),
        total_minutes=('minutes_played', 'sum'),
        yellow_cards=('yellow_cards', 'sum'),
        red_cards=('red_cards', 'sum')
    ).reset_index()

    # Per 90 metrics
    player_stats['goals_per_90'] = (
        player_stats['total_goals'] / player_stats['total_minutes'] * 90
    ).round(2)
    player_stats['assists_per_90'] = (
        player_stats['total_assists'] / player_stats['total_minutes'] * 90
    ).round(2)
    player_stats['goal_contributions_per_90'] = (
        player_stats['goals_per_90'] + player_stats['assists_per_90']
    ).round(2)

    # Calculate age from date_of_birth
    players['date_of_birth'] = pd.to_datetime(players['date_of_birth'], errors='coerce')
    players['age'] = ((pd.Timestamp.now() - players['date_of_birth']).dt.days / 365).round(1)

    # Merge player stats
    profiles = players.merge(latest_valuations, on='player_id', how='left')
    profiles = profiles.merge(player_stats, on='player_id', how='left')

    # Merge club info
    clubs_slim = clubs[['club_id', 'name', 'domestic_competition_id']].rename(
        columns={'name': 'club_name', 'club_id': 'current_club_id'}
    )
    profiles = profiles.merge(clubs_slim, on='current_club_id', how='left')

    # Merge competition info
    comps_slim = competitions[['competition_id', 'name', 'country_name']].rename(
        columns={'name': 'competition_name'}
    )
    profiles = profiles.merge(
        comps_slim,
        left_on='domestic_competition_id',
        right_on='competition_id',
        how='left'
    )

    # Use market_value from players.csv if valuation missing
    profiles['market_value_in_eur'] = profiles['market_value_in_eur_x'].fillna(
        profiles['market_value_in_eur_y']
    )

    # Clean and filter
    profiles = profiles[profiles['total_minutes'] > 500]
    profiles = profiles[profiles['market_value_in_eur'] > 0]
    profiles = profiles.dropna(subset=['market_value_in_eur', 'total_goals'])

    print(f"Player profiles built: {len(profiles)}")
    return profiles

def find_undervalued_players(profiles, position_filter=None, max_age=26,
                              max_value_eur=10_000_000, min_appearances=10):
    df = profiles.copy()

    if 'age' in df.columns:
        df = df[df['age'] <= max_age]
    df = df[df['market_value_in_eur'] <= max_value_eur]
    df = df[df['total_appearances'] >= min_appearances]

    if position_filter and position_filter != 'All':
        df = df[df['position'].str.contains(position_filter, case=False, na=False)]

    df['performance_percentile'] = df['goal_contributions_per_90'].rank(pct=True).round(2) * 100
    df['value_percentile'] = (1 - df['market_value_in_eur'].rank(pct=True)).round(2) * 100
    df['opportunity_score'] = ((df['performance_percentile'] + df['value_percentile']) / 2).round(1)

    return df.sort_values('opportunity_score', ascending=False)

def find_similar_players(profiles, player_name, top_n=5):
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import cosine_similarity

    features = ['goals_per_90', 'assists_per_90', 'total_appearances', 'age']
    df = profiles.dropna(subset=features).copy()

    if player_name not in df['name'].values:
        return None

    scaler = StandardScaler()
    X = scaler.fit_transform(df[features])

    idx = df[df['name'] == player_name].index[0]
    player_vec = X[df.index.get_loc(idx)].reshape(1, -1)

    similarities = cosine_similarity(player_vec, X)[0]
    df['similarity'] = similarities

    similar = df[df['name'] != player_name].nlargest(top_n, 'similarity')
    return similar[['name', 'age', 'position', 'current_club_name',
                     'market_value_in_eur', 'goals_per_90',
                     'assists_per_90', 'similarity']]

if __name__ == "__main__":
    profiles = build_player_profiles()
    print("\nSample profiles:")
    print(profiles[['name', 'age', 'position', 'current_club_name',
                     'market_value_in_eur', 'goals_per_90',
                     'total_appearances']].head(10).to_string())

    print("\nTop undervalued players:")
    undervalued = find_undervalued_players(profiles)
    print(undervalued[['name', 'age', 'position', 'current_club_name',
                        'market_value_in_eur', 'goal_contributions_per_90',
                        'opportunity_score']].head(10).to_string())