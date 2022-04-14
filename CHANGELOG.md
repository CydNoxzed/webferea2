# Changelog
All notable changes to webferea will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

Features: 

- theme/w3css: don't show pagination if there is only one page



## [2.4.0] - 2022-03-13

Features:

- main: change infobar to statistic dict
- entry: always fetch the scraped content of the entry, if possible
- entry: use [bleach](https://github.com/mozilla/bleach) to clean the html of the feed entry
- entry: show author in entry
- feed: add total count to pagination
- theme/w3css: add new theme

Changes:
- theme: move theme into separate directory and the possibility to change the theme
- api: change post-fields for settings and entry modification in template and backend

Fixes: 

- auth: fix redirect and don't redirect to "/None"

Theme w3css:

- [w3css.com](https://www.w3schools.com/w3css/) as foundation
- [fontawesome 4.7](https://fontawesome.com/v4/) for the icons 
- size of 140kb of the static layout files (10x more than the default theme)
- size of html per call is lower than the default theme
- Bulk read/mark of entries in the feed
- Toggle for light- and dark-mode
- Toggle for serif and san-serif font


## [2.3.0] - 2022-01-15

Features:

- entry: change title link to open in blank tab
- entry: change link filter to replace lazy loading img src attributes
- entry: set the max with of the detail page to 100vw!important
- entry: save the windows scrollX in the browsers local storage, to save the reading progress
- entry: delete all local storage entries with menu button
- feed: change highlight color of an item, if it has a reading progress
- main: Navigation moved from the header into the footer
- db: allow a folder as node name in the configuration to fetch all feeds that are directly in this folder
- login: redirect to requested page after login

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

[Unreleased]: https://github.com/CydNoxzed/webferea2/compare/2.4.0...HEAD
[2.4.0]: https://github.com/CydNoxzed/webferea2/compare/2.3.0...2.4.0
[2.3.0]: https://github.com/CydNoxzed/webferea2/compare/2.2.0...2.3.0
[2.2.0]: https://github.com/CydNoxzed/webferea2/compare/2.1.0...2.2.0
[2.1.0]: https://github.com/CydNoxzed/webferea2/compare/2.0.0...2.1.0
