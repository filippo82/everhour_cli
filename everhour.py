#!/usr/bin/env python
"""
This is the template for a script file. Please change this docstring to reflect
realities.
"""
import argparse
from configparser import ConfigParser
import logging
import os
import sys
import tempfile
import time

import requests
import datetime

try:
    import ujson as json
except ImportError:
    import json


# Script version. It's recommended to increment this with every change, to make
# debugging easier.
VERSION = "1.0.1"
BASE_URL = "https://api.everhour.com"

# Set up logging.
log = logging.getLogger("{0}[{1}]".format(os.path.basename(sys.argv[0]), os.getpid()))


def run():
    """Main entry point run by __main__ below. No need to change this usually."""
    args = parse_args()
    setup_logging(args)
    config = get_config(args)

    log.debug("Starting process (version %s).", VERSION)
    log.debug("Arguments: %r", args)

    # run the application
    try:
        main(args, config)
    except Exception:
        log.exception("Processing error")


def main(args, config):
    """
    The main method. Any exceptions are caught outside of this method and will
    be handled.
    """

    global API_KEY
    API_KEY = config.get("everhour", "token")
    args.func(**vars(args))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        help="Show additional information.",
        default=0,
    )
    parser.add_argument("--log-file", dest="log_file", help="Log file on disk.")
    parser.add_argument(
        "--config-file",
        dest="config_file",
        help="Configuration file to read settings from.",
    )

    subparsers = parser.add_subparsers(help="sub-command help")

    # projects
    projects = subparsers.add_parser("projects", help="Commands related to projects")
    projects_sub = projects.add_subparsers(help="sub-command help")
    projects_ls = projects_sub.add_parser("ls", help="list all projects")
    projects_ls.add_argument("query", nargs="?")
    projects_ls.set_defaults(func=list_projects)

    # tasks
    tasks = subparsers.add_parser("tasks", help="Commands related to tasks")
    tasks_sub = tasks.add_subparsers(help="sub-command help")
    tasks_ls = tasks_sub.add_parser("ls", help="list all tasks")
    tasks_ls.add_argument("project", nargs="?")
    tasks_ls.set_defaults(func=list_tasks)

    # set time
    tlog = subparsers.add_parser("log", help="Commands related to time logging")

    log_sub = tlog.add_subparsers(help="sub-command help")
    log_set = log_sub.add_parser("set", help="set logged hours for a day")
    log_set.add_argument("--task", required=True, type=str)
    log_set.add_argument("--hours", required=True, type=float)
    log_set.add_argument(
        "--date",
        type=str,
        default="today",
        help="date formated as 2018-01-20, defaults to today",
    )
    log_set.set_defaults(func=set_time)

    # set time
    log_add = log_sub.add_parser("add", help="add logged hours for a day")
    log_add.add_argument("--task", required=True, type=str)
    log_add.add_argument("--hours", required=True, type=float)
    log_add.add_argument(
        "--date",
        type=str,
        default="today",
        help="date formated as 2018-01-20, defaults to today, also supports "
        "mon, tue, wed, thu, fri, sat, sun",
    )
    log_add.set_defaults(func=add_time)

    # set time
    log_ls = log_sub.add_parser("ls", help="list recently logged time")
    log_ls.add_argument(
        "--limit", default=20, type=int, help="Limit of records, default 20"
    )
    log_ls.set_defaults(func=log_recent)

    return parser.parse_args()


def parse_date(date):
    """
    Validates and transform date string from user
    """

    if date in ["today", "now"]:
        date = datetime.now()
    elif date == "yesterday":
        date = datetime.now().subtract(days=1)
    elif date in ["su", "sun", "sunday"]:
        date = datetime.now().replace(weekday=0)
    elif date in ["mo", "mon", "monday"]:
        date = datetime.now().replace(weekday=1)
    elif date in ["tu", "tue", "tuesday"]:
        date = datetime.now().replace(weekday=2)
    elif date in ["we", "wed", "wednesday"]:
        date = datetime.now().replace(weekday=3)
    elif date in ["th", "thu", "thursday"]:
        date = datetime.now().replace(weekday=4)
    elif date in ["fr", "fri", "friday"]:
        date = datetime.now().replace(weekday=5)
    elif date in ["sa", "sat", "saturday"]:
        date = datetime.now().replace(weekday=6)
    else:
        date = datetime.date(date)

    return date.format("YYYY-MM-DD")


def get_profile():
    """
    Gets current users profile
    """

    return get("/users/me")


def get_project(project_id):
    """
    Gets a project by id
    """

    return get("/projects/{0}".format(project_id))


def log_recent(limit, **kwargs):
    user = get_profile()
    ret = get("/users/{0}/time?limit={1}&offset=0".format(user["id"], limit))
    log.debug("%s", json.dumps(ret, indent=2))

    log.info(
        "--%s---%s---%s---%s---%s--",
        "".ljust(12, "-"),
        "".ljust(30, "-"),
        "".ljust(30, "-"),
        "".ljust(20, "-"),
        "".ljust(6, "-"),
    )
    log.info(
        "| %s | %s | %s | %s | %s |",
        "Date".ljust(12),
        "Project".ljust(30),
        "Task".ljust(30),
        "Task ID".ljust(20),
        "Hours".ljust(6),
    )
    log.info(
        "--%s---%s---%s---%s---%s--",
        "".ljust(12, "-"),
        "".ljust(30, "-"),
        "".ljust(30, "-"),
        "".ljust(20, "-"),
        "".ljust(6, "-"),
    )

    for task in ret:
        project = get_project(task["task"]["projects"][0])

        log.info(
            "| %s | %s | %s | %s | %s |",
            task["date"].ljust(12),
            project["name"].ljust(30)[0:30],
            task["task"]["name"].ljust(30)[0:30],
            task["task"]["id"].ljust(20),
            seconds_to_str(task["time"]).ljust(6),
        )

    log.info(
        "--%s---%s---%s---%s---%s--",
        "".ljust(12, "-"),
        "".ljust(30, "-"),
        "".ljust(30, "-"),
        "".ljust(20, "-"),
        "".ljust(6, "-"),
    )


def seconds_to_str(seconds):
    hours = float(seconds / 60 / 60)
    return "{0:.2f}".format(hours)


def set_time(task, hours, date, **kwargs):

    date = parse_date(date)

    if not "ev:" in task:
        task = "ev:{0}".format(task)

    seconds = hours * 60 * 60

    user = get_profile()

    data = {"time": seconds, "date": date, "user": user["id"]}

    ret = put("/tasks/{0}/time".format(task), data)

    if "time" in ret["task"]:
        total_hours = ret["task"]["time"]["total"]
        if total_hours:
            total_hours = seconds_to_str(total_hours)

        if str(user["id"]) in ret["task"]["time"]["users"]:
            user_hours = ret["task"]["time"]["users"][str(user["id"])]
            if user_hours:
                user_hours = seconds_to_str(user_hours)
        else:
            user_hours = 0
    else:
        total_hours = 0
        user_hours = 0

    log.info("Set your hours for %s to %i to %s", date, hours, ret["task"]["name"])
    log.info("Task total: %s hours", total_hours)
    log.info("Your total: %s hours", user_hours)


def add_time(task, hours, date, **kwargs):

    date = parse_date(date)

    if not "ev:" in task:
        task = "ev:{0}".format(task)

    seconds = hours * 60 * 60
    user = get_profile()

    data = {"time": seconds, "date": date, "user": user["id"]}

    ret = post("/tasks/{0}/time".format(task), data)

    if "time" in ret["task"]:
        total_hours = ret["task"]["time"]["total"]
        if total_hours:
            total_hours = seconds_to_str(total_hours)

        if str(user["id"]) in ret["task"]["time"]["users"]:
            user_hours = ret["task"]["time"]["users"][str(user["id"])]
            if user_hours:
                user_hours = seconds_to_str(user_hours)
        else:
            user_hours = 0
    else:
        total_hours = 0
        user_hours = 0

    log.info("Set your hours for %s to %i to %s", date, hours, ret["task"]["name"])
    log.info("Task total: %s hours", total_hours)
    log.info("Your total: %s hours", user_hours)


def list_projects(query, **kwargs):
    """
    List all available projects
    """
    if not query:
        query = ""

    ret = get("/projects?limit=&query={0}&platform=".format(query))

    log.debug("%s", json.dumps(ret, indent=2))

    log.info("--%s---%s--", "".ljust(18, "-"), "".ljust(40, "-"))
    log.info("| %s | %s |", "Id".ljust(18), "Name".ljust(40))
    log.info("--%s---%s--", "".ljust(18, "-"), "".ljust(40, "-"))

    for project in ret:
        log.info("| %s | %s |", project["id"].ljust(18), project["name"].ljust(40))

    log.info("--%s---%s--", "".ljust(18, "-"), "".ljust(40, "-"))


def get_task(task_id):
    """
    Get a task by id
    """
    return get("/tasks/{0}".format(task_id))


def list_tasks(project, **kwargs):
    """
    List all available tasks
    """

    if project is None:
        log.error("Please specify a project id, check --help for details")
        quit(1)

    if not "ev:" in project:
        project = "ev:{0}".format(project)

    ret = get("/projects/{0}/tasks".format(project))
    log.debug("%s", json.dumps(ret, indent=2))

    log.info(
        "--%s---%s---%s--", "".ljust(18, "-"), "".ljust(40, "-"), "".ljust(20, "-")
    )
    log.info("| %s | %s | %s |", "Id".ljust(18), "Name".ljust(40), "Hours".ljust(20))
    log.info(
        "--%s---%s---%s--", "".ljust(18, "-"), "".ljust(40, "-"), "".ljust(20, "-")
    )

    for task in ret:

        hours = 0

        if "time" in task:
            if "total" in task["time"]:
                seconds = task["time"]["total"]
                hours = seconds_to_str(seconds)

        log.info(
            "| %s | %s | %s |",
            task["id"].ljust(18),
            task["name"].ljust(40),
            str(hours).ljust(20),
        )

    log.info(
        "--%s---%s---%s--", "".ljust(18, "-"), "".ljust(40, "-"), "".ljust(20, "-")
    )


def get(path):
    """
    Run a everhour GET request
    """

    uri = "{0}{1}".format(BASE_URL, path)
    headers = {"x-api-key": API_KEY}

    r = requests.get(url=uri, headers=headers)

    if r.status_code != 200:
        log.error("Failed to GET %s Error Code: %s: %s", uri, r.status_code, r.text)
        quit(1)

    ret = r.json()
    return ret


def put(path, data):
    """
    Run a everhour PUT request
    """

    uri = "{0}{1}".format(BASE_URL, path)
    headers = {"x-api-key": API_KEY, "content-type": "application/json"}

    r = requests.put(url=uri, headers=headers, data=json.dumps(data))

    if r.status_code != 200:
        log.error("Failed to GET %s Error Code: %s: %s", uri, r.status_code, r.text)
        quit(1)

    ret = r.json()
    return ret


def post(path, data):
    """
    Run a everhour PUT request
    """

    uri = "{0}{1}".format(BASE_URL, path)
    headers = {"x-api-key": API_KEY, "content-type": "application/json"}

    r = requests.post(url=uri, headers=headers, data=json.dumps(data))

    if r.status_code not in [200, 201]:
        log.error("Failed to GET %s Error Code: %s: %s", uri, r.status_code, r.text)
        quit(1)

    ret = r.json()
    return ret


def setup_logging(args):
    """Set up logging based on the command line options."""
    # Set up logging
    fmt = "%(message)s"
    if args.verbose == 0:
        level = logging.INFO
        logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(
            logging.WARN
        )
    elif args.verbose >= 1:
        level = logging.DEBUG
    else:
        # default value
        level = logging.INFO
        logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(
            logging.WARN
        )

    # configure the logging system
    if args.log_file:
        out_dir = os.path.dirname(args.log_file)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)
        logging.basicConfig(
            filename=args.log_file, filemode="a", level=level, format=fmt
        )
    else:
        logging.basicConfig(level=level, format=fmt)

    # Log time in UTC
    logging.Formatter.converter = time.gmtime


def get_config(args):
    """Parse the config file and return a ConfigParser object.

    Always reads the `main.ini` file in the current directory (`main` is
    replaced by the current basename of the script).
    """
    cfg = ConfigParser()

    root, _ = os.path.splitext(__file__)
    files = [root + ".ini"]
    if args.config_file:
        files.append(args.config_file)

    log.debug("Reading config files: %r", files)
    cfg.read(files)
    return cfg


# This is run if this script is executed, rather than imported.
if __name__ == "__main__":
    run()
