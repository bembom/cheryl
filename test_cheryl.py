from copy import copy

import pytest 

from cheryl import (Player, Game, Knows, 
                    knows, knows_cases,
                    DuplicateNamesError, InvalidStateError)

import cheryl

@pytest.fixture
def player1_told2():
    p = Player(name='0', index=1)
    p.tell((3, 2, 1, 0))

    return p

@pytest.fixture
def game():
    elems = [(0, 3, 1), (1, 4, 3), (4, 3, 1)]
    players = [Player(name='0', index=0), 
               Player(name='1', index=1),
               Player(name='2', index=2)]
    g = Game(elems, players) 

    return g

@pytest.fixture
def bigger_game():
    elems = [(0, 1, 3), (0, 5, 0), 
             (1, 2, 3), (1, 4, 2), (1, 8, 4),
             (2, 1, 6), (2, 7, 9),
             (4, 0, 2), (4, 1, 0), (4, 2, 9),
             (5, 1, 8), (5, 4, 1)
             ]

    players = [Player(name='0', index=0), 
               Player(name='1', index=1),
               Player(name='2', index=2)]
    game = Game(elems, players) 

    return game

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
    players = [Player(name='0', index=0), 
               Player(name='0', index=1),
               Player(name='2', index=2)]

    with pytest.raises(DuplicateNamesError):
        g = Game(elems, players) 

def test_game_has_solution_before_telling(game):

    game.assert_has_solution(game.elems)

def test_game_has_solution_after_telling(game):

    game.tell((0, 3, 1))
    game.assert_has_solution(game.elems)


def test_game_has_no_solution(game):

    game.tell((0, 5, 1))
    with pytest.raises(InvalidStateError):
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


def test_matches_statement_nobody_knows():

    elems = [(0, 1, 3), (0, 5, 0), 
             (1, 2, 3), (1, 4, 2), (1, 8, 4),
             (2, 1, 6), (2, 7, 9),
             (4, 0, 2), (4, 1, 0), (4, 2, 9),
             (5, 1, 8), (5, 4, 1)
             ]
    players = [Player(name='0', index=0), 
               Player(name='1', index=1),
               Player(name='2', index=2)]
    game = Game(elems, players) 

    cand = (0, 1, 3)
    teller_name = '0'

    statement = {'0': Knows.no, '1': Knows.maybe, '2': Knows.no}
    assert game.matches_statement(cand, statement, teller_name)
    
    statement = {'1': Knows.maybe, '2': Knows.no}
    assert game.matches_statement(cand, statement, teller_name)

    statement = {'0': Knows.no}
    assert game.matches_statement(cand, statement, teller_name)

    # player 0 is wrong
    statement = {'0': Knows.yes, '1': Knows.maybe, '2': Knows.no}
    assert not game.matches_statement(cand, statement, teller_name)
    
    statement = {'0': Knows.maybe, '1': Knows.maybe, '2': Knows.no}
    assert not game.matches_statement(cand, statement, teller_name)

    # player 1 is wrong
    statement = {'0': Knows.no, '1': Knows.yes, '2': Knows.no}
    assert not game.matches_statement(cand, statement, teller_name)

    statement = {'0': Knows.no, '1': Knows.no, '2': Knows.no}
    assert not game.matches_statement(cand, statement, teller_name)

    # player 2 is wrong
    statement = {'0': Knows.no, '1': Knows.maybe, '2': Knows.yes}
    assert not game.matches_statement(cand, statement, teller_name)

    statement = {'0': Knows.no, '1': Knows.maybe, '2': Knows.maybe}
    assert not game.matches_statement(cand, statement, teller_name)

    # player 1 is wrong
    statement = {'1': Knows.yes, '2': Knows.no}
    assert not game.matches_statement(cand, statement, teller_name)

    statement = {'1': Knows.no, '2': Knows.no}
    assert not game.matches_statement(cand, statement, teller_name)

    # player 2 is wrong
    statement = {'1': Knows.maybe, '2': Knows.yes}
    assert not game.matches_statement(cand, statement, teller_name)

    statement = {'1': Knows.maybe, '2': Knows.maybe}
    assert not game.matches_statement(cand, statement, teller_name)

    # player 0 is wrong
    statement = {'0': Knows.yes}
    assert not game.matches_statement(cand, statement, teller_name)

    statement = {'0': Knows.maybe}
    assert not game.matches_statement(cand, statement, teller_name)


def test_matches_statement_somebody_knows():

    elems = [(0, 1, 3), (0, 5, 0), 
             (1, 2, 3), (1, 4, 2), (1, 8, 4),
             (2, 1, 6), 
             (4, 0, 2), (4, 1, 0), (4, 2, 9),
             (5, 1, 8), (5, 4, 1)
             ]
    players = [Player(name='0', index=0), 
               Player(name='1', index=1),
               Player(name='2', index=2)]
    game = Game(elems, players) 

    cand = (2, 1, 6)
    teller_name = '0' 

    statement = {'0': Knows.yes, '1': Knows.no, '2': Knows.yes}
    assert game.matches_statement(cand, statement, teller_name)

    statement = {'1': Knows.no, '2': Knows.yes}
    assert game.matches_statement(cand, statement, teller_name)

    statement = {'2': Knows.yes}
    assert game.matches_statement(cand, statement, teller_name)

    # player 0 is wrong
    statement = {'0': Knows.maybe, '1': Knows.no, '2': Knows.yes}
    assert not game.matches_statement(cand, statement, teller_name)

    statement = {'0': Knows.no, '1': Knows.no, '2': Knows.yes}
    assert not game.matches_statement(cand, statement, teller_name)

    # player 1 is wrong
    statement = {'0': Knows.yes, '1': Knows.yes, '2': Knows.yes}
    assert not game.matches_statement(cand, statement, teller_name)

    statement = {'0': Knows.yes, '1': Knows.maybe, '2': Knows.yes}
    assert not game.matches_statement(cand, statement, teller_name)

    # player 2 is wrong
    statement = {'0': Knows.yes, '1': Knows.no, '2': Knows.maybe}
    assert not game.matches_statement(cand, statement, teller_name)
    
    statement = {'0': Knows.yes, '1': Knows.no, '2': Knows.no}
    assert not game.matches_statement(cand, statement, teller_name)

    # all wrong
    statement = {'0': Knows.no, '1': Knows.yes, '2': Knows.no}
    assert not game.matches_statement(cand, statement, teller_name)

    # player 1 is wrong
    statement = {'1': Knows.yes, '2': Knows.yes}
    assert not game.matches_statement(cand, statement, teller_name)

    statement = {'1': Knows.maybe, '2': Knows.yes}
    assert not game.matches_statement(cand, statement, teller_name)

    # player 2 is wrong
    statement = {'1': Knows.no, '2': Knows.maybe}
    assert not game.matches_statement(cand, statement, teller_name)

    statement = {'1': Knows.no, '2': Knows.no}
    assert not game.matches_statement(cand, statement, teller_name)

    # player 2 is wrong
    statement = {'2': Knows.maybe}
    assert not game.matches_statement(cand, statement, teller_name)

    statement = {'2': Knows.no}
    assert not game.matches_statement(cand, statement, teller_name)


def test_filter_elems_empty(bigger_game):

    teller_name = '0' 
    statement = {'0': Knows.yes}

    with pytest.raises(InvalidStateError):
        bigger_game.filter_elems(statement, teller_name)

def test_filter_elems_subset(bigger_game):

    teller_name = '1'
    statement = {'1': Knows.yes}
    bigger_game.filter_elems(statement, teller_name)
    exp =[(4, 0, 2), (0, 5, 0), (2, 7, 9), (1, 8, 4)] 
    assert bigger_game.elems == set(exp)

def test_filter_elems_all(bigger_game):

    all_elems = copy(bigger_game.elems)
    teller_name = '0'
    statement = {'0': Knows.no}
    bigger_game.filter_elems(statement, teller_name)
    assert bigger_game.elems == set(all_elems)
    




