# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.4.0] - 2023-11-17

### Added

- The options `--include`, `--include-unit`, `--include-type`,
  `--exclude`, `--exclude-unit`, `--exclude-type` have been added to
  have better control over which units should be selected for testing.
- A new entry was added to the performance data: `data_source=cli` or
  `data_source=dbus`
- Add example `icinga2` configuration for command (#23)
- New option to query user units (`--user`) (#22)
- New option `--required` to set the state that the systemd unit must have (#17)

### Changed

- The options `--dead-timers`, `--dead-timers-warning` and
  `--dead-timers-critical` have been renamed to `--timers`,
  `--timers-warning` and `--timers-critical`
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
