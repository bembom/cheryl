
# Solving and Generating Puzzles like *Find Cheryl's Birthday*

[![Build Status](https://travis-ci.org/bembom/cheryl.svg?branch=master)](https://travis-ci.org/bembom/cheryl)

[Finding Cheryl's birthday](http://www.nytimes.com/2015/04/15/science/a-math-problem-from-singapore-goes-viral-when-is-cheryls-birthday.html) is a fun puzzle. But what if the situation were more complex? What if apart from Albert and Bernard there was also Carl, and between the three of them they had to guess Cheryl's complete birthday, including the year she was born?

The strategy for solving such puzzles stays the same, but the paper-and-pencil approach quickly becomes tedious as the puzzles become more complex. Also, how would we come up with such puzzles in the first place? Going through a large list of possible permutations before arriving at an interesting version would be even more time consuming.

Inspired by Peter Norvig's [IPython notebook](http://nbviewer.ipython.org/url/norvig.com/ipython/Cheryl.ipynb) on finding Cheryl's birthday in Python, [`cheryl`](https://github.com/bembom/cheryl) is a Python module for generating and solving such problems in a more general way.

## Solving Puzzles

Let's use `cheryl` to solve the original problem:


    from cheryl import Game, Statement, Knows
    
    candidates = [
        ('May', 15), ('May', 16), ('May', 19),
        ('June', 17), ('June', 18),
        ('July', 14), ('July', 16),
        ('Aug', 14), ('Aug', 15), ('Aug', 17)
        ]
    
    game = Game(candidates, player_names=['Albert', 'Bernard'])
    
    statement1 = Statement(
            author='Albert',
            facts={'Albert': Knows.no, 'Bernard': Knows.no}
            )
    statement2 = Statement(
            author='Bernard',
            facts={'Bernard': Knows.yes}
            )
    statement3 = Statement(
            author='Albert',
            facts={'Albert': Knows.yes}
            )
    
    game.get_solution([statement1, statement2, statement3])




    ('July', 16)



We can also ask to see the progression of candidate values that are still in play as each statement is applied as a filter:


    game.get_solution([statement1, statement2, statement3], trace=True)

    Before filtering:
    Albert	Bernard
    Aug 15	July 14
    Aug 14	Aug 14
    Aug 17	May 15
    July 14	Aug 15
    July 16	May 16
    June 17	July 16
    June 18	June 17
    May 19	Aug 17
    May 16	June 18
    May 15	May 19
    
    After applying statement 1:
    Albert	Bernard
    Aug 15	Aug 14
    Aug 14	July 14
    Aug 17	Aug 15
    July 16	July 16
    July 14	Aug 17
    
    After applying statement 2:
    Albert	Bernard
    Aug 15	Aug 15
    Aug 17	July 16
    July 16	Aug 17
    
    After applying statement 3:
    Albert 	Bernard
    July 16	July 16





    ('July', 16)



At each point, the candidate values are sorted for each candidate based on the piece of information they were told.

The `candidates` list contains the candidate values that Cheryl gives Albert and Bernard. A `Game` object is instantiated from these candidates values and a list of player names.

Next we instantiate `Statement`s that represent what Albert and Bernard know at the various stages of the game. First Albert states that neither he nor Bernard know the solution, using the `Enum` class `Knows`. After Albert has made his statement, Bernard says that he now knows the solution. After this statement, now Albert knows too.

The solution is found through a method call to `get_solution`, which takes a `list` of `Statement`s that must be true when evaluated one after another.

Next let's consider the more complex game, in which Albert, Bernard and Carl guess Cheryl's full birthday. Again Cheryl gives 10 candidate dates:


    candidates = [
        (1970, 'May', 19), (1970, 'July', 18), (1971, 'May', 19),
        (1971, 'July', 19), (1973, 'May', 18), (1973, 'June', 18), 
        (1973, 'Aug', 16), (1973, 'Aug', 18), (1974, 'June', 18), 
        (1974, 'Sept', 18)    
        ]
    
    game = Game(candidates, player_names=['Albert', 'Bernard', 'Carl'])

In this case it might take the three of them a little longer to figure out her birthday. Each of them might, for example, say that they don't know the answer yet, before Albert finally arrives at it in statement 10:


    statements = [Statement(author='Albert', facts={'Albert': Knows.no}),
                  Statement(author='Bernard', facts={'Bernard': Knows.no}),
                  Statement(author='Carl', facts={'Carl': Knows.no}),
                  Statement(author='Albert', facts={'Albert': Knows.no}),
                  Statement(author='Bernard', facts={'Bernard': Knows.no}),
                  Statement(author='Carl', facts={'Carl': Knows.no}),
                  Statement(author='Albert', facts={'Albert': Knows.no}),
                  Statement(author='Bernard', facts={'Bernard': Knows.no}),
                  Statement(author='Carl', facts={'Carl': Knows.no}),
                  Statement(author='Albert', facts={'Albert': Knows.yes}),
                ]

Given the candidate values above, this game has a unique solution:


    game.get_solution(statements)




    (1970, 'May', 19)



Again we can look at the trace as statements are applied:


    game.get_solution(statements, trace=True)

    Before filtering:
      Albert   	  Bernard  	   Carl    
    1970 May 19	1973 Aug 16	1973 Aug 16
    1970 July 18	1973 Aug 18	1974 June 18
    1971 July 19	1971 July 19	1973 June 18
    1971 May 19	1970 July 18	1973 May 18
    1973 June 18	1974 June 18	1974 Sept 18
    1973 Aug 16	1973 June 18	1973 Aug 18
    1973 May 18	1971 May 19	1970 July 18
    1973 Aug 18	1973 May 18	1971 July 19
    1974 June 18	1970 May 19	1971 May 19
    1974 Sept 18	1974 Sept 18	1970 May 19
    
    After applying statement 1:
      Albert   	  Bernard  	   Carl    
    1970 May 19	1973 Aug 16	1973 Aug 16
    1970 July 18	1973 Aug 18	1974 June 18
    1971 July 19	1971 July 19	1973 June 18
    1971 May 19	1970 July 18	1973 May 18
    1973 Aug 16	1974 June 18	1974 Sept 18
    1973 June 18	1973 June 18	1973 Aug 18
    1973 May 18	1971 May 19	1970 July 18
    1973 Aug 18	1973 May 18	1971 July 19
    1974 June 18	1970 May 19	1971 May 19
    1974 Sept 18	1974 Sept 18	1970 May 19
    
    After applying statement 2:
      Albert   	  Bernard  	   Carl    
    1970 May 19	1973 Aug 16	1973 Aug 16
    1970 July 18	1973 Aug 18	1974 June 18
    1971 May 19	1971 July 19	1973 June 18
    1971 July 19	1970 July 18	1973 May 18
    1973 Aug 16	1974 June 18	1973 Aug 18
    1973 June 18	1973 June 18	1970 July 18
    1973 May 18	1971 May 19	1971 May 19
    1973 Aug 18	1973 May 18	1971 July 19
    1974 June 18	1970 May 19	1970 May 19
    
    After applying statement 3:
      Albert   	  Bernard  	   Carl    
    1970 May 19	1973 Aug 18	1974 June 18
    1970 July 18	1971 July 19	1973 June 18
    1971 July 19	1970 July 18	1973 May 18
    1971 May 19	1974 June 18	1973 Aug 18
    1973 June 18	1973 June 18	1970 July 18
    1973 May 18	1971 May 19	1971 July 19
    1973 Aug 18	1973 May 18	1971 May 19
    1974 June 18	1970 May 19	1970 May 19
    
    After applying statement 4:
      Albert   	  Bernard  	   Carl    
    1970 May 19	1973 Aug 18	1973 June 18
    1970 July 18	1971 July 19	1973 May 18
    1971 July 19	1970 July 18	1973 Aug 18
    1971 May 19	1973 June 18	1970 July 18
    1973 June 18	1971 May 19	1971 July 19
    1973 May 18	1973 May 18	1971 May 19
    1973 Aug 18	1970 May 19	1970 May 19
    
    After applying statement 5:
       Albert   	  Bernard   	    Carl    
    1970 July 18	1970 July 18	1973 May 18
    1970 May 19	1971 July 19	1970 July 18
    1971 July 19	1973 May 18	1970 May 19
    1971 May 19	1970 May 19	1971 July 19
    1973 May 18	1971 May 19	1971 May 19
    
    After applying statement 6:
      Albert   	  Bernard  	   Carl    
    1970 May 19	1971 July 19	1973 May 18
    1970 July 18	1970 July 18	1970 July 18
    1971 July 19	1971 May 19	1971 July 19
    1971 May 19	1970 May 19	1971 May 19
    1973 May 18	1973 May 18	1970 May 19
    
    After applying statement 7:
       Albert   	  Bernard   	    Carl    
    1970 July 18	1970 July 18	1970 July 18
    1970 May 19	1971 July 19	1970 May 19
    1971 July 19	1970 May 19	1971 July 19
    1971 May 19	1971 May 19	1971 May 19
    
    After applying statement 8:
      Albert   	  Bernard  	   Carl    
    1970 May 19	1970 July 18	1970 July 18
    1970 July 18	1971 July 19	1971 May 19
    1971 May 19	1971 May 19	1970 May 19
    1971 July 19	1970 May 19	1971 July 19
    
    After applying statement 9:
      Albert   	  Bernard  	   Carl    
    1970 May 19	1971 July 19	1970 May 19
    1971 July 19	1970 May 19	1971 July 19
    1971 May 19	1971 May 19	1971 May 19
    
    After applying statement 10:
      Albert   	  Bernard  	   Carl    
    1970 May 19	1970 May 19	1970 May 19





    (1970, 'May', 19)



Let's look at another example:


    candidates = [
        (1970, 'Aug', 16), (1970, 'July', 15), (1970, 'Sept', 18), 
        (1971, 'Aug', 15), (1971, 'Aug', 17), (1972, 'Sept', 17), 
        (1973, 'July', 15), (1973, 'May', 17), (1974, 'July', 19), 
        (1974, 'Sept', 15)
        ]
    
    
    game = Game(candidates, player_names=['Albert', 'Bernard', 'Carl'])
    
    statements = [Statement(author='Albert', 
                            facts={'Albert': Knows.no, ('Bernard', 'Carl'): Knows.maybe}),
                  Statement(author='Bernard', 
                            facts={'Bernard': Knows.no, ('Albert', 'Carl'): Knows.maybe}),
                  Statement(author='Carl', 
                            facts={'Carl': Knows.no, ('Albert', 'Bernard'): Knows.maybe}),
                  Statement(author='Albert', 
                            facts={'Albert': Knows.yes}),
                  Statement(author='Bernard', 
                            facts={'Bernard': Knows.yes}),
                  Statement(author='Carl', 
                            facts={'Carl': Knows.yes}),
                 ]

In this case, Albert starts off by saying that he does not know the solution, but that either Bernard or Carl might know. This introduces the syntax of giving a tuple of names to denote that the following state is true for at least one of the named players. It also introduces the new state of knowing the solution 'maybe'. This means that when Albert looks at the values that are compatible with what Cheryl told him, there is at least one such value for which either Bernard or Carl knows the solution. In other words, Albert cannot be certain that both of them do *not* know the solution.

This game continues with Bernard and Carl making equivalent statements, before everyone figures out the answer in the second round. 

This game also has a unique solution:


    game.get_solution(statements, trace=True)

    Before filtering:
       Albert   	  Bernard   	    Carl    
    1970 Sept 18	1971 Aug 17	1973 July 15
    1970 Aug 16	1970 Aug 16	1970 July 15
    1970 July 15	1971 Aug 15	1974 Sept 15
    1971 Aug 17	1973 July 15	1971 Aug 15
    1971 Aug 15	1970 July 15	1970 Aug 16
    1972 Sept 17	1974 July 19	1971 Aug 17
    1973 May 17	1973 May 17	1972 Sept 17
    1973 July 15	1972 Sept 17	1973 May 17
    1974 Sept 15	1970 Sept 18	1970 Sept 18
    1974 July 19	1974 Sept 15	1974 July 19
    
    After applying statement 1:
       Albert   	  Bernard   	    Carl    
    1970 Sept 18	1970 Aug 16	1973 July 15
    1970 Aug 16	1973 July 15	1970 July 15
    1970 July 15	1970 July 15	1974 Sept 15
    1973 May 17	1974 July 19	1970 Aug 16
    1973 July 15	1973 May 17	1973 May 17
    1974 Sept 15	1970 Sept 18	1970 Sept 18
    1974 July 19	1974 Sept 15	1974 July 19
    
    After applying statement 2:
       Albert   	  Bernard   	    Carl    
    1970 July 15	1973 July 15	1973 July 15
    1970 Sept 18	1970 July 15	1970 July 15
    1973 July 15	1974 July 19	1974 Sept 15
    1974 July 19	1970 Sept 18	1970 Sept 18
    1974 Sept 15	1974 Sept 15	1974 July 19
    
    After applying statement 3:
       Albert   	  Bernard   	    Carl    
    1970 July 15	1973 July 15	1973 July 15
    1973 July 15	1970 July 15	1970 July 15
    1974 Sept 15	1974 Sept 15	1974 Sept 15
    
    After applying statement 4:
       Albert   	  Bernard   	    Carl    
    1970 July 15	1973 July 15	1973 July 15
    1973 July 15	1970 July 15	1970 July 15
    1974 Sept 15	1974 Sept 15	1974 Sept 15
    
    After applying statement 5:
       Albert   	  Bernard   	    Carl    
    1974 Sept 15	1974 Sept 15	1974 Sept 15
    
    After applying statement 6:
       Albert   	  Bernard   	    Carl    
    1974 Sept 15	1974 Sept 15	1974 Sept 15





    (1974, 'Sept', 15)



## Generating Puzzles

These are the kinds of games that can be solved with `cheryl`. But how were these particular configurations found to begin with?

The module provides a function `find_games` that can be used to search for a configuration that satisfies a given list of `Statements`:


    from cheryl import find_game
    
    domains = [range(1970, 1975), 
               ['May', 'June', 'July', 'Aug', 'Sept'], 
               range(15, 20)]
    
    n_candidates = 10
    
    statements = [Statement(author='Albert', 
                            facts={'Albert': Knows.no, ('Bernard', 'Carl'): Knows.maybe}),
                  Statement(author='Bernard', 
                            facts={'Bernard': Knows.no, ('Albert', 'Carl'): Knows.maybe}),
                  Statement(author='Carl', 
                            facts={'Carl': Knows.no, ('Albert', 'Bernard'): Knows.maybe}),
                  Statement(author='Albert', 
                            facts={'Albert': Knows.yes, 'Carl': Knows.no}),
                  Statement(author='Bernard', 
                            facts={'Bernard': Knows.yes, 'Carl': Knows.yes}),
                  Statement(author='Carl', 
                            facts={'Carl': Knows.yes}),
                 ]
    
    game = find_game(domains, n_candidates, statements, n_tries=500, 
                     player_names=['Albert', 'Bernard', 'Carl'])

First we define the domain of possible values for each dimension, with the birth year ranging from 1970 to 1974, the month from May to September, and the day from 15 to 19. Next we specify that Cheryl will give the players 10 candidate values. This list of statements that are to lead to a unique solution is given next. In the call to `find_game` we also specify that the function should try at most 500 random samples of candidate values from the given domains. If no solution is found within those iteration, an exception will be thrown. 

In this case, the call succeeds and we can examine the solution as before:


    game.get_solution(statements, trace=True)

    Before filtering:
      Albert   	  Bernard  	   Carl    
    1971 May 17	1972 Aug 18	1974 June 15
    1971 Aug 17	1971 Aug 17	1974 July 16
    1971 Aug 18	1971 Aug 18	1971 May 16
    1971 Aug 19	1971 Aug 19	1971 May 17
    1971 May 16	1974 July 16	1971 Aug 17
    1971 June 18	1974 June 15	1972 Aug 18
    1972 Aug 18	1971 June 18	1971 Aug 18
    1972 Sept 18	1971 May 17	1971 June 18
    1974 July 16	1971 May 16	1972 Sept 18
    1974 June 15	1972 Sept 18	1971 Aug 19
    
    After applying statement 1:
      Albert   	  Bernard  	   Carl    
    1971 May 17	1972 Aug 18	1974 June 15
    1971 Aug 17	1971 Aug 17	1974 July 16
    1971 Aug 18	1971 Aug 18	1971 May 16
    1971 Aug 19	1971 Aug 19	1971 May 17
    1971 May 16	1974 July 16	1971 Aug 17
    1971 June 18	1974 June 15	1972 Aug 18
    1972 Aug 18	1971 June 18	1971 Aug 18
    1972 Sept 18	1971 May 17	1971 June 18
    1974 July 16	1971 May 16	1972 Sept 18
    1974 June 15	1972 Sept 18	1971 Aug 19
    
    After applying statement 2:
      Albert   	  Bernard  	   Carl    
    1971 Aug 17	1972 Aug 18	1974 June 15
    1971 Aug 18	1971 Aug 17	1971 Aug 17
    1971 Aug 19	1971 Aug 18	1972 Aug 18
    1971 June 18	1971 Aug 19	1971 Aug 18
    1972 Aug 18	1974 June 15	1971 June 18
    1974 June 15	1971 June 18	1971 Aug 19
    
    After applying statement 3:
      Albert   	  Bernard  	   Carl    
    1971 Aug 18	1971 Aug 18	1971 Aug 18
    1971 June 18	1972 Aug 18	1972 Aug 18
    1972 Aug 18	1971 June 18	1971 June 18
    
    After applying statement 4:
      Albert   	  Bernard  	   Carl    
    1972 Aug 18	1972 Aug 18	1972 Aug 18
    
    After applying statement 5:
      Albert   	  Bernard  	   Carl    
    1972 Aug 18	1972 Aug 18	1972 Aug 18
    
    After applying statement 6:
      Albert   	  Bernard  	   Carl    
    1972 Aug 18	1972 Aug 18	1972 Aug 18





    (1972, 'Aug', 18)



As another example we look for a game in which each player first states that neither he nor anyone else knows the answer, before every player then finds the solution in the second round:


    statements = [
                  Statement(author='Albert', 
                            facts={'Albert': Knows.no, 'Bernard': Knows.no, 'Carl': Knows.no}),
                  Statement(author='Bernard', 
                            facts={'Bernard': Knows.no, 'Albert': Knows.no, 'Carl': Knows.no}),
                  Statement(author='Carl', 
                            facts={'Carl': Knows.no, 'Albert': Knows.no, 'Bernard': Knows.no}),
                  Statement(author='Albert', 
                            facts={'Albert': Knows.yes}), 
                  Statement(author='Bernard', 
                            facts={'Bernard': Knows.yes}), 
                  Statement(author='Carl', 
                            facts={'Carl': Knows.yes})
                 ]
    
    game = find_game(domains, n_candidates, statements, n_tries=1000, 
                     player_names=['Albert', 'Bernard', 'Carl'])
    game.get_solution(statements, trace=True)

    Before filtering:
      Albert   	  Bernard  	   Carl    
    1970 Aug 18	1970 Aug 18	1972 Sept 15
    1970 July 19	1973 Aug 19	1973 June 15
    1970 Sept 18	1971 Aug 17	1971 June 16
    1971 Aug 17	1970 July 19	1971 Aug 17
    1971 June 16	1973 July 19	1970 Aug 18
    1972 Sept 15	1971 June 16	1970 Sept 18
    1973 Aug 19	1974 June 19	1973 Aug 19
    1973 July 19	1973 June 15	1970 July 19
    1973 June 15	1972 Sept 15	1973 July 19
    1974 June 19	1970 Sept 18	1974 June 19
    
    After applying statement 1:
      Albert   	  Bernard  	   Carl    
    1970 Aug 18	1970 Aug 18	1973 June 15
    1970 July 19	1973 Aug 19	1970 Aug 18
    1970 Sept 18	1970 July 19	1970 Sept 18
    1973 Aug 19	1973 July 19	1973 Aug 19
    1973 July 19	1973 June 15	1970 July 19
    1973 June 15	1970 Sept 18	1973 July 19
    
    After applying statement 2:
      Albert   	  Bernard  	   Carl    
    1970 Aug 18	1970 Aug 18	1970 Aug 18
    1970 July 19	1973 Aug 19	1973 Aug 19
    1973 Aug 19	1973 July 19	1973 July 19
    1973 July 19	1970 July 19	1970 July 19
    
    After applying statement 3:
       Albert   	  Bernard   	    Carl    
    1970 July 19	1973 Aug 19	1973 Aug 19
    1973 Aug 19	1973 July 19	1973 July 19
    1973 July 19	1970 July 19	1970 July 19
    
    After applying statement 4:
       Albert   	  Bernard   	    Carl    
    1970 July 19	1970 July 19	1970 July 19
    
    After applying statement 5:
       Albert   	  Bernard   	    Carl    
    1970 July 19	1970 July 19	1970 July 19
    
    After applying statement 6:
       Albert   	  Bernard   	    Carl    
    1970 July 19	1970 July 19	1970 July 19





    (1970, 'July', 19)



Here is an example where we cannot find a matching configuration within the given number of iterations:


    statements = [
                  Statement(author='Albert', 
                            facts={'Albert': Knows.no, 'Bernard': Knows.no, 'Carl': Knows.yes}),
                  Statement(author='Bernard', 
                            facts={'Bernard': Knows.no, 'Albert': Knows.no, 'Carl': Knows.yes}),
                  Statement(author='Carl', 
                            facts={'Carl': Knows.yes}),
                 ]
    
    game = find_game(domains, n_candidates, statements, n_tries=100, 
                     player_names=['Albert', 'Bernard', 'Carl'])
    game.get_solution(statements, trace=True)


    ---------------------------------------------------------------------------

    NoGameFoundError                          Traceback (most recent call last)

    <ipython-input-12-367d63a504a0> in <module>()
          9 
         10 game = find_game(domains, n_candidates, statements, n_tries=100, 
    ---> 11                  player_names=['Albert', 'Bernard', 'Carl'])
         12 game.get_solution(statements, trace=True)


    /mnt/home/obembom/projects/cheryl/cheryl.py in find_game(domains, n_candidates, statements, n_tries, player_names, seed)
        498 
        499     msg = repr(Counter(n_solutions))
    --> 500     raise NoGameFoundError(msg)
        501 
        502 


    NoGameFoundError: Counter({0: 99, 2: 1})


Note that the exception message shows the distribution of the number of times a given number of solutions was encountered. In this case, 99 of the 100 samples had zero solutions after applying the given statements and 1 sample had 2 solutions. Since we are looking for a configuration with exactly one solution, `find_games()` failed, but this kind of output is helpful in tweaking the statements to find a feasible configuration.

## Usage

The `cheryl` module is available on [GitHub](https://github.com/bembom/cheryl). It is written in __Python 3.4__ but has no dependencies on other packages. The main thing to do to get the module to work in Python 2 would be to work around its lack of `Enum`s, which are used to encode if a player knows, does not know, or maybe knows the solution.
