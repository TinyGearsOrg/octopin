# octopin

[![Build status](https://github.com/TinyGearsOrg/octopin/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/TinyGearsOrg/octopin/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A tool to analyse transitive dependencies of GitHub workflows and to pin actions.

## Usage:

Setup:

```shell
$ poetry install
```

Show transitive dependencies:

```shell
$ poetry run octopin dependencies path/to/my/workflow.yml
```

Pin actions:

```shell
$ poetry run octopin pin path/to/my/workflow.yml
```

Note: depending on the specified options, various calls to the GitHub API have to be made, which means you can easily
run into rate limit issues. You can provide a GitHub PAT by setting the environment variable `GH_TOKEN`.

