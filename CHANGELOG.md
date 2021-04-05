# Changelog
All notable changes to webferea will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Features

- entry: use full fetched post from the metadata table and not the preview from the feed
- entry: filter out script-tags with src outside the posts domain
- client: add --verbose parameter to enable debug outputs
- theme: remove padding in flash message
- theme: make the items on the list a bit more compact


### Fixes

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

[Unreleased]: https://github.com/CydNoxzed/webferea2/compare/2.1.0...HEAD
[2.1.0]: https://github.com/CydNoxzed/webferea2/compare/2.0.0...2.1.0
