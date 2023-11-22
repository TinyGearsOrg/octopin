#  Copyright (c) 2023, tinygears.org
#  This code is licensed under MIT license (see LICENSE for details)

import unittest

from parameterized import parameterized

from octopin.model.actions import ActionRef, ReusableWorkflow


class ReusableWorkflowTestCase(unittest.TestCase):
    @parameterized.expand(
        [
            "owner/repo/path/to/workflow.yml@v1",
            "owner/repo/path/to/workflow.yml",
            "./path/to/workflow.yaml",
        ]
    )
    def test_create(self, pattern):
        action_ref = ActionRef.of_pattern(pattern)
        self.assertTrue(isinstance(action_ref, ReusableWorkflow))


if __name__ == '__main__':
    unittest.main()
