import itertools
import random

NDICE = 6
DICEMAX = 6

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def category(hand):
    rval = []
    rcnt = []
    for v in hand:
        if v not in rval:
            rval.append(v)
            num_v_in_hand = sum([item == v for item in hand])
            rcnt.append(num_v_in_hand)
    r = zip(rval, rcnt)
    return sorted(r, key=lambda vc: vc[1], reverse=True)

def moves(throw):

    cat = category(throw)
    counts = [cnt for v, cnt in cat]
    hival, hicnt = cat[0]

    moves = []

    def add_move(score, hand, name):     
        hand = list(sorted(hand))
        insert = True
        remove = None
        for move in moves:
            move_score, move_hand, _ = move
            if move_hand == hand:
                if move_score >= score:
                    # The existing move is better, we won't insert
                    insert = False
                else:
                    # The existing move should be removed as it is sucks
                    remove = move

        if remove is not None:
            moves.remove(remove)
        if insert:
            moves.append((score, hand, name))

    if len(throw) == NDICE:
        if len(cat) == 1:
            # Straight
            add_move(3000, throw, 'Full Straight')
        if len(cat) == NDICE:
            # Full Street
            add_move(1500, throw, 'Full Street')
        elif len(cat) == 2:
            if hicnt == 3:
                # Two Triplets
                add_move(2500, throw, 'Two Triplets')
            elif hicnt == 4:
                # 4 of a Kind + Pair
                add_move(1500, throw, '4 of a Kind and a Pair')
        elif len(cat) == 3 and counts[0] == 2 and counts[1] == 2:
            # Three Pairs
            add_move(1500, throw, 'Three Pairs')

    def add_move_and_residuals(base_move = (0, [], 'Residuals')):
        
        def calculate_residual_score(combination):
            def score(face):
                if face == 1:
                    return 100
                elif face == 5:
                    return 50
                else:
                    return 0
            return sum([score(face) for face in combination])

        base_score, base_hand, base_name = base_move
        if len(base_hand) > 0:
            add_move(base_score, base_hand, base_name)

        # List of 
        throw_rest = list(throw)
        for x in base_hand:
            throw_rest.remove(x)

        # Keep only 1 and 5 as those are the only ones relevant
        throw_rest = [x for x in throw_rest if x == 1 or x == 5]

        possible_throws = []
        for l in range(1, len(throw_rest) + 1):
            possible_combinations = [list(x) for x in itertools.combinations(throw_rest, l)]
            possible_throws.extend(possible_combinations)

        for residual_throw in possible_throws:
            residual_score = calculate_residual_score(residual_throw)
            add_move(base_score + residual_score, base_hand + residual_throw, base_name)

    if hicnt == 5:
        # Five of a Kind
        add_move_and_residuals((1500, 5 * [hival], 'Five of a Kind'))
    elif hicnt == 4:
        # Four of a Kind
        add_move_and_residuals((1000, 4 * [hival], 'Four of a Kind'))

    if hicnt == 3:
        if hival == 1:
            add_move_and_residuals((300, 3 * [1], 'Three 1\'s'))
        elif hival == 2:
            add_move_and_residuals((200, 3 * [2], 'Three 2\'s'))
        elif hival == 3:
            add_move_and_residuals((300, 3 * [3], 'Three 3\'s'))
        elif hival == 4:
            add_move_and_residuals((400, 3 * [4], 'Three 4\'s'))
        elif hival == 5:
            add_move_and_residuals((500, 3 * [5], 'Three 5\'s'))
        elif hival == 6:
            add_move_and_residuals((600, 3 * [6], 'Three 6\'s'))

    # Add residual scores
    add_move_and_residuals()

    return sorted(moves, key=lambda move: move[0], reverse=True)

def print_move(move):
    score, hand, name = move
    print ("%s (%d) (grab %s)" % (name, score, hand))

def print_moves(moves):
    if len(moves) > 0:
        for move in moves:
            print_move(move)
    else:
        print("Farkel!")

class IStrategy:
    
    def best_move(self, kept, moves, is_stopping=False):
        raise NotImplementedError()

    def should_stop(self, kept, total_score, best_move):
        raise NotImplementedError()

    def should_restart(self):
        raise NotImplementedError()

    def should_take_over(self, kept, score):
        raise NotImplementedError()

class Strategy1(IStrategy):
    
    DICE_WORTH = 160
    TAKE_OVER_THRESHOLD = 800
    HISCORE = 9999

    TH_MIN_FARKEL_CHANCE = .05
    
    def best_move(self, kept, possible_moves, is_stopping=False):
        moves2 = [(move, self._points(kept, move, is_stopping)) for move in possible_moves]

        best_move, _ = sorted(moves2, key=lambda x: x[1], reverse=True)[0]
        return best_move

    def should_stop(self, kept, total_score, move):
        return farkel_chance(NDICE - len(kept)) > self.TH_MIN_FARKEL_CHANCE

    def should_restart(self):
        return True 

    def should_take_over(self, kept, score):
        return score > self.TAKE_OVER_THRESHOLD
        
    def _points(self, kept, move, is_stopping=False):
        score, hand, _ = move
        if len(kept) + len(hand) >= NDICE:
            return self.HISCORE

        if not is_stopping:
            return score + ((NDICE - len(hand)) * self.DICE_WORTH) 
        else:
            return score
        
def memoize(f):
    memo = {}
    def helper(x):
        if x not in memo:
            memo[x] = f(x)
        return memo[x]
    return helper

@memoize
def all_possible_throws(n=NDICE):
    if n == 0:
        return [[]]
    suffixes = all_possible_throws(n - 1)
    result = []
    for d in range(1, DICEMAX + 1):
        result.extend([[d] + suffix for suffix in list(suffixes)])
    return result
    
def farkel_chance(ndice=NDICE, use_cache=True):
    if not use_cache:
        all_throws = all_possible_throws(ndice)
        num_farkels = 0
        for throw in all_throws:
            farkel = len(moves(throw)) == 0
            if farkel:
                num_farkels += 1
        return num_farkels / len(all_throws)
    else:
        cache = [4 / 6, 16 / 36, 60 / 216, 204 / 1296, 600 / 7776, 1080 / 46656]
        return cache[ndice - 1]
        
def throw_dices(ndice=NDICE):
    return [random.randint(0, DICEMAX - 1) + 1 for _ in range(0, ndice)]

def play(strategy, output=False, initial_score=0, initial_kept=[]):
    kept = initial_kept
    score = initial_score
    while True:
        throw = throw_dices(NDICE - len(kept))
        if output:
            print ("Threw " + str(throw))
        possible_moves = moves(throw)

        if len(possible_moves) == 0:
            if output:
                print ("Farkel :(")
            return (0, [])

        move = strategy.best_move(kept, possible_moves)
        move_score, move_hand, name = move

        if len(kept) + len(move_hand) == NDICE:
            score += move_score
            kept.extend(move_hand)
            if output:
                print ("Played %s, have %s -- score: %d" % (name, str(kept), score))
                print ("Move leads to possible restart")

            will_restart = strategy.should_restart()

            if will_restart:
                if output:
                    print ("Restart")
                restart_score, restart_kept = play(strategy,
                    initial_score=score,
                    initial_kept=[],
                    output=output)
                if restart_score == 0:
                    return (0, restart_kept)
                else:
                    return (restart_score, restart_kept)
            else:
                if output:
                    print ("Won't restart")
                return (score, kept)
        else:
            if strategy.should_stop(kept, score, move):
                # Recalculating best move
                move_score, move_hand, _ = strategy.best_move(
                    kept,
                    possible_moves,
                    is_stopping=True)

                kept.extend(move_hand)
                score += move_score
                if output:
                    print ("Played %s, have %s -- score: %d" % (name, str(kept), score))
                    print ("Stopping")

                return (score, kept)
            else:
                kept.extend(move_hand)
                score += move_score
                if output:
                    print ("Played %s, have %s -- score: %d" % (name, str(kept), score))

    return (score, kept)

def game(players, first_to_score=10000, output=False):
    num_players = len(players)
    current_scores = [0 for _ in range(num_players)]
    countdown = None
    round_count = 0

    kept = []
    score = 0
    while True:
        round_count += 1

        for i in range(num_players):
            if output:
                print ("\nPlayer %d" % (i + 1))
                print ("--------")

            if len(kept) > 0 and players[i].should_take_over(kept, score):
                # Players will take over previous left over
                # dice + score
                if output:
                    print ("Player will take over")
                score, kept = play(
                    strategy=players[i],
                    initial_score=score,
                    initial_kept=kept,
                    output=output)
            else:
                # No take over possible
                score, kept = play(
                    strategy=players[i],
                    initial_score=0,
                    initial_kept=[],
                    output=output)

            current_scores[i] += score

            if countdown is None and current_scores[i] >= first_to_score:
                print ("All other players get one extra turn")
                countdown = num_players

            if countdown is not None:
                if countdown > 0:
                    countdown -= 1
                else:
                    break

        if countdown is not None and countdown <= 0:
            break

    player_scores = [(index, score) for index, score in enumerate(current_scores)]
    player_scores_sorted = sorted(player_scores, key=lambda x: x[1], reverse=True)
    return round_count, player_scores_sorted