# Simple Everhour CLI bassed Hour Reporting

Version 1.0.1

## Getting started

### Install the requirements

```shell
pip install -r requirements.txt
```

Add the folder to your $PATH variable

### Authenticate

1. Rename the everhour.ini.example to everhour.ini
2. Go to [https://app.everhour.com/#/account/profile](https://app.everhour.com/#/account/profile)
3. Copy the API Token into your clipboard
4. Edit the everhour.ini file and replace the example token

### List recent time log entries of current user

```shell
everhour log ls --limit 3
```

#### Output

```
------------------------------------------------------------------------------------------------------------------
| Date         | Project                        | Task                           | Task ID              | Hours  |
------------------------------------------------------------------------------------------------------------------
| 2018-05-19   | My Client                      | Setup Dev Server               | ev:164347293151111   | 5.00   |
| 2018-05-18   | My Client                      | Setup Dev Server               | ev:164347293151111   | 3.00   |
| 2018-05-17   | My Client                      | Setup Dev Server               | ev:164347293151111   | 5.00   |
------------------------------------------------------------------------------------------------------------------
```

### List all Projects

```shell
everhour projects ls
```

#### Output

```
-----------------------------------------------------------------
| Id                 | Name                                     |
-----------------------------------------------------------------
| ev:163263560641111 | Partner work                             |
| ev:163263561971111 | Product Work                             |
| ev:163263567591111 | Engineering work                         |
-----------------------------------------------------------------

```

### List all Projects matching a string

```shell
everhour projects ls product
```

```shell
-----------------------------------------------------------------
| Id                 | Name                                     |
-----------------------------------------------------------------
| ev:163263561971111 | Product Work                             |
-----------------------------------------------------------------

```

### List all tasks of projects

```shell
everhour tasks ls 163263561971111
````

#### Output

```·
----------------------------------------------------------------------------------------
| Id                 | Name                                     | Hours                |
----------------------------------------------------------------------------------------
| ev:163386356211111 | Project Managment                        | 55                   |
| ev:163499436211111 | Activity Tracking                        | 22                   |
| ev:164347293111111 | Setup Dev Server                         | 0                    |
----------------------------------------------------------------------------------------
```

### Log hours to a task today

```shell
everhour log add --task 164347293111111 --hours 3
```

### Log hours to a task on yesterday

```shell
everhour log add --task 164347293111111 --hours 3 --date yesterday
```

### Log hours to a task on monday

```shell
everhour log add --task 164347293111111 --hours 3 --date mon
```

### Log hours to a task on a given day

```shell
everhour log add --task 164347293111111 --hours 3 --date 2018-05-10
```

### Set hours to a task on a given day

```shell
everhour log set --task 164347293111111 --hours 3 --date 2018-05-10
```

## TODO's

- Create proper python package
- Add caching for profile, project and task lookups
- ...

Enjoy!
