# swing_dance_scores

This is a web interface for performing relative placement, a common scoring mechanism used in [Swing Dancing](https://en.wikipedia.org/wiki/Swing_(dance)) competitions.

Please also see our [wiki](https://github.com/paul-tqh-nguyen/swing_dance_scores/wiki) for additional information.

We have a [brief explanation of relative placement on our wiki](https://github.com/paul-tqh-nguyen/swing_dance_scores/wiki/Relative-Placement-Explanation). 

For further explanation on how relative placement works, see [some of the external resources on the topic that we found insightful](https://github.com/paul-tqh-nguyen/swing_dance_scores/wiki/Useful-External-Resources).

## Architecture

This repository provides functionality for a front-facing interface that'll perform relative scoring.

The front end and scoring mechanisms are implemented in [React](https://en.wikipedia.org/wiki/React_(web_framework)) & [Javascript](https://en.wikipedia.org/wiki/JavaScript).

Our serverside fucntionality for storing and updating results utilizes [Firebase](https://en.wikipedia.org/wiki/Firebase).

We use [Python](https://en.wikipedia.org/wiki/Python_(programming_language)) for scripting and glue code.

## Instructions For Use

See the sub-sections below for details on how to use the provided functionalities.

### Utilizing Our Front End Interfaces

We can use the following command to utilize our front end functionality.
```
./swing_dance_scores.py -start-front-end-server
```

This starts a server to serve our web application.

Information will be printed about the URI relevant to access our web application (the URI will be something like http://localhost:3000/).

### Deployment Instructions

If local changes are made to the front end functionality, we can deploy them to our demo site at https://paul-tqh-nguyen.github.io/swing_dance_scores/ via the following command:
```
./swing_dance_scores.py -deploy
```

## Troubleshooting Tips

This section contains some tips for troubleshooting any installation or run-time problems. 

All of the notes below stem from troubles repoted by our end users and are stored on our [wiki](https://github.com/paul-tqh-nguyen/swing_dance_scores/wiki).

This list is incomplete. 

Trouble Shooting Tips:
* [Linux Lamentations](https://github.com/paul-tqh-nguyen/swing_dance_scores/wiki/Linux-Lamentations)

