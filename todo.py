"""
TODO: This should be able to calculate more precisely the value of each move.
Someday.
"""
def expected_score(acc_score, acc_hand, strategy):
    nleft = NDICE - acc_hand

    subscores = []
    for throw in all_possible_throws(nleft):
        posmoves = moves(throw)
        if len(posmoves) > 0:
            smove = strategy.best_move
            smove_score, smove_hand, _ = smove
            if strategy.should_stop == 0:
                # Stopped
                subscores.append(acc_score + smove_score)
            elif acc_hand + len(smove_hand) == NDICE:
                # All dice have been taken, return E(game)
                subscores.append(acc_score + smove_score + 1337) # Placeholder value ... must estimate
            else:
                submove_score = expected_score(acc_score, acc_hand + len(smove_hand), strategy)
                subscores.append(submove_score)
        else:
            # Farkel
            subscores.append(0)

    return mean(subscores)