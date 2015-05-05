"""Classes for finding and solving puzzles like Cheryl's birthday puzzle"""

from enum import Enum
from collections import Counter
from functools import partial
from operator import itemgetter
import random


class Player(object):
    """A Player who takes part in a Game

    Attributes
    ----------
    name: str
        The name of the player
    index: int
        The index of the dimension that this player is told by Cheryl. Starts
        at zero.
    """

    def __init__(self, name, index):
        self.name = name
        self.index = index

    def get_compatible(self, truth, candidates):
        """Given a possible truth, get all candidates that would be compatible

        Parameters
        ----------
        truth: tuple
            The candidate to be considered as the possible truth.
        candidates: list of tuples
            All candidates that are still in play.

        Returns
        -------
        A list of candidates that are compatible with this possible truth.
        """
        return [e for e in candidates if e[self.index] == truth[self.index]]

    def would_know(self, truths, candidates):
        """Given a list of possible truths, would the player know the solution?

        If the player knows the solution for all given truths, then the player
        knows. If the player does not know for any given truth, the player does
        not know. Otherwise, the player maybe knows.

        Parameters
        ----------
        truths: list of tuples
            The candidates that will be considered as possible values for the
            truth.
        candidates: list of tuples
            All candidates that are still in play.

        Returns
        -------
        A Knows enum value, one of Knows.yes, Knows.maybe, and Knows.no.
        """

        cases = []
        for truth in truths:
            compatibles = self.get_compatible(truth=truth, 
                                              candidates=candidates)
            cases.append(knows(compatibles))

        return knows_cases(cases)

    def view(self, candidates):
        """Create a view of a set of candidates from this player's perspective

        Candidates are sorted by the dimension this player is told about.

        Parameters
        ----------
        candidates: list of tuples
            The candidates for which to create the view

        Returns
        -------
        A list of strings, one for each candidate.
        """
        widths = _max_widths(candidates)
        sorted_candidates = sorted(candidates, key=itemgetter(self.index))

        return [_format_candidate(cand, widths) for cand in sorted_candidates]

    def __repr__(self):
        return "Player(name='{name}', index={index})".format(
                name=self.name,
                index=self.index)


def _format_candidate(cand, widths):
    """Get a string representation of a candidate tuple

    Parameters
    ----------
    cand: tuple
        The candidate tuple
    widths: sequence
        The width for each field in the candidate tuple

    Returns
    -------
    str
    """
    assert len(cand) == len(widths)

    parts = []
    for elem, width in zip(cand, widths):
        parts.append('{0:<{1}}'.format(elem, width))
    return ' '.join(parts)


def _max_widths(candidates):
    """Get the maximum width for each element of a candidate tuple

    What is the maximum number of characters that the first element of the
    candidate tuples might need, over a list of candidate tuples? How about the
    other elements?

    Parameters
    ----------
    candidates: list of tuples
        The candidate tuples

    Returns
    -------
    A list of ints, giving the maximum width for each element.

    """
    candidate_list = list(candidates)
    widths = []
    for idx in range(len(candidate_list[0])):
        fields = map(itemgetter(idx), candidate_list)
        str_fields = map(str, fields)
        widths.append(max(map(len, str_fields)))

    return widths


class Game(object):
    """A game in which Cheryl tells players separate parts of the truth

    One Player is created for each dimension in the tuples that Cheryl
    provides.

    Attributes
    ----------
    candidates: list of tuples
        The candidates that Cheryl gives the players to choose from. These are
        tuples, with each part of the tuple being a dimension that one player
        is told about. As statements are applied to filter out candidates that
        incompatible with them, this list shrinks to contain only those that
        are still in play.
    player_names: str
        If given, these are the names of the players. If not given, players are
        named after the index of the dimension they are told about.
    """

    def __init__(self, candidates, player_names=None):

        n_players = len(candidates[0])
        self.candidates = set(candidates)

        if player_names is None:
            player_names = [str(i) for i in range(n_players)]

        elif len(player_names) != len(set(player_names)):
            msg  = "player_names cannot contain duplicates"
            raise BadPlayerNamesError(msg)

        elif len(player_names) != n_players:
            msg = "Expected {exp} names but got {obs}".format(
                    exp=n_players,
                    obs=len(player_names)
                    )
            raise BadPlayerNamesError(msg)


        self.players = [Player(n, idx) for idx, n in enumerate(player_names)]

    def get_player(self, name):
        """Get a Player instance by name"""
        for player in self.players:
            if player.name == name:
                return player

    def get_player_names(self):
        """Get the names of the players"""
        return [player.name for player in self.players]

    def filter(self, statement):
        """Filter the candidates based on a Statment about player's knowledge

        Raises a NoSolutionError if no candidates satisfy the statement.

        Parameters
        ----------
        statement: Statement
            The statement to filter the candidates by.

        Returns
        -------
        A new Game object containing only those candidates that are compatible
        with the given statement.

        Raises
        ------
        NoSolutionError
        """

        filtered = []
        for cand in self.candidates:
            if statement.true_for(cand=cand, game=self):
                filtered.append(cand)

        if not filtered:
            msg = "No candidates found that satisfy the filtering criterion"
            raise NoSolutionError(msg)

        return Game(candidates=filtered, player_names=self.get_player_names())


    def filter_chain(self, statements, trace=False):
        """Filter the candidates based on a list of Statments

        Raises a NoSolutionError if no candidates satisfy the statements.

        Parameters
        ----------
        statements: list of Statement
            The statements to filter the candidates by, applied one after
            another.
        trace: bool
            If true, print out intermediate values.

        Returns
        -------
        A new Game object containg only candidates that are compatible with the
        given Statements.

        Raises
        ------
        NoSolutionError

        """
        if trace:
            print("Before filtering:")
            print(repr(self))

        game = self
        for i, statement in enumerate(statements, 1):
            game = game.filter(statement)
            if trace:
                print("\nAfter applying statement {}:".format(i))
                print(repr(game))

        return game

    def n_solutions(self, statements):
        """How many candidates are compatible with a list of Statements?

        Parameters
        ----------
        statements: list of Statement
            The statements to filter the candidates by, applied one after
            another.

        Returns
        -------
        int
        """

        try:
            game = self.filter_chain(statements)
            n_solutions = len(game.candidates)
        except NoSolutionError as e:
            n_solutions = 0

        return n_solutions

    def get_solution(self, statements, trace=False):
        """Get the solution that satifies the given Statements

        Raises a NoSolutionError if no solution is found and a
        MultipleSolutionsError if multiple solutions are found.

        Parameters
        ----------
        statements: list of Statement
            The statements to filter the candidates by, applied one after
            another.
        trace: bool
            If true, print out intermediate values.

        Returns
        -------
        The one tuple that satisfies all Statements

        Raises
        ------
        NoSolutionError, MultipleSolutionsError
        """

        game = self.filter_chain(statements, trace=trace)
        if len(game.candidates) > 1:
            msg = "Found {} solutions".format(len(game.candidates))
            raise MultipleSolutionsError(msg)

        return list(game.candidates)[0]


    def __repr__(self):

        views = []
        for player in self.players:
            views.append(player.view(self.candidates))

        width = len(views[0][0])
        col_names = []
        for player in self.players:
            col_name = '{0:^{1}}'.format(player.name, width)
            col_names.append(col_name)

        header = '\t'.join(col_names)

        transposed = list(zip(*views))
        lines = map(lambda x: '\t'.join(x), transposed)
        body = '\n'.join(lines)

        return '\n'.join([header, body])


class Statement(object):
    """A statement made by one of the players about who knows what

    Attributes
    ----------
    author: str
        The name of the player who is making this statement.
    facts: dict str -> Knows
        Does each player know, not know, or maybe know? A dictionary mapping
        player names to Knows enum values. If a player's name does not appear
        in this dict, no statement about that player's knowledge is made.
        If a key is a tuple of strings, the given knowledge state applies
        to at least one of the players specified in the tuple.
    """

    def __init__(self, author, facts):
        for who, condition in facts.items():

            if not isinstance(who, tuple):
                continue

            for name in who:
                if name == author:
                    msg = "Author cannot be part of tuple"
                    raise InvalidStatementError(msg)

        self.author = author
        self.facts = facts

    def true_for(self, cand, game):
        """Is the statement true for a given candidate tuple?

        Parameters
        ----------
        cand: tuple
            The candidate tuple for which to evaluate the statement.
        game: Game
            The game in the context of which the statement is to be evaluated.

        Returns
        -------
        bool
        """

        author  = game.get_player(self.author)
        author_compatible = author.get_compatible(truth=cand, 
                                                  candidates=game.candidates)

        if (author.name in self.facts and
            knows(author_compatible) != self.facts[author.name]):
            return False

        for who, expected in self.facts.items():

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
                            candidates=game.candidates
                            )
                    if player_knowledge == expected:
                        found_match = True

                if not found_match:
                    return False

            else:

                player = game.get_player(who)
                player_knowledge = player.would_know(
                        truths=author_compatible,
                        candidates=game.candidates
                        )
                if player_knowledge != self.facts[who]:
                    return False

        return True

    def __repr__(self):
        return 'Statement(author={author}, facts={facts}'.format(
                author=self.author,
                facts=repr(self.facts)
                )


def choose_k(k):
    """Get a function that samples K values from a list of choices

    Would be nice to use numpy.random.choice here, but will avoid adding numpy
    as a dependency.

    Parameters
    ----------
    k: int
        The number of candidates to choose.

    Returns
    -------
    Function
    """

    def choose_func(choices):
        return [random.choice(choices) for _ in range(k)]

    return choose_func


def sample_candidates(domains, n_candidates, max_tries=100):
    """Sample N unique candidates from given sets of choices

    Parameters
    ----------
    domains: list of lists
        Each sublist contains the possible values that the corresponding
        dimension can take on.
    n_candidates: int
        The number of unique candidates to sample from each domain.
    max_tries: int
        The maximum number of times to loop in order to get n_candidates unique
        candidate, to prevent an infinite loop in cases that cannot be
        satisfied.

    Returns
    -------
    A sorted list of tuples

    >>> random.seed(123)
    >>> domains = [range(10), range(10, 20), range(20, 30)]
    >>> sample_candidates(domains, 5)
    [(0, 11, 25), (1, 16, 20), (4, 10, 25), (4, 18, 22), (6, 18, 22)]
    >>> domains = [list('abcdef'), range(6)]
    >>> sample_candidates(domains, 3)
    [('c', 1), ('c', 5), ('e', 1)]
    >>> domains = [[0, 1], ['a', 'b']]
    >>> sample_candidates(domains, 4)
    [(0, 'a'), (0, 'b'), (1, 'a'), (1, 'b')]
    """

    sample = []
    n_unique = 0
    n_tries = 0
    while n_unique != n_candidates:

        n_tries += 1
        if n_tries > max_tries:
            raise TooManyTriesError()

        choose = choose_k(n_candidates - n_unique)

        candidates = map(choose, domains)
        sample.extend(list(zip(*candidates)))

        n_unique = len(set(sample))

    return sorted(list(set(sample)))


def find_game(domains, n_candidates, statements, n_tries, player_names=None, 
              seed=123):
    """Find a game that satisfies a given list of Statements

    Find a Game object that has a unique solution under the given Statements.
    Raises NoGameFoundError if no such game is found.

    Parameters
    ----------
    domains: list of lists
        Each sublist contains the possible values that the corresponding
        dimension can take on.
    n_candidates: int
        The number of unique candidates to sample from each domain.
    statments: list of Statements
        The statements made by the players about who knows what.
    n_tries: int
        The maximum number of Game objects to generate and test before giving
        up.
    player_names: list of str
        The list of player names to use. If not given, each player will be
        named after the index of the dimension he is told about.
    seed: int
        The value to set the random seed to, for reproducibility of results.

    Returns
    -------
    A Game object that has a unique solution under the given Statements

    Raises
    ------
    NoGameFoundError
    """

    random.seed(seed)

    n_solutions = []
    for _ in range(n_tries):
        candidates = sample_candidates(domains, n_candidates)
        game = Game(candidates, player_names)

        my_n_solutions = game.n_solutions(statements)
        if my_n_solutions == 1:
            return game

        n_solutions.append(my_n_solutions)

    msg = repr(Counter(n_solutions))
    raise NoGameFoundError(msg)


class Knows(Enum):
    """Enum to represent different states of knowledge"""

    no = -1
    maybe = 0
    yes = 1


def knows(compatible):
    """Given a list of candidates still compatible, does a player know?

    Parameters
    ----------
    compatible: list
        The candidates that are still compatible with a players current
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
    """Aggregate knowledge over a list of possible cases

    During a game a number of candidates might be considered as candidates for a
    Player. For each of these candidates, the Player might know the solution
    (if the set of candidates has length 1) or not know (otherwise). This
    function aggregates the player's knowledge across the different cases. The
    player knows if he knows for each of the cases; does not know if he does
    not know for each of the cases; and knows maybe otherwise.

    Parameters
    ----------
    cases: list of Knows
        The knowledge state for the different cases under consideration

    Returns
    -------
    A Knows value (Knows.yes, Knows.maybe, or Knows.no).

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
    """Exception base class for this module"""
    pass

class BadPlayerNamesError(Error):
    """Names passed to Game are bad, e.g. contain duplicates"""
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

class MultipleSolutionsError(Error):
    """Found more than one solution for the given Statements"""
    pass

class TooManyTriesError(Error):
    """Too many tries in finding a sample of candidates"""
    pass
