# CHANGELOG


## [3.1.6] - 2025-05-16
### Changed
- Update grpcio-tools requirements

## [3.1.5] - 2025-04-07
### Changed
- remove version restrictions on dependencies to provide more flexibility

## [3.1.4] - 2024-12-26
### Changed
- bump version

## [3.1.3] - 2024-12-26
### Added
- Lock requirements using pip-tools

## [3.1.2] - 2024-12-18
### Added
- Support reading grpc middlewares from env and removing duplicates according to config middlewares

## [3.1.1] - 2023-08-21
### Added
- Support grpc reflection

## [3.1.0] - 2022-11-10
### Changed
- Upgrade depebdebcies to support python 3.10+
- Changed CI from Travis CI to Github Actions

## [3.0.0] - 2022-06-24
### Added
- Added multiprocessing worker class
### Changed
- Use cached_property from standard lib when possible


## [2.3.3] - 2022-04-22
### Added
- Added `post_ready` signal that will be sended after sea app is ready
- Added reading default config from environment variables, will overwrite the config file

## [2.3.2] - 2022-01-12
### Changed
- Update grpcio-tools requirement from <1.39.0,>=1.27.0 to >=1.27.0,<1.44.0

## [2.3.1] - 2021-06-01
### Fixed
- fix(version): fix unchanged version tag

## [2.3.0] - 2021-04-13
### Changed
- Update grpcio-tools requirement from <1.33.0,>=1.27.0 to >=1.27.0,<1.38.0

## [2.2.3] - 2020-10-09
### Changed
- change log level when load lib jobs
- fix test
- bump version

## [2.2.2] - 2020-09-28
### Changed
- Update __init__.py

## [2.2.1] - 2020-09-17
### Changed
- bump version

## [2.2.0] - 2020-03-13
### Changed
- update grpc version

## [2.1.0] - 2019-11-21
### Changed
- celery inspect 不调用 create_app

## [2.0.2] - 2019-10-15
### Changed
- bump version

## [2.0.1] - 2019-10-15
### Changed
- update travis ci

## [0.3.0] - 2017-08-16
