# GHubby
GHubby collects the activities within the past 90 days of a user on GitHub by querying the API, which is accessed via a token. 
In case the token rate limit is reached, Ghubby sleeps until the rate limit is reset. 

GHubby is built on top of the GitHub backend of [chaoss/grimoirelab-perceval](https://github.com/chaoss/grimoirelab-perceval).

## How To

### Install
```
$> cd <...>/ghubby
$> python setup.py build
$> python setup.py install
```

### Execute

The parameters to execute **GHubby** are:
```
-u (--user), the login/username of a GitHub user                 [mandatory] 
-t (--api-token), a valid token to access the GitHub API         [mandatory] 
-d (--from-date), a starting date to collect the user activities [optional] 
```
Note that due to restriction on the GitHub API, **only the activities within the last 90 days can be collected.**

### Execute
```
$> cd <...>/ghubby/ghubby
$> python3 ghubby.py -u <username> -t <api-token> -d <from-date>
```

### Output
GHubby writes the collected events (see an example below) to the standard output. Every event contains information about the author (**actor** attribute) and the repository (**repo** and **repo_data** attributes) where
the event occurred, plus some additional data that depends on the type of event (e.g., pull request, commit, etc.).

```
...
{
    "actor": {
        "avatar_url": "https://avatars.githubusercontent.com/u/6515067?",
        "display_login": "valeriocos",
        "gravatar_id": "",
        "id": 6515067,
        "login": "valeriocos",
        "url": "https://api.github.com/users/valeriocos"
    },
    "created_at": "2018-04-13T15:44:38Z",
    "id": "7527041378",
    "payload": {
        "description": null,
        "master_branch": "master",
        "pusher_type": "user",
        "ref": "change-loading-identities",
        "ref_type": "branch"
    },
    "public": true,
    "repo": {
        "id": 116242339,
        "name": "valeriocos/GrimoireELK",
        "url": "https://api.github.com/repos/valeriocos/GrimoireELK"
    },
    "repo_data: {
      ...
    }
    "type": "CreateEvent"
}
...
```
