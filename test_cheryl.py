from copy import copy
import random

import pytest 

from cheryl import (Player, Game, Knows, Statement,
                    knows, knows_cases, find_game, sample_elems,
                    BadPlayerNamesError, InvalidStatementError, 
                    NoGameFoundError, NoSolutionError, TooManyTriesError)


@pytest.fixture
def player1_told2():
    p = Player(name='0', index=1)
    p.tell((3, 2, 1, 0))

    return p

@pytest.fixture
def game():
    elems = [(0, 3, 1), (1, 4, 3), (4, 3, 1)]
    g = Game(elems) 

    return g

@pytest.fixture
def bigger_game():
    elems = [(0, 1, 3), (0, 5, 0), 
             (1, 2, 3), (1, 4, 2), (1, 8, 4),
             (2, 1, 6), (2, 7, 9),
             (4, 0, 2), (4, 1, 0), (4, 2, 9),
             (5, 1, 8), (5, 4, 1)
             ]

    game = Game(elems) 

    return game

@pytest.fixture
def elems():
    elems = [(0, 1, 3), (0, 5, 0), 
             (1, 2, 3), (1, 4, 2), (1, 8, 4),
             (2, 1, 6), (2, 7, 9),
             (4, 0, 2), (4, 1, 0), (4, 2, 9),
             (5, 1, 8), (5, 4, 1)
             ]
    return elems

@pytest.fixture
def solution_elems():
    elems = [(1935, 3, 18), (1932, 3, 17), (1938, 12, 12), (1936, 7, 14),
             (1934, 11, 15), (1938, 8, 15), (1935, 7, 16), (1938, 2, 10),
             (1932, 1, 10), (1934, 10, 17)]
    return elems

def test_original_game():
    """The original game from Singapore"""

    elems = [
        (5, 15), (5, 16), (5, 19),
        (6, 17), (6, 18),
        (7, 14), (7, 16),
        (8, 14), (8, 15), (8, 17)
    ]

    g = Game(elems)

    statement1 = Statement(
            author='0', 
            conditions={'0': Knows.no, '1': Knows.no}
            )
    g.filter(statement1)
    assert g.elems ==set([(7, 14), (7, 16), (8, 14), (8, 15), (8, 17)])

    statement2 = Statement(
            author='1', 
            conditions={'1': Knows.yes}
            )
    g.filter(statement2)
    assert g.elems == set([(7, 16), (8, 15), (8, 17)])

    statement3 = Statement(
            author='0', 
            conditions={'0': Knows.yes}
            )
    g.filter(statement3)
    assert g.elems == set([(7, 16)])


def test_original_game_filter_chain():

    elems = [
        (5, 15), (5, 16), (5, 19),
        (6, 17), (6, 18),
        (7, 14), (7, 16),
        (8, 14), (8, 15), (8, 17)
    ]

    g = Game(elems)

    statement1 = Statement(
            author='0', 
            conditions={'0': Knows.no, '1': Knows.no}
            )
    statement2 = Statement(
            author='1', 
            conditions={'1': Knows.yes}
            )
    statement3 = Statement(
            author='0', 
            conditions={'0': Knows.yes}
            )

    g.filter_chain([statement1, statement2, statement3])
    assert g.elems == set([(7, 16)])

def test_player_would_know_yes(player1_told2, elems):

    obs = player1_told2.would_know(truths=[(2, 7, 9)],
                                   elems=elems)
    assert obs == Knows.yes

def test_player_would_know_no(player1_told2, elems):

    obs = player1_told2.would_know(truths=[(2, 7, 9)],
                                   elems=elems)
    assert obs == Knows.yes

def test_player_has_solution(player1_told2):

    assert player1_told2.has_solution([(0, 2, 2), (2, 1, 4)])

def test_player_has_no_solution(player1_told2):

    assert not player1_told2.has_solution([(0, 1, 2), (3, 1, 4)])

def test_player_not_told():
    p = Player(name='0', index=0)

    assert p.told is None

def test_player_told0(player1_told2):
    p = Player(name='1', index=1)
    p.tell((3, 0, 1, 0))

    assert p.told == 0 

def test_player_told2(player1_told2):

    assert player1_told2.told == 2 

def test_matches_not_told():
    p = Player(name='1', index=1)

    assert p.matches((3, 2, 1, 0))
    
def test_matches_told_and_matches(player1_told2):

    assert player1_told2.matches((4, 2, 0, 1))

def test_matches_told_and_no_match(player1_told2):

    assert not player1_told2.matches((2, 3, 0, 1))

def test_get_compatible(player1_told2):

    elems=[(3, 1, 1), (4, 4, 2), (5, 1, 3), (1, 2, 0)]
    obs = player1_told2.get_compatible(truth=elems[0], elems=elems)

    assert obs == [(3, 1, 1), (5, 1, 3)]

def test_format_no_match(player1_told2):

    assert ' 4 4 4 4 ' == player1_told2._format((4, 4, 4, 4))

def test_format_match(player1_told2):

    assert '|4 2 4 4|' == player1_told2._format((4, 2, 4, 4))

def test_view_sort(player1_told2):

    obs = player1_told2.view([(4, 4, 4, 4), (4, 2, 4, 4)])
    assert ['|4 2 4 4|', ' 4 4 4 4 '] == obs 

def test_view_no_sort(player1_told2):

    obs = player1_told2.view([(4, 2, 4, 4), (4, 4, 4, 4)])
    assert ['|4 2 4 4|', ' 4 4 4 4 '] == obs 

def test_game_duplicate_names_error():

    elems = [(0, 3, 1), (1, 4, 3), (4, 3, 1)]

    with pytest.raises(BadPlayerNamesError):
        g = Game(elems, player_names=['jim', 'jim', 'jack']) 

def test_game_player_names_wrong_length():

    elems = [(0, 3, 1), (1, 4, 3), (4, 3, 1)]

    with pytest.raises(BadPlayerNamesError):
        g = Game(elems, player_names=['jim', 'jack']) 

def test_game_has_solution_before_telling(game):

    game.assert_has_solution(game.elems)

def test_game_has_solution_after_telling(game):

    game.tell((0, 3, 1))
    game.assert_has_solution(game.elems)


def test_game_has_no_solution(game):

    game.tell((0, 5, 1))
    with pytest.raises(NoSolutionError):
        game.assert_has_solution(game.elems)

def test_game_get_player(game):

    player = game.get_player('1')

    assert player.name == '1'
    assert player.index == 1
    assert player.told is None


def test_game_remove_one(game):

    game.remove([(0, 3, 1)])

    assert game.elems == set([(1, 4, 3), (4, 3, 1)])

def test_game_remove_two(game):

    game.remove([(0, 3, 1), (4, 3, 1)])

    assert game.elems == set([(1, 4, 3)])

def test_game_tell(game):

    game.tell((1, 4, 3))

    assert game.players[0].told == 1
    assert game.players[1].told == 4
    assert game.players[2].told == 3

def test_game_n_solutions_0(bigger_game):
    statements = [Statement(author='0', conditions={'0': Knows.yes})]
    assert bigger_game.n_solutions(statements) == 0
    

def test_game_n_solutions_1(bigger_game):
    statements = [Statement(author='1', 
                            conditions={'1': Knows.yes, '2': Knows.yes})]
    assert bigger_game.n_solutions(statements) == 1


def test_game_n_solutions_many(bigger_game):
    statements = [Statement(author='0', 
                            conditions={'0': Knows.no, '1': Knows.maybe})]
    assert bigger_game.n_solutions(statements) == 10 

def test_game_n_solutions_two_statements(bigger_game):
    statements = [Statement(author='0', conditions={'0': Knows.no}),
                  Statement(author='1', conditions={'1': Knows.no}),
                  Statement(author='2', conditions={'2': Knows.no})]
    assert bigger_game.n_solutions(statements) == 2

def test_game_n_solutions_no_side_effects(bigger_game):
    n_elems = len(bigger_game.elems)
    statements = [Statement(author='0', conditions={'0': Knows.no})]
    assert bigger_game.n_solutions(statements) == 12 

    assert len(bigger_game.elems) == n_elems

def test_knows_yes():

    assert knows([(1, 3, 4)]) == Knows.yes
    
def test_knows_no():

    assert knows([(1, 3, 4), (4, 3, 2)]) == Knows.no

def test_knows_cases_yes():

    assert knows_cases([Knows.yes, Knows.yes]) == Knows.yes

def test_knows_cases_no():

    assert knows_cases([Knows.no, Knows.no]) == Knows.no
    
def test_knows_cases_maybe():

    assert knows_cases([Knows.yes, Knows.no]) == Knows.maybe

def test_filter_empty(bigger_game):

    author = '0' 
    conditions = {'0': Knows.yes}

    with pytest.raises(NoSolutionError):
        bigger_game.filter(Statement(author, conditions))

def test_filter_subset(bigger_game):

    author = '1'
    conditions = {'1': Knows.yes}
    bigger_game.filter(Statement(author, conditions))
    exp =[(4, 0, 2), (0, 5, 0), (2, 7, 9), (1, 8, 4)] 
    assert bigger_game.elems == set(exp)

def test_filter_all(bigger_game):

    all_elems = copy(bigger_game.elems)
    author = '0'
    conditions = {'0': Knows.no}
    bigger_game.filter(Statement(author, conditions))
    assert bigger_game.elems == set(all_elems)
    

def test_game_get_solution(solution_elems):

    game = Game(solution_elems)

    statements = [Statement(author='0', conditions={'0': Knows.yes}),
                  Statement(author='1', conditions={'1': Knows.yes}),
                  Statement(author='2', conditions={'2': Knows.yes})]

    assert game.get_solution(statements) == (1936, 7, 14)



def test_statement_author_in_tuple():

    author = '0' 
    conditions = {('0', '1', '2'): Knows.maybe}
    with pytest.raises(InvalidStatementError):
        assert Statement(author, conditions)


def test_statement_true_for_nobody_knows():

    elems = [(0, 1, 3), (0, 5, 0), 
             (1, 2, 3), (1, 4, 2), (1, 8, 4),
             (2, 1, 6), (2, 7, 9),
             (4, 0, 2), (4, 1, 0), (4, 2, 9),
             (5, 1, 8), (5, 4, 1)
             ]
    game = Game(elems) 

    cand = (0, 1, 3)
    teller_name = '0'

    conditions = {'0': Knows.no, '1': Knows.maybe, '2': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert statement.true_for(cand, game)
    
    conditions = {'1': Knows.maybe, '2': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert statement.true_for(cand, game)

    conditions = {'0': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert statement.true_for(cand, game)

    # player 0 is wrong
    conditions = {'0': Knows.yes, '1': Knows.maybe, '2': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)
    
    conditions = {'0': Knows.maybe, '1': Knows.maybe, '2': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    # player 1 is wrong
    conditions = {'0': Knows.no, '1': Knows.yes, '2': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    conditions = {'0': Knows.no, '1': Knows.no, '2': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    # player 2 is wrong
    conditions = {'0': Knows.no, '1': Knows.maybe, '2': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    conditions = {'0': Knows.no, '1': Knows.maybe, '2': Knows.maybe}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    # player 1 is wrong
    conditions = {'1': Knows.yes, '2': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    conditions = {'1': Knows.no, '2': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    # player 2 is wrong
    conditions = {'1': Knows.maybe, '2': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    conditions = {'1': Knows.maybe, '2': Knows.maybe}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    # player 0 is wrong
    conditions = {'0': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    conditions = {'0': Knows.maybe}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)


def test_statement_true_for_somebody_knows():

    elems = [(0, 1, 3), (0, 5, 0), 
             (1, 2, 3), (1, 4, 2), (1, 8, 4),
             (2, 1, 6), (4, 0, 2), (4, 1, 0), (4, 2, 9),
             (5, 1, 8), (5, 4, 1)
             ]

    game = Game(elems) 

    cand = (2, 1, 6)

    conditions = {'0': Knows.yes, '1': Knows.no, '2': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert statement.true_for(cand, game)

    conditions = {'1': Knows.no, '2': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert statement.true_for(cand, game)

    conditions = {'2': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert statement.true_for(cand, game)

    # player 0 is wrong
    conditions = {'0': Knows.maybe, '1': Knows.no, '2': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    conditions = {'0': Knows.no, '1': Knows.no, '2': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    # player 1 is wrong
    conditions = {'0': Knows.yes, '1': Knows.yes, '2': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    conditions = {'0': Knows.yes, '1': Knows.maybe, '2': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    # player 2 is wrong
    conditions = {'0': Knows.yes, '1': Knows.no, '2': Knows.maybe}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)
    
    conditions = {'0': Knows.yes, '1': Knows.no, '2': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    # all wrong
    conditions = {'0': Knows.no, '1': Knows.yes, '2': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    # player 1 is wrong
    conditions = {'1': Knows.yes, '2': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    conditions = {'1': Knows.maybe, '2': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    # player 2 is wrong
    conditions = {'1': Knows.no, '2': Knows.maybe}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    conditions = {'1': Knows.no, '2': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    # player 2 is wrong
    conditions = {'2': Knows.maybe}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    conditions = {'2': Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

def test_matches_statement_at_least_one():

    elems = [(0, 1, 3), (0, 5, 0), 
             (1, 2, 3), (1, 4, 2), (1, 8, 4),
             (2, 1, 6), 
             (4, 0, 2), (4, 1, 0), (4, 2, 9),
             (5, 1, 8), (5, 4, 1)
             ]
    game = Game(elems) 

    cand = (2, 1, 6)
    teller_name = '0' 

    conditions = {'0': Knows.yes, '1': Knows.no, '2': Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert statement.true_for(cand, game)

    conditions = {'0': Knows.yes, ('1', '2'): Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert statement.true_for(cand, game)

    conditions = {'0': Knows.yes, ('1', '2'): Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert statement.true_for(cand, game)

    conditions = {'0': Knows.yes, ('1', '2'): Knows.maybe}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)


def test_matches_statement_at_least_one_maybe():

    elems = [(0, 1, 3), (0, 5, 0), 
             (1, 2, 3), (1, 4, 2), (1, 8, 4),
             (2, 1, 6), 
             (4, 0, 2), (4, 1, 0), (4, 2, 9),
             (5, 1, 8), (5, 4, 1)
             ]
    game = Game(elems) 

    cand = (4, 1, 0)
    teller_name = '0' 

    conditions = {'0': Knows.no, '1': Knows.maybe, '2': Knows.maybe}
    statement = Statement(author='0', conditions=conditions)
    assert statement.true_for(cand, game)

    conditions = {'0': Knows.no, ('1', '2'):  Knows.maybe}
    statement = Statement(author='0', conditions=conditions)
    assert statement.true_for(cand, game)

    conditions = {'0': Knows.no, ('1', '2'):  Knows.no}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

    conditions = {'0': Knows.no, ('1', '2'):  Knows.yes}
    statement = Statement(author='0', conditions=conditions)
    assert not statement.true_for(cand, game)

def test_find_game_succeeds(solution_elems):

    random.seed(123)

    domains = [range(1930, 1940), range(1, 13), range(10, 20)]
    n_elems = 10
    statements = [Statement(author='0', conditions={'0': Knows.yes}),
                  Statement(author='1', conditions={'1': Knows.yes}),
                  Statement(author='2', conditions={'2': Knows.yes})]
    game = find_game(domains, n_elems, statements, n_trys=100)

    assert game.elems == set(solution_elems)

    assert game.get_solution(statements) == (1936, 7, 14)
     

def test_find_game_fails():

    random.seed(123)

    domains = [range(1930, 1940), range(1, 13), range(10, 20)]
    n_elems = 10
    statements = [Statement(author='0', conditions={'0': Knows.no}),
                  Statement(author='1', conditions={'1': Knows.no}),
                  Statement(author='2', conditions={'2': Knows.no})]

    with pytest.raises(NoGameFoundError):
        game = find_game(domains, n_elems, statements, n_trys=100)

def test_sample_elems_fails():

    domains = [[0, 1], ['a', 'b']]
    with pytest.raises(TooManyTriesError):
        sample_elems(domains, 5)


