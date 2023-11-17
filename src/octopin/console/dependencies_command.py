# Copyright (c) 2023, tinygears.org
# This code is licensed under MIT license (see LICENSE for details)

from __future__ import annotations

import asyncio

from cleo.commands.command import Command
from cleo.helpers import argument, option

from anytree import Node, RenderTree

from octopin.model.actions import ActionRef


class DependenciesCommand(Command):
    """
    Prints transitive workflow dependencies.
    """

    name = "dependencies"
    description = "Print workflow dependencies"
    arguments = [argument("workflow", description="Workflow to process", optional=False)]
    options = [option("resolve-pinned-versions", description="Resolve version", short_name="r")]

    def handle(self) -> int:
        workflow = self.argument("workflow")
        resolve_pinned_versions = self.option("resolve-pinned-versions")

        self.line(f"Reading workflow: <info>{workflow}</info>")
        self.line(text="")

        root = asyncio.run(self.create_tree(ActionRef.of_pattern(workflow), resolve_pinned_versions))

        def mysort(items):
            return sorted(items, key=lambda item: item.name)

        for pre, fill, node in RenderTree(root, childiter=mysort):
            action = node.action
            pinned_version = node.pinned_version

            if resolve_pinned_versions:
                if action.can_be_pinned() and node.parent is not None:
                    if pinned_version is not None:
                        self.line("%s%s # %s" % (pre, f"<fg=green>{action!r}</>", pinned_version))
                    else:
                        self.line("%s%s" % (pre, f"<fg=red>{action!r}</>"))
                else:
                    self.line("%s%s" % (pre, f"{action!r}"))
            else:
                self.line("%s%s" % (pre, f"{action!r}"))

        return 0

    async def create_tree(self, action: ActionRef, resolve_pinned_versions: bool, parent: Node = None) -> Node:
        workflow_file = await action.get_workflow_file()

        if resolve_pinned_versions is True:
            if action.can_be_pinned() and parent is not None:
                pinned_version = await action.pinned_version()
            else:
                pinned_version = None
        else:
            pinned_version = None

        node = Node(
            f"{action!r}", parent=parent, action=action, workflow_file=workflow_file, pinned_version=pinned_version
        )

        if workflow_file is not None:
            deps = workflow_file.get_used_actions()
            if len(deps) > 0:
                await asyncio.gather(
                    *[self.create_tree(ActionRef.of_pattern(dep), resolve_pinned_versions, node) for dep in deps]
                )
        return node
