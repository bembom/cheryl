from enum import Enum
from collections import Counter
from functools import partial
from operator import itemgetter

import numpy as np
import pandas as pd


class Player(object):

    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.told = None

    def tell(self, elem):
        self.told = elem[self.index]

    def view(self, elems):
        sorted_elems = sorted(elems, key=itemgetter(self.index))
        return [self._format(x) for x in sorted_elems]

    def matches(self, elem):
        if self.told is None:
            return True

        return elem[self.index] == self.told

    def has_solution(self, elems):

        if not elems:
            return False

        if self.told is None:
            return True

        possible = [e for e in elems if e[self.index] == self.told]
        return len(possible) > 0 

    def get_compatible(self, truth, elems):
        """Given a possible truth, get all elements that would be compatible

        Parameters
        ----------
        truth: tuple
            The element to be considered as the possible truth.
        elems: list of tuples
            All elements that are still in play.

        This is from the perspective of another player, that is, it ignores the
        specific information the player has been told and only makes use of
        knowing which part of the tuple the player has been told.
        """
        return [e for e in elems if e[self.index] == truth[self.index]]

    def would_know(self, truths, elems):
        """Given a list of possible truths, would the player know the solution? 

        This is from the perspective of another player, that is, it ignores the
        specific information the player has been told and only makes use of
        knowing which part of the tuple the player has been told.

        Parameters
        ----------
        truths: list of tuples
            The elements that will be considered as possible values for the
            truth.
        elems: list of tuples
            All elements that are still in play.

        """

        cases = []
        for elem in truths:
            compatibles = self.get_compatible(truth=elem, elems=elems)
            cases.append(knows(compatibles))

        return knows_cases(cases)


    def _format(self, elem):
        border = '|' if self.matches(elem) else ' '

        return '{border}{data}{border}'.format(
            border=border,
            data=' '.join([str(e) for e in elem])
            )

    def __repr__(self):
        return "Player(name='{name}', index={index}, told={told})".format(
                name=self.name,
                index=self.index, 
                told=self.told)


class Game(object):

    def __init__(self, elems, players):
        self.elems = set(elems)

        names = [player.name for player in players]
        if len(names) != len(set(names)):
            raise DuplicateNamesError()

        self.players = players

    def remove(self, to_remove):
        self.elems = self.elems.difference(set(to_remove))

    def tell(self, elem):

        for player in self.players:
            player.tell(elem)

    def get_player(self, name):
        for player in self.players:
            if player.name == name:
                return player

    def assert_has_solution(self, elems):
        """

        Raises
        ------
        NoSolutionError
        """

        for player in self.players:
            if not player.has_solution(elems):
                msg = "No solution for player {}".format(player.name)   
                raise NoSolutionError(msg)


    def filter(self, statement, inplace=True):
        """

        Parameters
        ----------
        statement: Statement
            The statement to filter the elements by.
        inplace: bool
            Should the Game object be updated in place with the new, filtered
            elements? Otherwise return a new Game object based on the filtered
            elements.

        Returns
        -------
        None if inplace is True, a Game object otherwise.

        Raises
        ------
        NoSolutionError

        """

        filtered = []
        for elem in self.elems:
            if statement.true_for(cand=elem, game=self):
                filtered.append(elem)

        self.assert_has_solution(filtered)

        if inplace:
            self.elems =  set(filtered)
        else:
            return Game(elems=filtered, players=self.players)


    def filter_chain(self, statements, inplace=True, trace=False):
        """

        Parameters
        ----------
        statements: list of Statement
            The statements to filter the elements by, applied one after
            another.            
        inplace: bool
            Should the Game object be updated in place with the new, filtered
            elements? Otherwise return a new Game object based on the filtered
            elements.

        Returns
        -------
        None if inplace is True, a Game object otherwise.

        Raises
        ------
        NoSolutionError

        """

        if inplace:
            for statement in statements:
                self.filter(statement, inplace=True)
                if trace:
                    print(repr(self))
        
        else:
            game = self 
            for statement in statements:
                game = game.filter(statement, inplace=False)
                if trace:
                    print(repr(game))

            return game

    def n_solutions(self, statements):
        """How many elements are compatible with a list of Statements?

        Parameters
        ----------
        statements: list of Statement
            The statements to filter the elements by, applied one after
            another.            

        """

        try:
            game = self.filter_chain(statements, inplace=False)
            n_solutions = len(game.elems)
        except NoSolutionError as e:
            n_solutions = 0

        return n_solutions

    def get_solution(self, statements, trace=False):

        game = self.filter_chain(statements, inplace=False, trace=trace)
        if len(game.elems) > 1:
            msg = "Found {} solutions".format(len(game.elems))
            raise MultipleSolutionsError(msg)

        return list(game.elems)[0]


    def __repr__(self):

        views = []
        for player in self.players:
            views.append(player.view(self.elems))

        frame = pd.DataFrame(views).T
        col_names = []
        for player in self.players:
            col_name = '{}: {}={}'.format(player.name, player.index, player.told)
            col_names.append(col_name)
        frame.columns = col_names

        return repr(frame)


class Statement(object):

    def __init__(self, author, conditions):
        """
        author: str
            The name of the player who is making this statement.
        conditions: dict str -> Knows
            Does each player know, not know, or maybe know? A dictionary mapping
            player names to Knows enum values. If a player's name does not appear
            in this dict, no statement about that player's knowledge is made.
            If a key is a tuple of strings, the given knowledge state applies
            to at least one of the players specified in the tuple.
        """
        for who, condition in conditions.items():

            if not isinstance(who, tuple):
                continue

            for name in who:
                if name == author:
                    msg = "Author cannot be part of tuple"
                    raise InvalidStatementError(msg)

        self.author = author
        self.conditions = conditions

    def true_for(self, cand, game):
        """

        Parameters
        ----------
        cand: tuple
            The candidate element for which to evaluate the statement.
        game: Game
            The game in the context of which the statement is to be evaluated.

        Returns
        -------
        bool
        """

        author  = game.get_player(self.author)
        author_compatible = author.get_compatible(truth=cand, elems=game.elems)

        if (author.name in self.conditions and
            knows(author_compatible) != self.conditions[author.name]):
            return False

        for who, expected in self.conditions.items():

            # already dealt with condition on author
            if who == author:
                continue

            # in the case of multiple players, the statement has to be true for
            # at least one of them
            if isinstance(who, tuple):

                found_match = False
                for name in who:

                    player_knowledge = game.get_player(name).would_know(
                            truths=author_compatible, 
                            elems=game.elems
                            ) 
                    if player_knowledge == expected:
                        found_match = True

                if not found_match:
                    return False

            else:

                player = game.get_player(who)
                player_knowledge = player.would_know(truths=author_compatible, 
                                                    elems=game.elems) 
                if player_knowledge != self.conditions[who]:
                    return False

        return True

    def __repr__(self):
        return 'Statement(author={author}, conditions={conditions}'.format(
                author=self.author, 
                conditions=repr(self.conditions)
                )


    n_elems = 20
    domains = [range(10), range(10, 20), range(20, 30)]

def sample_elems(domains, n_elems, max_tries=100):
    """
    >>> np.random.seed(123)
    >>> domains = [range(10), range(10, 20), range(20, 30)]
    >>> sample_elems(domains, 5)
    [(1, 10, 29), (2, 16, 20), (2, 19, 29), (3, 11, 23), (6, 11, 20)]
    >>> domains = [list('abcdef'), range(6)]
    >>> sample_elems(domains, 3)
    [('a', 1), ('e', 4), ('f', 0)]
    >>> domains = [[0, 1], ['a', 'b']]
    >>> sample_elems(domains, 4)
    [(0, 'a'), (0, 'b'), (1, 'a'), (1, 'b')]
    """

    sample = []
    n_unique = 0
    n_tries = 0
    while n_unique != n_elems:

        n_tries += 1
        if n_tries > max_tries:
            raise TooManyTriesError()

        choose = partial(np.random.choice, size=n_elems - n_unique) 
        elems = map(choose, domains)
        sample.extend(list(zip(*elems)))

        n_unique = len(set(sample))

    return sorted(list(set(sample)))

    
def players_from_domains(domains):
    """Generate one player for each domain 

    >>> domains = [range(10), list('abcdef')]
    >>> players_from_domains(domains)
    [Player(name='0', index=0, told=None), Player(name='1', index=1, told=None)]
    """
    n_players = len(domains)
    return [Player(name=str(i), index=i) for i in range(n_players)]


def find_game(domains, n_elems, statements, n_trys):

    n_solutions = []
    for _ in range(n_trys):
        elems = sample_elems(domains, n_elems)
        players = players_from_domains(domains)
        game = Game(elems, players)

        my_n_solutions = game.n_solutions(statements)
        if my_n_solutions == 1:
            return game

        n_solutions.append(my_n_solutions)

    msg = repr(Counter(n_solutions))
    raise NoGameFoundError(msg)




class Knows(Enum):

    no = -1
    maybe = 0
    yes = 1


def knows(compatible):
    """Given a list of elements still compatible, does a player know?

    Parameters
    ----------
    compatible: list
        The elements that are still compatible with a players current
        knowledge.

    Returns
    -------
    Knows enum

    >>> knows([(1, 2, 3), (4, 5, 6)])
    <Knows.no: -1>
    >>> knows([(1, 2, 3)])
    <Knows.yes: 1>
    """
    return Knows.yes if len(compatible) == 1 else Knows.no


def knows_cases(cases):
    """

    >>> knows_cases([Knows.yes, Knows.yes, Knows.yes])
    <Knows.yes: 1>
    >>> knows_cases([Knows.yes, Knows.no, Knows.yes])
    <Knows.maybe: 0>
    >>> knows_cases([Knows.maybe, Knows.no, Knows.yes])
    <Knows.maybe: 0>
    >>> knows_cases([Knows.no, Knows.no, Knows.no])
    <Knows.no: -1>
    """

    assert all([isinstance(case, Knows) for case in cases])

    if all([case == Knows.yes for case in cases]):
        return Knows.yes
    elif all([case == Knows.no for case in cases]):
        return Knows.no
    else:
        return Knows.maybe



class Error(Exception):
    pass

class DuplicateNamesError(Error):
    """Two Player objects passed to Game() have the same name"""
    pass

class NoSolutionError(Error):
    """A Game has reached a state without a solution for at least one Player"""
    pass

class InvalidStatementError(Error):
    """A Statement cannot be created because it is invalid"""
    pass

class NoGameFoundError(Error):
    """Could not find a feasible game for the given Statements"""
    pass

class TooManyTriesError(Error):
    """Too many tries in finding a sample of elements"""
    pass
