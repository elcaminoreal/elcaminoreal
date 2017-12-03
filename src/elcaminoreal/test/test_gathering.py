"""
Test dependencies and commands
"""
from __future__ import print_function

import unittest

from elcaminoreal.test import some_plugins


class DependencyResolverTester(unittest.TestCase):

    """
    Dependency resolution tests
    """

    def test_mkgraph(self):
        """
        mkgraph finds and runs dependencies without subdependencis
        """
        result = some_plugins.COMMANDS.mkgraph(['bar'])
        self.assertEquals(result.pop('bar'), "I'm a bar")
        self.assertEquals(result, {})

    def test_mkgraph_cycle(self):
        """
        mkgraph raises ValueError when it detects a cycle
        """
        with self.assertRaises(ValueError):
            some_plugins.COMMANDS.mkgraph(['robin'])

    def test_mkgraph_random(self):
        """
        mkgraph caches subdependencies
        """
        result = some_plugins.COMMANDS.mkgraph(['rand', 'needs_rand'])
        self.assertEquals(result['rand'], result['needs_rand']['rand'])

    def test_mkgraph_possible(self):
        """
        mkgraph possible dependencies are functions that return the object
        """
        result = some_plugins.COMMANDS.mkgraph(['foo_2'])
        self.assertEquals(result['foo_2'], dict(bar="I'm a bar"))


class RunnerResolverTester(unittest.TestCase):

    """
    Command running tests
    """

    def test_run(self):
        """
        Run calls the command with the dependencies it requested
        """
        output = []

        def _my_print(*args):
            output.append(' '.join(map(str, args)))
        some_plugins.COMMANDS.run(['show', 'heee'],
                                  override_dependencies=dict(print=_my_print))
        self.assertEquals(len(output), 1)
        args, deps = output[0].split(None, 1)
        self.assertIn('hee', args)
        self.assertIn('foo', deps)
        self.assertIn('bar', deps)