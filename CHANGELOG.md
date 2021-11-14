# Changelog
All notable changes to webferea will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

Features:

- entry: change title link to open in blank tab
- entry: change link filter to replace lazy loading img src attributes
- entry: set the max with of the detail page to 100vw!important
- entry: save the windows scrollX in the browsers local storage, to save the reading progress
- entry: delete all local storage entries with menu button
- feed: change highlight color of an item, if it has a reading progress

Fixes:

- entry: change regex for the iframe filter, to catch iframes with different formatting
- link filter: don't interpret links that start with "//" as relative
- link filter: fix ignoring of links that contains "/" inside
- show read: default variable was not converted the right way


## [2.2.0] - 2021-04-18

Features:

- sync: add optional bz2 compression to the database transfer
- deployment: add scripts for docker and docker-compose
- entry: use full fetched post from the metadata table and not the preview from the feed
- entry: filter out script-tags with src outside the posts domain
- client: add --verbose parameter to enable debug outputs
- theme: remove padding in flash message
- theme: make the items on the list a bit more compact

Fixes:

- db: catch error, if database is not synced yet
- auth: check if the username and password values in the config are not empty
- helpers: don't crash if last_updated file was not found
- entry: change relative urls to absolute urls too


## [2.1.0] - 2021-04-01

- filter iframes out of the items, because they cause trouble
- change relative urls in posts to absolute urls
- change action buttons from post to get (where possible)
- make header and footer sticky
- add status in footer

## 2.0.0 - 2021-03-28

- Refactor whole application
- New design and layout
- Replace ssh sync with http-basicauth

## 1.0.0 - 2017-07-26

- Initial release

[Unreleased]: https://github.com/CydNoxzed/webferea2/compare/2.2.0...HEAD
[2.2.0]: https://github.com/CydNoxzed/webferea2/compare/2.1.0...2.2.0
[2.1.0]: https://github.com/CydNoxzed/webferea2/compare/2.0.0...2.1.0
