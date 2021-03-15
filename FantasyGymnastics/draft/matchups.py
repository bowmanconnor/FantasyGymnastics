import random

# Generator function for list of matchups from a team_list
def games_from_list(team_list):
    n_teams = len(team_list)
    for i in range(int(n_teams/2)):
        yield team_list[i], team_list[i+int(n_teams/2)]

# Function to apply rotation to list of teams as described in article
def rotate_list(team_list):
    n_teams = len(team_list)
    team_list = [team_list[int(n_teams/2)]] + team_list[0:int(n_teams/2-1)] + team_list[int(n_teams/2+1):n_teams] + [team_list[int(n_teams/2-1)]]
    team_list[0], team_list[1] = team_list[1], team_list[0]
    return team_list

def round_robin_matchups(n_teams, n_weeks):
  # Generate list of teams & empty list of games played
  teams = list(range(1, n_teams+1))
  matchups_dict = {}
  games_played = []
  matchups = []

  # Optionally shuffle teams before generating schedule
  random.shuffle(teams)

  # For each week -
  for week in range(n_weeks):

      # Get all the pairs of games from the list of teams.
      week_pairs = []
      for pair in games_from_list(teams):
          # If the matchup has already been played:
          if pair in games_played:
              # Play the opposite match
              pair = pair[::-1]

          # Print the matchup and append to list of games.
          #week_pairs.append(str(pair[0]) + " vs " + str(pair[1]))
          week_pairs.append((pair[0], pair[1]))
          games_played.append(pair)

      # Assign all pairs of matchups to the current week
      #matchups_dict["Week "+str(week+1)] = week_pairs
      matchups_dict[week+1] = week_pairs
      matchups.append(week_pairs)

      # Rotate the list of teams
      teams = rotate_list(teams)
  return matchups_dict

if __name__ == "__main__":
    print(round_robin_matchups(2, 12))

