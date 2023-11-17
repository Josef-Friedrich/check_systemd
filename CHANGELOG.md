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

### Changed

- The options `--dead-timers`, `--dead-timers-warning` and
  `--dead-timers-critical` have been renamed to `--timers`,
  `--timers-warning` and `--timers-critical`
- In the command line help, the options have been grouped according to
  their monitoring scope.

### Removed

- The options `-i`, `--ignore-inactive-state` have been removed.

## [2.2.1] - 2020-10-27

### Fixed

- Make the plugin compatible with systemd 246 (#10)

## [2.2.0] - 2020-05-27

### Added

- New option `-n, --no-startup-time` to disable the startup time check (#7).

## [2.1.0] - 2020-05-16

### Added
