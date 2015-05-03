from operator import itemgetter

import pandas as pd
from enum import Enum


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

        return [e for e in elems if e[self.index] == truth[self.index]]

    def _format(self, elem):
        border = '|' if self.matches(elem) else ' '

        return '{border}{data}{border}'.format(
            border=border,
            data=' '.join([str(e) for e in elem])
            )

    def __repr__(self):
        return 'Player(index={}, told={})'.format(self.index, self.told)


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

        for player in self.players:
            if not player.has_solution(elems):
                msg = "No solution for player {}".format(player.name)   
                raise InvalidStateError(msg)


    def matches_statement(self, cand, statement, teller_name):
        """

        Parameters
        ----------
        cand: tuple
            The candidate element for which to evaluate the statement.
        statement: dict str -> Knows
            Does each player know, not know, or maybe know? A dictionary mapping
            player names to Knows enum values. If a player's name does not appear
            in this dict, no statement about that player's knowledge is made.
        teller_name: str
            The name of the player who is making this statement.

        Returns
        -------
        bool
        """

        teller  = self.get_player(teller_name)
        teller_compatible = teller.get_compatible(truth=cand, elems=self.elems)

        if (teller.name in statement and
            knows(teller_compatible) != statement[teller.name]):
            return False


        for name, expected in statement.items():

            if name == teller_name:
                continue

            player = self.get_player(name)

            cases = []
            for elem in teller_compatible:
                player_compatible = player.get_compatible(truth=elem, 
                                                         elems=self.elems)
                cases.append(knows(player_compatible))

            if knows_cases(cases) != statement[name]:
                return False

        return True


    def filter_elems(self, statement, teller_name):

        filtered = []
        for elem in self.elems:
            if self.matches_statement(elem, statement, teller_name):
                filtered.append(elem)

        self.assert_has_solution(filtered)

        self.elems =  set(filtered)

        return len(filtered)


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
    """
    return Knows.yes if len(compatible) == 1 else Knows.no


def knows_cases(cases):

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
    pass

class InvalidStateError(Error):
    pass
