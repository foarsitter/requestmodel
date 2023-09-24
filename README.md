# requestmodel

[![PyPI](https://img.shields.io/pypi/v/requestmodel.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/requestmodel.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/requestmodel)][pypi status]
[![License](https://img.shields.io/pypi/l/requestmodel)][license]

[![Read the documentation at https://requestmodel.readthedocs.io/](https://img.shields.io/readthedocs/requestmodel/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/foarsitter/requestmodel/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/foarsitter/requestmodel/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/requestmodel/
[read the docs]: https://requestmodel.readthedocs.io/
[tests]: https://github.com/foarsitter/requestmodel/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/foarsitter/requestmodel
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features

- Model your http requests as a pydantic model
- Annotate your request parameters with fastapi params
- Support voor sync & async requests

## Goals

- Create a generator for an OpenAPI spec
- Support all kinds of http requests

## Installation

You can install _requestmodel_ via [pip] from [PyPI]:

```console
$ pip install requestmodel
```

## Usage

Please see the [implementation detail] for further instructions.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_requestmodel_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/foarsitter/requestmodel/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/foarsitter/requestmodel/blob/main/LICENSE
[contributor guide]: https://github.com/foarsitter/requestmodel/blob/main/CONTRIBUTING.md
[implementation detail]: https://requestmodel.readthedocs.io/en/latest/usage.html
