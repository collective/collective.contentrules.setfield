Changelog
=========

0.9.1 (2021-08-05)
------------------

- Fixed running setfield when using the `update_all` option instead of the object that triggered the content rule #27 [JeffersonBledsoe]
- Added black, isort and flake8 #28 [JeffersonBledsoe]


0.9.0 (2021-07-27)
------------------

- Initial release.
  [instification]

- Add configurable option to set values on all content that would match the executing rule.
  [instification]

- Add configurable option to preserve modification date of updated objects.
  [instification]

- Add 'Objects parent modified' trigger and handler to contentrules.
  [instification]

- Add unit tests.
  [JeffersonBledsoe]

- Ensure only dexterity fields can be set and values are valid or error thrown
  [djay]

- Fix bug where object with no workflow would prevent rule being fired
  [djay]
