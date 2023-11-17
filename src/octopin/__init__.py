# Copyright (c) 2023, tinygears.org
# This code is licensed under MIT license (see LICENSE for details)

import importlib.metadata


_DISTRIBUTION_METADATA = importlib.metadata.metadata("octopin")
__version__ = _DISTRIBUTION_METADATA["Version"]
__app__ = _DISTRIBUTION_METADATA["Name"]
