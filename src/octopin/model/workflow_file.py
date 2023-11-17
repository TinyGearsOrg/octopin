# Copyright (c) 2023, tinygears.org
# This code is licensed under MIT license (see LICENSE for details)

from __future__ import annotations

import dataclasses

import yaml

from typing import Any


@dataclasses.dataclass
class WorkflowFile:
    raw_content: str
    content: dict[str, Any] = dataclasses.field(init=False)
    lines: list[str] = dataclasses.field(init=False)

    def __post_init__(self):
        self.content = yaml.safe_load(self.raw_content)
        self.lines = self.raw_content.splitlines(keepends=True)

    def get_used_actions(self) -> list[str]:
        """

        :return:
        """
        workflows = []

        # regular workflows
        for k, v in self.content.get("jobs", {}).items():
            # jobs.<job_id>.steps[*].uses
            for step in v.get("steps", []):
                if "uses" in step:
                    workflows.append(step["uses"])

            # jobs.<job_id>.uses
            if "uses" in v:
                workflows.append(v["uses"])

        # composite actions
        if "runs" in self.content:
            # runs.steps[*].uses
            for step in self.content["runs"].get("steps", []):
                if "uses" in step:
                    workflows.append(step["uses"])

        return workflows
