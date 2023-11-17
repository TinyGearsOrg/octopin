# Copyright (c) 2023, tinygears.org
# This code is licensed under MIT license (see LICENSE for details)

from cleo.application import Application

from octopin import __version__
from octopin.console.dependencies_command import DependenciesCommand
from octopin.console.pin_command import PinCommand


class OctolockApplication(Application):
    def __init__(self) -> None:
        super().__init__("octopin", __version__)

        self.add(DependenciesCommand())
        self.add(PinCommand())


def cli() -> int:
    # logging.basicConfig(level='DEBUG')

    exit_code: int = OctolockApplication().run()
    return exit_code
