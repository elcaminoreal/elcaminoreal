"""
Some plugins to support the tests.
"""

from __future__ import print_function

import random

import elcaminoreal


COMMANDS = elcaminoreal.Commands()


@COMMANDS.dependency(name="foo", dependencies=["bar"])
def a_foo(dependencies, _possible_dependencies):
    """
    Depend on a bar object
    """
    return dict(bar=dependencies['bar'])


@COMMANDS.dependency(possible_dependencies=["bar"])
def foo_2(_dependencies, possible_dependencies):
    """
    Depend on a bar object in an optional way.
    """
    return dict(bar=possible_dependencies['bar']())


@COMMANDS.dependency(name="bar")
def a_bar(_dependencies, _possible_dependencies):
    """
    Return a bar-like object.
    """
    return "I'm a bar"


@COMMANDS.dependency()
def rand(_dependencies, _possible_dependencies):
    """
    Generate a random number.
    """
    return random.random()


@COMMANDS.dependency(dependencies=["rand"])
def needs_rand(dependencies, _possible_dependencies):
    """
    Depend on a random number.
    """
    return dict(rand=dependencies["rand"])


@COMMANDS.dependency(name="baz")
def a_baz(dependencies, _possible_dependencies):
    """
    Use an undeclared dependency.
    """
    return dependencies['bar']


@COMMANDS.dependency(dependencies=['tuck'])
def robin(_dependencies, _possible_dependencies):
    """
    Depend on tuck
    """


@COMMANDS.dependency(dependencies=['robin'])
def tuck(_dependencies, _possible_dependencies):
    """
    Depend on robin
    """


@COMMANDS.dependency(name='print')
def _print(_dependencies, _possible_dependencies):
    """
    Return a function to display things on the terminal.
    """
    return print


@COMMANDS.command(dependencies=['foo', 'print'],
                  parser=elcaminoreal.argparser(
                      elcaminoreal.argument('lala'),
                  ))
def show(args, dependencies):
    """
    Print then arguments.
    """
    dependencies['print'](args, dependencies)


@COMMANDS.command(dependencies=['bar'],
                  parser=elcaminoreal.argparser(
                      elcaminoreal.argument('wooo'),
                  ))
def gowoo(args, dependencies):
    """
    Print 'woo' and then arguments.
    """
    dependencies['print']("woo", args, dependencies)
