# The MIT License (MIT)
# Copyright (c) 2016-2026 HIS e. G.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from permissions.configDb import fetchLatestConfig
except ImportError:
    pass

from permissions.response import ret403, ret200


def matchesPattern(name, pattern):
    return bool(re.compile(pattern).match(name))


def matches(line, repository, branch, user, group, commitmsg):
    """parses a configuration line and returns whether it matches the current commit metadata"""

    line = line[1:]  # strip leading '+' or '-'
    s = line.split()
    if len(s) >= 6:
        msg = " ".join(s[5:])
        msg = msg[msg.find("|<| ") + 4:]
        badNews = msg
        goodNews = msg
    else:
        badNews = "Rejected."
        goodNews = "Accepted."

    if len(s) < 1 or matchesPattern(repository, s[0]):
        pass
    else:
        return (False, badNews)

    if len(s) < 2 or matchesPattern(branch, s[1]):
        pass
    else:
        return (False, badNews)

    if len(s) < 3 or matchesPattern(user, s[2]):
        pass
    else:
        return (False, badNews)

    if len(s) < 4 or matchesPattern(group, s[3]):
        pass
    else:
        return (False, badNews)

    if len(s) < 5 or matchesPattern(commitmsg, s[4]):
        pass
    else:
        return (False, badNews)

    return (True, goodNews)


def checkLines(conf, repository, branch, user, group, commitmsg):
    """returns whether conf allows a commit, paired with an explanatory message"""
    for line in conf.splitlines():
        line = line.strip()
        if line == "" or line.isspace() or line.startswith("#"):
            pass
        elif line.startswith("+"):
            accepted, message = matches(line, repository, branch, user, group, commitmsg)
            if accepted:
                return (True, message)
        elif line.startswith("-"):
            rejected, message = matches(line, repository, branch, user, group, commitmsg)
            if rejected:
                return (False, message)
        else:
            return (False, "Commit Stop Check: Malformed configuration.")
    return (False, "Commit Stop Check: Rejected by default.")


def matchesPatternSyntax(pattern):
    try:
        re.compile(pattern)
        return (True, "ok.")
    except re.error:
        return (False, f"The string '{pattern}' is not a pattern.")


def matchesSyntax(line):
    """parses a configuration line and returns whether it conforms to the syntax"""

    line = line[1:]  # strip leading '+' or '-'
    s = line.split()

    for i in range(min(len(s), 5)):
        ok, msg = matchesPatternSyntax(s[i])
        if not ok:
            return (False, msg)

    return (True, "ok.")


def checkLinesSyntax(conf):
    """parses a configuration file and returns whether it conforms to the syntax"""
    for line in conf.splitlines():
        line = line.strip()
        if line == "" or line.isspace() or line.startswith("#"):
            pass
        elif line.startswith("+"):
            syntaxIsOkay, syntaxMsg = matchesSyntax(line)
            if not syntaxIsOkay:
                return (False, syntaxMsg)
        elif line.startswith("-"):
            syntaxIsOkay, syntaxMsg = matchesSyntax(line)
            if not syntaxIsOkay:
                return (False, syntaxMsg)
        else:
            return (False, f"The line '{line}' does not start with '#', '+' or '-'.")
    return (True, "ok.")


def checkPrivilege2(arguments):
    """checks whether the requested commit is allowed"""
    if "repository" not in arguments:
        return (False, "Commit Stop Check: no repository given")
    elif "branch" not in arguments:
        return (False, "Commit Stop Check: no branch given")
    elif "user" not in arguments:
        return (False, "Commit Stop Check: no user given")
    else:
        repository = arguments["repository"][0] if isinstance(arguments["repository"], list) else arguments["repository"]
        branch = arguments["branch"][0] if isinstance(arguments["branch"], list) else arguments["branch"]
        user = arguments["user"][0] if isinstance(arguments["user"], list) else arguments["user"]
        group = ""
        if "group" in arguments:
            group = arguments["group"][0] if isinstance(arguments["group"], list) else arguments["group"]
        commitmsg = ""
        if "commitmsg" in arguments:
            commitmsg = arguments["commitmsg"][0] if isinstance(arguments["commitmsg"], list) else arguments["commitmsg"]

        conf = fetchLatestConfig()
        return checkLines(conf, repository, branch, user, group, commitmsg)


def checkPrivilege(arguments):
    """interprets a GET request and returns whether the current permissions allow to commit"""
    allowed, message = checkPrivilege2(arguments)
    if allowed:
        ret200(message)
    else:
        ret403(message)
