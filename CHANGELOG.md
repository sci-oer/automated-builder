# Changelog

## [v0.10.0](https://github.com/sci-oer/automated-builder/releases/v0.10.0) (2023-02-18)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.9.1...v0.10.0)

**Merged pull requests:**

- chore\(deps\): update docker/build-push-action action to v4 [\#171](https://github.com/sci-oer/automated-builder/pull/171) ([renovate[bot]](https://github.com/apps/renovate))
- fix: linter errors [\#170](https://github.com/sci-oer/automated-builder/pull/170) ([MarshallAsch](https://github.com/MarshallAsch))
- chore\(deps\): update dependency requests to v2.28.2 [\#169](https://github.com/sci-oer/automated-builder/pull/169) ([renovate[bot]](https://github.com/apps/renovate))
- chore\(deps\): bump gitpython from 3.1.27 to 3.1.30 [\#168](https://github.com/sci-oer/automated-builder/pull/168) ([dependabot[bot]](https://github.com/apps/dependabot))
- chore\(deps\): update pypa/gh-action-pypi-publish action to v1.6.4 [\#166](https://github.com/sci-oer/automated-builder/pull/166) ([renovate[bot]](https://github.com/apps/renovate))
- chore\(deps\): update dependency docker to v6.0.1 [\#165](https://github.com/sci-oer/automated-builder/pull/165) ([renovate[bot]](https://github.com/apps/renovate))
- chore\(deps\): update dependency gitpython to v3.1.31 [\#147](https://github.com/sci-oer/automated-builder/pull/147) ([renovate[bot]](https://github.com/apps/renovate))

## [v0.9.1](https://github.com/sci-oer/automated-builder/releases/v0.9.1) (2022-10-23)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.9.0...v0.9.1)

**Merged pull requests:**

- fix: remove unsuported buildx platforms [\#164](https://github.com/sci-oer/automated-builder/pull/164) ([MarshallAsch](https://github.com/MarshallAsch))

## [v0.9.0](https://github.com/sci-oer/automated-builder/releases/v0.9.0) (2022-10-23)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.8.2...v0.9.0)

**Implemented enhancements:**

- Use docker heath check status instead of polling the wiki to see if the container is ready [\#153](https://github.com/sci-oer/automated-builder/issues/153)
- Confirm that multi arch builds from within a docker container [\#123](https://github.com/sci-oer/automated-builder/issues/123)
- Check that buildx is avalible before starting a multi arch build.  [\#122](https://github.com/sci-oer/automated-builder/issues/122)
- Multi architecture builds [\#109](https://github.com/sci-oer/automated-builder/issues/109)
- feat: if the container supports health checks wait for healthcheck [\#159](https://github.com/sci-oer/automated-builder/pull/159) ([MarshallAsch](https://github.com/MarshallAsch))

**Merged pull requests:**

- feat: check to see if buildx is enabled on startup [\#162](https://github.com/sci-oer/automated-builder/pull/162) ([MarshallAsch](https://github.com/MarshallAsch))
- fix: add missing docker cli and buildx plugin when running in docker [\#160](https://github.com/sci-oer/automated-builder/pull/160) ([MarshallAsch](https://github.com/MarshallAsch))
- feat: add type hints and pytype config file [\#157](https://github.com/sci-oer/automated-builder/pull/157) ([MarshallAsch](https://github.com/MarshallAsch))

## [v0.8.2](https://github.com/sci-oer/automated-builder/releases/v0.8.2) (2022-10-22)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.8.1...v0.8.2)

**Merged pull requests:**

- fix: double quoted [\#156](https://github.com/sci-oer/automated-builder/pull/156) ([MarshallAsch](https://github.com/MarshallAsch))

## [v0.8.1](https://github.com/sci-oer/automated-builder/releases/v0.8.1) (2022-10-22)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.8.0...v0.8.1)

**Fixed bugs:**

- fix: setuptools in docker image fails to get version number [\#155](https://github.com/sci-oer/automated-builder/pull/155) ([MarshallAsch](https://github.com/MarshallAsch))

## [v0.8.0](https://github.com/sci-oer/automated-builder/releases/v0.8.0) (2022-10-19)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.7.0...v0.8.0)

**Implemented enhancements:**

- Add interupt handler to gracefully handle ctrl-c [\#137](https://github.com/sci-oer/automated-builder/issues/137)
- feat: gracefully handle shutdown on sigint [\#151](https://github.com/sci-oer/automated-builder/pull/151) ([MarshallAsch](https://github.com/MarshallAsch))

**Closed issues:**

- student proof install/running [\#37](https://github.com/sci-oer/automated-builder/issues/37)

**Merged pull requests:**

- fix: used the container before it was created [\#152](https://github.com/sci-oer/automated-builder/pull/152) ([MarshallAsch](https://github.com/MarshallAsch))
- Package new [\#149](https://github.com/sci-oer/automated-builder/pull/149) ([MarshallAsch](https://github.com/MarshallAsch))
- chore: remove unneeded packages from requirements.txt [\#148](https://github.com/sci-oer/automated-builder/pull/148) ([MarshallAsch](https://github.com/MarshallAsch))

## [v0.7.0](https://github.com/sci-oer/automated-builder/releases/v0.7.0) (2022-09-07)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.6.0...v0.7.0)

**Merged pull requests:**

- feat: allow custom message of the day file to be specified [\#143](https://github.com/sci-oer/automated-builder/pull/143) ([MarshallAsch](https://github.com/MarshallAsch))

## [v0.6.0](https://github.com/sci-oer/automated-builder/releases/v0.6.0) (2022-09-04)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.5.1...v0.6.0)

**Merged pull requests:**

- feat: add cli option to configure the url of the external lectures server so future lite and full images can be built [\#141](https://github.com/sci-oer/automated-builder/pull/141) ([MarshallAsch](https://github.com/MarshallAsch))

## [v0.5.1](https://github.com/sci-oer/automated-builder/releases/v0.5.1) (2022-09-04)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.5.0...v0.5.1)

**Implemented enhancements:**

- chore: copy the lecture content last for ease of future compatibility with full/lite images [\#140](https://github.com/sci-oer/automated-builder/pull/140) ([MarshallAsch](https://github.com/MarshallAsch))

**Fixed bugs:**

- fix: removed trailing .CONTAINER that got left behind in the ssh key file path when cleaning up the wiki [\#139](https://github.com/sci-oer/automated-builder/pull/139) ([MarshallAsch](https://github.com/MarshallAsch))

## [v0.5.0](https://github.com/sci-oer/automated-builder/releases/v0.5.0) (2022-09-03)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.4.0...v0.5.0)

**Implemented enhancements:**

- remove the lectures subdirectory [\#127](https://github.com/sci-oer/automated-builder/issues/127)
- enable / dissable comments with a flag [\#117](https://github.com/sci-oer/automated-builder/issues/117)
- feat: add flag to enable or dissable wiki comments [\#135](https://github.com/sci-oer/automated-builder/pull/135) ([MarshallAsch](https://github.com/MarshallAsch))

**Fixed bugs:**

- crashes if no ssh key file is provided [\#121](https://github.com/sci-oer/automated-builder/issues/121)
- Automated builder doesn't stop the docker container it runs [\#111](https://github.com/sci-oer/automated-builder/issues/111)
- fix: gracefully recover if a git clone is unsuccessful [\#133](https://github.com/sci-oer/automated-builder/pull/133) ([MarshallAsch](https://github.com/MarshallAsch))
- fix: no longer crashes if an ssh key file is not specified [\#132](https://github.com/sci-oer/automated-builder/pull/132) ([MarshallAsch](https://github.com/MarshallAsch))

**Merged pull requests:**

- feat: change ownership and copy files at the same time to reduce the number of image layers [\#136](https://github.com/sci-oer/automated-builder/pull/136) ([MarshallAsch](https://github.com/MarshallAsch))
- feat: allow custom ssh options to be passed to the git clone command using the  envirionment variable [\#134](https://github.com/sci-oer/automated-builder/pull/134) ([MarshallAsch](https://github.com/MarshallAsch))

## [v0.4.0](https://github.com/sci-oer/automated-builder/releases/v0.4.0) (2022-09-01)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.3.1...v0.4.0)

**Implemented enhancements:**

- be able toi change to none or  or  [\#118](https://github.com/sci-oer/automated-builder/issues/118)
- Move docker check before the interactive input [\#106](https://github.com/sci-oer/automated-builder/issues/106)
- feat: add the ability to configure the wiki site navigation mode [\#131](https://github.com/sci-oer/automated-builder/pull/131) ([MarshallAsch](https://github.com/MarshallAsch))

**Fixed bugs:**

- Lectures using -keepgit [\#110](https://github.com/sci-oer/automated-builder/issues/110)
- Expand ssh key path before trying to use it [\#108](https://github.com/sci-oer/automated-builder/issues/108)
- \[BUG\] Package is not correctly including the dockerfile [\#86](https://github.com/sci-oer/automated-builder/issues/86)
- fix: expand ssh key path name before it is used [\#113](https://github.com/sci-oer/automated-builder/pull/113) ([MarshallAsch](https://github.com/MarshallAsch))
- fix: change ownership of the letures directory to be owned by the student user [\#112](https://github.com/sci-oer/automated-builder/pull/112) ([MarshallAsch](https://github.com/MarshallAsch))
- feat: move check for docker daemon beofre interactive input prompt [\#107](https://github.com/sci-oer/automated-builder/pull/107) ([MarshallAsch](https://github.com/MarshallAsch))

**Merged pull requests:**

- Multi arch [\#129](https://github.com/sci-oer/automated-builder/pull/129) ([MarshallAsch](https://github.com/MarshallAsch))
- Update dependency colorlog to v6.7.0 [\#128](https://github.com/sci-oer/automated-builder/pull/128) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency websocket-client to v1.4.0 [\#126](https://github.com/sci-oer/automated-builder/pull/126) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency urllib3 to v1.26.12 [\#125](https://github.com/sci-oer/automated-builder/pull/125) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency charset-normalizer to v2.1.1 [\#124](https://github.com/sci-oer/automated-builder/pull/124) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency docker to v6 [\#119](https://github.com/sci-oer/automated-builder/pull/119) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency pycodestyle to v2.9.1 [\#105](https://github.com/sci-oer/automated-builder/pull/105) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency flake8 to v5.0.4 [\#104](https://github.com/sci-oer/automated-builder/pull/104) ([renovate[bot]](https://github.com/apps/renovate))
- fix: strip the .github folder out of the src dist [\#103](https://github.com/sci-oer/automated-builder/pull/103) ([MarshallAsch](https://github.com/MarshallAsch))
- fix: pass the correct application version to docker build [\#102](https://github.com/sci-oer/automated-builder/pull/102) ([MarshallAsch](https://github.com/MarshallAsch))

## [v0.3.1](https://github.com/sci-oer/automated-builder/releases/v0.3.1) (2022-08-01)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.3.0...v0.3.1)

**Fixed bugs:**

- fix: add manifest file to include dockerfile in sdist [\#101](https://github.com/sci-oer/automated-builder/pull/101) ([MarshallAsch](https://github.com/MarshallAsch))

## [v0.3.0](https://github.com/sci-oer/automated-builder/releases/v0.3.0) (2022-08-01)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.2.1...v0.3.0)

**Implemented enhancements:**

- Add interactive mode for the auto builder [\#96](https://github.com/sci-oer/automated-builder/issues/96)
- Check to make sure docker is running before starting, issue warning if it is not.  [\#83](https://github.com/sci-oer/automated-builder/issues/83)
- add workflow to automatically increase the semantic version number [\#70](https://github.com/sci-oer/automated-builder/issues/70)
- add workflow to automatically create a GH release [\#69](https://github.com/sci-oer/automated-builder/issues/69)
- add workflow to deploy pip package [\#68](https://github.com/sci-oer/automated-builder/issues/68)
- Create Changelog [\#67](https://github.com/sci-oer/automated-builder/issues/67)
- Pass ssh private key as volume mount to sci-oer container [\#51](https://github.com/sci-oer/automated-builder/issues/51)
- Automatically upload the image to a specified registry [\#44](https://github.com/sci-oer/automated-builder/issues/44)
- feat: Add the option for interactive input for the builder options [\#100](https://github.com/sci-oer/automated-builder/pull/100) ([MarshallAsch](https://github.com/MarshallAsch))
- feat\(flag\): can now push to a docker registry without auth or with pre configured credentials [\#94](https://github.com/sci-oer/automated-builder/pull/94) ([MarshallAsch](https://github.com/MarshallAsch))

**Fixed bugs:**

- ensure git is installed on system as installation dependancy [\#97](https://github.com/sci-oer/automated-builder/issues/97)
- fix\(dep\): exit gracefully if git is not installed on the system [\#98](https://github.com/sci-oer/automated-builder/pull/98) ([MarshallAsch](https://github.com/MarshallAsch))

**Security fixes:**

- Update dependency urllib3 to v1.26.11 [\#80](https://github.com/sci-oer/automated-builder/pull/80) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency requests to v2.28.1 [\#79](https://github.com/sci-oer/automated-builder/pull/79) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency websocket-client to v1.3.3 [\#78](https://github.com/sci-oer/automated-builder/pull/78) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency charset-normalizer to v2.1.0 [\#77](https://github.com/sci-oer/automated-builder/pull/77) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency certifi to v2022.6.15 [\#76](https://github.com/sci-oer/automated-builder/pull/76) ([renovate[bot]](https://github.com/apps/renovate))
- Update actions/setup-python action to v4 [\#75](https://github.com/sci-oer/automated-builder/pull/75) ([renovate[bot]](https://github.com/apps/renovate))

**Merged pull requests:**

- Update dependency flake8 to v5.0.1 [\#99](https://github.com/sci-oer/automated-builder/pull/99) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency flake8 to v5 [\#93](https://github.com/sci-oer/automated-builder/pull/93) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency pycodestyle to v2.9.0 [\#92](https://github.com/sci-oer/automated-builder/pull/92) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency pyflakes to v2.5.0 [\#91](https://github.com/sci-oer/automated-builder/pull/91) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency attrs to v22 [\#90](https://github.com/sci-oer/automated-builder/pull/90) ([renovate[bot]](https://github.com/apps/renovate))
- Update pypa/gh-action-pypi-publish action to v1.5.1 [\#89](https://github.com/sci-oer/automated-builder/pull/89) ([renovate[bot]](https://github.com/apps/renovate))

## [v0.2.1](https://github.com/sci-oer/automated-builder/releases/v0.2.1) (2022-07-31)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.2.0...v0.2.1)

## [v0.2.0](https://github.com/sci-oer/automated-builder/releases/v0.2.0) (2022-07-31)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/v0.1.2...v0.2.0)

**Breaking changes:**

- fix!: fixed ssh key loading, removed support for specifying the ssh private key in plain text [\#88](https://github.com/sci-oer/automated-builder/pull/88) ([MarshallAsch](https://github.com/MarshallAsch))

**Implemented enhancements:**

- Import lectures from local directory [\#71](https://github.com/sci-oer/automated-builder/issues/71)
- feat: import lectures from local directory or from git repo [\#87](https://github.com/sci-oer/automated-builder/pull/87) ([MarshallAsch](https://github.com/MarshallAsch))

**Fixed bugs:**

- \[BUG\] ssh key path only worked with public keys [\#85](https://github.com/sci-oer/automated-builder/issues/85)
- \[BUG\] ssh key does not accept absolute paths  [\#84](https://github.com/sci-oer/automated-builder/issues/84)

## [v0.1.2](https://github.com/sci-oer/automated-builder/releases/v0.1.2) (2022-06-23)

[Full Changelog](https://github.com/sci-oer/automated-builder/compare/5031ac982e8ac94b04d30b8ad0f7ad625227d7fa...v0.1.2)

**Implemented enhancements:**

- Create pip package for the builder [\#52](https://github.com/sci-oer/automated-builder/issues/52)
- Automatically export the image as a tar archive [\#43](https://github.com/sci-oer/automated-builder/issues/43)
- Do not clone single practiceProblems repo into sub directory [\#66](https://github.com/sci-oer/automated-builder/pull/66) ([MarshallAsch](https://github.com/MarshallAsch))

**Fixed bugs:**

- location of practice problems [\#53](https://github.com/sci-oer/automated-builder/issues/53)
- The git ssh host does not automaticly get accepted and it requires user intervention [\#49](https://github.com/sci-oer/automated-builder/issues/49)
- Will not use git credentials for private repos [\#48](https://github.com/sci-oer/automated-builder/issues/48)
- node/knex version [\#47](https://github.com/sci-oer/automated-builder/issues/47)

**Security fixes:**

- Update dependency requests to v2.28.0 [\#72](https://github.com/sci-oer/automated-builder/pull/72) ([renovate[bot]](https://github.com/apps/renovate))
- Update actions/checkout action to v3 [\#65](https://github.com/sci-oer/automated-builder/pull/65) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency certifi to v2022 [\#62](https://github.com/sci-oer/automated-builder/pull/62) ([renovate[bot]](https://github.com/apps/renovate))
- Update docker/setup-buildx-action action to v2 [\#61](https://github.com/sci-oer/automated-builder/pull/61) ([renovate[bot]](https://github.com/apps/renovate))
- Update docker/login-action action to v2 [\#60](https://github.com/sci-oer/automated-builder/pull/60) ([renovate[bot]](https://github.com/apps/renovate))
- Update docker/build-push-action action to v3 [\#59](https://github.com/sci-oer/automated-builder/pull/59) ([renovate[bot]](https://github.com/apps/renovate))
- Update docker/setup-qemu-action action to v2 [\#58](https://github.com/sci-oer/automated-builder/pull/58) ([renovate[bot]](https://github.com/apps/renovate))
- Update docker/metadata-action action to v4 [\#57](https://github.com/sci-oer/automated-builder/pull/57) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency pyparsing to v3.0.9 [\#50](https://github.com/sci-oer/automated-builder/pull/50) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency websocket-client to v1.3.2 [\#42](https://github.com/sci-oer/automated-builder/pull/42) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency urllib3 to v1.26.9 [\#30](https://github.com/sci-oer/automated-builder/pull/30) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency websocket-client to v1.3.1 [\#28](https://github.com/sci-oer/automated-builder/pull/28) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency GitPython to v3.1.27 [\#27](https://github.com/sci-oer/automated-builder/pull/27) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency charset-normalizer to v2.0.12 [\#26](https://github.com/sci-oer/automated-builder/pull/26) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency tomli to v2.0.1 [\#25](https://github.com/sci-oer/automated-builder/pull/25) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency mccabe to v0.7.0 [\#24](https://github.com/sci-oer/automated-builder/pull/24) ([renovate[bot]](https://github.com/apps/renovate))
- Update dependency charset-normalizer to v2.0.11 [\#16](https://github.com/sci-oer/automated-builder/pull/16) ([renovate[bot]](https://github.com/apps/renovate))
- Configure Renovate [\#15](https://github.com/sci-oer/automated-builder/pull/15) ([renovate[bot]](https://github.com/apps/renovate))

**Closed issues:**

- Add docker build instructions [\#63](https://github.com/sci-oer/automated-builder/issues/63)
- configure and build docker container [\#54](https://github.com/sci-oer/automated-builder/issues/54)
- gradle vs gradlew [\#39](https://github.com/sci-oer/automated-builder/issues/39)
- docker desktop "open in browser" [\#38](https://github.com/sci-oer/automated-builder/issues/38)
- command prompt default [\#36](https://github.com/sci-oer/automated-builder/issues/36)
- home directory for student user [\#35](https://github.com/sci-oer/automated-builder/issues/35)
- su from root after startup? [\#34](https://github.com/sci-oer/automated-builder/issues/34)
- video streaming [\#33](https://github.com/sci-oer/automated-builder/issues/33)
- Change mapped drive structure [\#31](https://github.com/sci-oer/automated-builder/issues/31)
- Set and document the ssh credential heiarchy.  [\#23](https://github.com/sci-oer/automated-builder/issues/23)
- Load the ssh key dirrectly from an envirionment variable  [\#22](https://github.com/sci-oer/automated-builder/issues/22)
- Load the ssh key file from an envirionment variable  [\#21](https://github.com/sci-oer/automated-builder/issues/21)
- Load git ssh key directly from a specified key [\#20](https://github.com/sci-oer/automated-builder/issues/20)
- Load git ssh credentials from a specified key file [\#19](https://github.com/sci-oer/automated-builder/issues/19)
- Add preseed content for the worked examples [\#14](https://github.com/sci-oer/automated-builder/issues/14)
- Use graphql api to configure the wiki title [\#13](https://github.com/sci-oer/automated-builder/issues/13)
- Figureout how to preseed the wiki content by modifying the wiki.js storage dirrectly [\#12](https://github.com/sci-oer/automated-builder/issues/12)
- Allow the builder to be run on the docker host [\#9](https://github.com/sci-oer/automated-builder/issues/9)
- Add labels to the main docker file [\#8](https://github.com/sci-oer/automated-builder/issues/8)
- Fill in the information for the community profile [\#7](https://github.com/sci-oer/automated-builder/issues/7)
- Fill in the README [\#6](https://github.com/sci-oer/automated-builder/issues/6)
- Add a CI pipeline to generate the docker image [\#3](https://github.com/sci-oer/automated-builder/issues/3)
- Add cli flags to pass options into the script [\#2](https://github.com/sci-oer/automated-builder/issues/2)
-  Automate setup of wiki seed content [\#1](https://github.com/sci-oer/automated-builder/issues/1)

**Merged pull requests:**

- Contributing docs [\#41](https://github.com/sci-oer/automated-builder/pull/41) ([MarshallAsch](https://github.com/MarshallAsch))
- Revert "Update dependency mccabe to v0.7.0" [\#29](https://github.com/sci-oer/automated-builder/pull/29) ([MarshallAsch](https://github.com/MarshallAsch))
- 4 add linter [\#18](https://github.com/sci-oer/automated-builder/pull/18) ([MarshallAsch](https://github.com/MarshallAsch))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
