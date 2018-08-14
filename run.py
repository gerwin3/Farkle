from functions import play, game, Strategy1, mean

def test_strategy(strategy):
    test_strategy = strategy
    test_num_games = 10000

    results = []

    for _ in range(test_num_games):
        result_score, _ = play(strategy=test_strategy, output=False)
        results.append(result_score)

    print ("Statistics over %d games" % test_num_games)
    print ("------------------------")
    print ("Mean score : %d" % mean(results))
    print ("Farkel %%   : %d%%" % (sum([x == 0 for x in results]) / test_num_games * 100))
    print ("Hi-score   : %d" % max(results))

players = [Strategy1() for _ in range(4)]
result_rounds, results = game(players, output=True)

print ("\nFinal scores")
print ("------------")
print ("In %d rounds" % result_rounds)
print ("------------")
for player, score in results:
    print ("P%d %d" % (player + 1, score))