# Changelog

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
