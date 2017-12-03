"""
Gather dependencies and commands
"""
import argparse
import functools

import attr

import pyrsistent

import gather

_COLLECTOR_FACTORY = gather.Collector(functools.partial(gather.Collector,
                                                        depth=1))


@attr.s(frozen=True)
class Commands(object):

    """
    A command and dependency gatherer.
    """

    _collector = attr.ib(default=_COLLECTOR_FACTORY, init=False)
    _command_collector = attr.ib(default=_COLLECTOR_FACTORY, init=False)

    def command(self,
                name=None,
                parser=argparse.ArgumentParser(),
                dependencies=pyrsistent.v()):
        """
        Register as a command.

        """
        transform = gather.Wrapper.glue((dependencies, parser))
        ret = self._command_collector.register(name, transform=transform)
        return ret

    def run(self, args, override_dependencies=pyrsistent.m()):
        """
        Run a command

        """
        name, args = args[0], args[1:]
        collection = self._command_collector.collect()
        command = collection[name]
        func = command.original
        dependencies, parser = command.extra
        graph = self.mkgraph(dependencies)
        graph.update(override_dependencies)
        parsed = parser(args)
        return func(parsed, graph)

    def dependency(self,
                   name=None,
                   dependencies=pyrsistent.v(),
                   possible_dependencies=pyrsistent.v()):
        """
        Register as a dependency.

        """
        glue = (dependencies, possible_dependencies)
        transform = gather.Wrapper.glue(glue)
        ret = self._collector.register(name, transform=transform)
        return ret

    # Recursive implementation for now
    def mkgraph(self, things):
        """
        Resolve dependencies and generate them

        """
        collection = self._collector.collect()
        ret = {}

        def _build(thing, on_route=pyrsistent.s()):
            if thing in on_route:
                raise ValueError("circular dependency detected",
                                 thing, on_route)
            if thing in ret:
                return ret[thing]
            on_route = on_route.add(thing)
            plugin = collection[thing]
            func = plugin.original
            dependencies, possible_dependencies = plugin.extra
            my_dependencies, my_possible_dependencies = {}, {}
            for other_thing in dependencies:
                my_dependencies[other_thing] = _build(other_thing, on_route)
            for other_thing in possible_dependencies:
                builder = functools.partial(_build, other_thing, on_route)
                my_possible_dependencies[other_thing] = builder
            ret[thing] = func(my_dependencies, my_possible_dependencies)
            return ret[thing]
        for thing in things:
            _build(thing)
        return ret
