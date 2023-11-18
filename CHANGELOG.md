# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0] - 2023-11-18

### Added

- The options `--include`, `--include-unit`, `--include-type`,
  `--exclude`, `--exclude-unit`, `--exclude-type` have been added to
  have better control over which units should be selected for testing.
- A new entry was added to the performance data: `data_source=cli` or
  `data_source=dbus`
- Add example `icinga2` configuration for the plugin (#23)
- New option to query user units (`--user`) (#22)
- New option `--required` to set the state that the systemd unit must have (#17)

### Changed

- The options `--dead-timers`, `--dead-timers-warning` and
  `--dead-timers-critical` have been renamed to `--timers`,
  `--timers-warning` and `--timers-critical`.
- In the command line help, the options have been grouped according to
  their monitoring scope.
- Always return perfdata for `startup_time` even with `-n` (#27)
- Exit `Unknown` when importing `nagiosplugin` fails (#24)

### Removed

- The options `-i`, `--ignore-inactive-state` have been removed.
- Drop support for 3.6 and 3.7

## [2.3.1] - 2021-03-03

### Fixed

- Clean up the documentation

### Removed

- Remove the systemd source to avoid confusion (#13)

## [2.3.0] - 2021-01-15

### Added

- Add option `--ignore-inactive-state` to prevent `check_systemd` from triggering a critical state

## [2.2.1] - 2020-10-27

### Fixed

- Make the plugin compatible with systemd 246 (#10)

## [2.2.0] - 2020-05-27

### Added

- New option `-n, --no-startup-time` to disable the startup time check (#7).

## [2.1.0] - 2020-05-16

### Added

- Exclude units using regular expressions

## [2.0.11] - 2020-03-20

### Fixed

- Versioning
- Documentation (README)

## [2.0.10] - 2020-03-19

### Fixed

- Fix KeyError 'not-found'

## [2.0.9] - 2019-08-05

### Fixed

- Parse milliseconds in timespan strings (#3)

## [2.0.8] - 2019-05-26

### Fixed

- Boot not finished

## [2.0.7] - 2019-05-26

## Added

- Tests to test bootup not finisched

## [2.0.6] - 2019-04-13

### Added

- Documentation

### Fixed

- Version number

## [2.0.5] - 2019-04-13

### Fixed

- `start_time` performance data

## [2.0.4] - 2019-04-08

### Fixed

- startup time on raspbian

## [2.0.3] - 2019-04-07

### Added

- New option `--version`
- Check startup time
- performance data

## [2.0.2] - 2019-04-06

### Fixed

- Fix setup.py

## [2.0.1] - 2019-04-06

### Fixed

- Fix setup.py

## [2.0.0] - 2019-04-06

### Added

- Added an --exclude option to exclude some systemd units from the checks

## [1.2.0] - 2018-07-31

## [1.1.1] - 2017-07-14

## [1.1.0] - 2016-09-26

## [1.0.4] - 2016-09-01

## [1.0.2] - 2015-07-30

## [1.0.1] - 2015-07-15
