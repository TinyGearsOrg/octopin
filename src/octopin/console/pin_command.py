# Copyright (c) 2023, tinygears.org
# This code is licensed under MIT license (see LICENSE for details)

from __future__ import annotations

import asyncio
import difflib
import os.path
import re
from typing import Optional

from cleo.commands.command import Command
from cleo.helpers import argument, option

from octopin.model.actions import ActionRef
from octopin.model.workflow_file import WorkflowFile


class PinCommand(Command):
    """
    Pin actions used in workflows.
    """

    name = "pin"
    description = "Pin used workflows / actions"
    arguments = [argument("workflow", description="Workflow to process", optional=False)]
    options = [
        option("diff", description="Show diffs", short_name="d"),
        option(
            "inplace",
            description="Modify input workflow inplace, not taken into account when --diff is enabled",
            short_name="i",
        ),
    ]

    def handle(self) -> int:
        workflow = self.argument("workflow")
        diff_mode = self.option("diff")
        inplace_mode = self.option("inplace")

        workflow_ref = ActionRef.of_pattern(workflow)
        workflow_file, pinned_lines = asyncio.run(self.handle_async(workflow_ref))

        if workflow_file is None:
            return 1

        if diff_mode is True:
            for line in difflib.unified_diff(
                workflow_file.lines, pinned_lines, fromfile='original', tofile='pinned', n=3, lineterm='\n'
            ):
                line = line.rstrip('\n')
                if line.startswith("-"):
                    self.line(f"<fg=red>{line}</>")
                elif line.startswith("+"):
                    self.line(f"<fg=green>{line}</>")
                else:
                    self.line(line)
        else:
            if inplace_mode is True and os.path.exists(workflow):
                with open(workflow, "wt") as out:
                    for line in pinned_lines:
                        out.write(line)
            else:
                for line in pinned_lines:
                    self.line(line.rstrip('\n'))

        return 0

    async def handle_async(self, workflow_ref: ActionRef) -> tuple[Optional[WorkflowFile], list[str]]:
        workflow_file = await workflow_ref.get_workflow_file()
        if workflow_file is None:
            self.line_error("<error>Could not retrieve workflow file</error>")
            return None, []

        actions = set(workflow_file.get_used_actions())
        pinned_actions = {}

        tasks = []
        for action in actions:
            a = ActionRef.of_pattern(action)
            if a.can_be_pinned():
                tasks.append(a.pin())
            else:
                pinned_actions[action] = action

        r = await asyncio.gather(*tasks)

        for orig_action, pinned_action, pinned_comment in r:
            if pinned_comment:
                pinned_actions[orig_action] = f"{pinned_action!r} # {pinned_comment}"
            else:
                pinned_actions[orig_action] = f"{pinned_action!r}"

        def pin(m):
            return m.group(2) + pinned_actions[m.group(3)]

        pinned_lines = []
        for line in workflow_file.lines:
            pinned_lines.append(re.sub(r"((uses:\s+)([^\s#]+)((\s+#)([^\n]+))?)(?=\n?)", pin, line))

        return workflow_file, pinned_lines
