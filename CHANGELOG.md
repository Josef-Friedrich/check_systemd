# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

<small>[Compare with latest](https://github.com/Josef-Friedrich/check_systemd/compare/v4.1.1...HEAD)</small>

## [v4.1.1] - 2024-11-02

<small>[Compare with v0.4.0](https://github.com/Josef-Friedrich/check_systemd/compare/v4.1.0...v4.1.1)</small>

### Added

- Add support for Python 3.13

### Changed

- Updated `contrib/icinga2/command.conf` to support latest commands and harmonize with Icinga 2 ITL upstream.
  The two variables `systemd_dead_timer_warning` and `systemd_dead_timer_critical` were renamed to `systemd_dead_timers_warning` and `systemd_dead_timers_critical`, respectively.
- Fix typos in the help output

## [v4.1.0] - 2024-03-01

<small>[Compare with v0.4.0](https://github.com/Josef-Friedrich/check_systemd/compare/v4.0.0...v4.1.0)</small>

### Added

- Add basic debug support (--debug) ([f371f78](https://github.com/Josef-Friedrich/check_systemd/commit/f371f78256bd0a407156abf7a507a3bdd4fcf328) by Josef Friedrich).

### Fixed

- Fix check response for stopped units and units selected with --unit ([dd79ced](https://github.com/Josef-Friedrich/check_systemd/commit/dd79ceddcb23b7924b52c38e916aeea40a2d058e) by Josef Friedrich).

## [v4.0.0] - 2024-02-20

<small>[Compare with v3.1.0](https://github.com/Josef-Friedrich/check_systemd/compare/v3.1.0...v4.0.0)</small>

### Changed

- Switch the testing framework to pytest ([a0aa63c](https://github.com/Josef-Friedrich/check_systemd/commit/a0aa63c0ff0aad038d9cc7f484cd7eee50744db5) by Josef Friedrich)

### Fixed

- Fix the readthedocs site ([a7cf474](https://github.com/Josef-Friedrich/check_systemd/commit/a7cf4741500a981773d48d5f065ee5379828462e) by Josef Friedrich).
- Fix some type hint issues in the tests ([1e2b135](https://github.com/Josef-Friedrich/check_systemd/commit/1e2b135e92f919135eb7d937320d7878822ba99f) by Josef Friedrich).

### Removed

- Remove the perfdata `data_source` ([62fd828](https://github.com/Josef-Friedrich/check_systemd/commit/62fd828177c9372a5234314e354ca9a442e726bb) by Josef Friedrich).

## [v3.1.0] - 2024-01-04

### Added

- (Re)add the options `-i`, `--ignore-inactive-state` (#31).

## [v3.0.0] - 2023-11-18

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

## [v2.3.1] - 2021-03-03

### Fixed

- Clean up the documentation

### Removed

- Remove the systemd source to avoid confusion (#13)

## [v2.3.0] - 2021-01-15

### Added

- Add option `--ignore-inactive-state` to prevent `check_systemd` from triggering a critical state

## [v2.2.1] - 2020-10-27

### Fixed

- Make the plugin compatible with systemd 246 (#10)

## [v2.2.0] - 2020-05-27

### Added

- New option `-n, --no-startup-time` to disable the startup time check (#7).

## [v2.1.0] - 2020-05-16

### Added

- Exclude units using regular expressions

## [v2.0.11] - 2020-03-20

### Fixed

- Versioning
- Documentation (README)

## [v2.0.10] - 2020-03-19

### Fixed

- Fix KeyError 'not-found'

## [v2.0.9] - 2019-08-05

### Fixed

- Parse milliseconds in timespan strings (#3)

## [v2.0.8] - 2019-05-26

### Fixed

- Boot not finished

## [v2.0.7] - 2019-05-26

## Added

- Tests to test bootup not finisched

## [v2.0.6] - 2019-04-13

### Added

- Documentation

### Fixed

- Version number

## [v2.0.5] - 2019-04-13

### Fixed

- `start_time` performance data

## [v2.0.4] - 2019-04-08

### Fixed

- startup time on raspbian

## [v2.0.3] - 2019-04-07

### Added

- New option `--version`
- Check startup time
- performance data

## [v2.0.2] - 2019-04-06

### Fixed

- Fix setup.py

## [v2.0.1] - 2019-04-06

### Fixed

- Fix setup.py

## [v2.0.0] - 2019-04-06

### Added

- Added an --exclude option to exclude some systemd units from the checks

## [v1.2.0](https://github.com/Josef-Friedrich/check_systemd/releases/tag/v1.2.0) - 2018-07-30

<small>[Compare with V1.1.1](https://github.com/Josef-Friedrich/check_systemd/compare/V1.1.1...v1.2.0)</small>

### Added

- Added custom Summary class to handle status line output Added verbosity flag ([79d4a3b](https://github.com/Josef-Friedrich/check_systemd/commit/79d4a3b4c314a250d461473b5766b8d0217fcbf2) by spike).

## [v1.1.1](https://github.com/Josef-Friedrich/check_systemd/releases/tag/V1.1.1) - 2017-07-14

<small>[Compare with v1.1.0](https://github.com/Josef-Friedrich/check_systemd/compare/v1.1.0...V1.1.1)</small>

### Removed

- Remove global service variable ([daeb929](https://github.com/Josef-Friedrich/check_systemd/commit/daeb92963238c88e4e8ffa471d1da80fd9a5a0a4) by Adam Cécile).

## [v1.1.0](https://github.com/Josef-Friedrich/check_systemd/releases/tag/v1.1.0) - 2016-09-26

<small>[Compare with v1.0.4](https://github.com/Josef-Friedrich/check_systemd/compare/v1.0.4...v1.1.0)</small>

### Added

- Added Parsing option for testing a single Systemd-service ([a1d2af0](https://github.com/Josef-Friedrich/check_systemd/commit/a1d2af0a78015684b554c83604d572ce43b6b283) by Felix Buehler).

### Changed

- changed from optionparse to argparse ([0ef5153](https://github.com/Josef-Friedrich/check_systemd/commit/0ef5153c4c38067b0ebdfe15d76d1cedc8b1316b) by Felix Buehler).

## [v1.0.4](https://github.com/Josef-Friedrich/check_systemd/releases/tag/v1.0.4) - 2016-08-31

<small>[Compare with v1.0.2](https://github.com/Josef-Friedrich/check_systemd/compare/v1.0.2...v1.0.4)</small>

### Added

- add execute permissions ([3f4df49](https://github.com/Josef-Friedrich/check_systemd/commit/3f4df496610edd37ba617f3879352cca5069a78f) by Felix Buehler).

### Fixed

- Fix python path ([2c9e835](https://github.com/Josef-Friedrich/check_systemd/commit/2c9e8353d6a8dac730b95e3750c11e9f3e893a03) by Andrea Briganti).

## [v1.0.2](https://github.com/Josef-Friedrich/check_systemd/releases/tag/v1.0.2) - 2015-07-30

<small>[Compare with v1.0.1](https://github.com/Josef-Friedrich/check_systemd/compare/v1.0.1...v1.0.2)</small>

## [v1.0.1](https://github.com/Josef-Friedrich/check_systemd/releases/tag/v1.0.1) - 2015-07-15

<small>[Compare with first commit](https://github.com/Josef-Friedrich/check_systemd/compare/9dbe9d1332fb82a65fdfb98bb81c44f48c9be680...v1.0.1)</small>
