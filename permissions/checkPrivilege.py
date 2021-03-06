# The MIT License (MIT)
# Copyright (c) 2016-2018 HIS e. G.
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

import sys
import os
import re

# ugly but necessary: also find packages at the root of the package tree
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    import config
    from permissions.configDb import fetchLatestConfig
except ImportError:
    pass

from response import ret403
from response import ret200



def matchesPattern(name, pattern):
    return bool(re.compile(pattern).match(name))


def matches(line, repository, branch, user, group, commitmsg):
    """ parses a configuration line and returns whether it matches the current commit metadata"""

    line = line[1:]  # strip leading '+' or '-'
    s = line.split()
    if(len(s) >= 6):
        msg = " ".join(s[5:])
        msg = msg[msg.find("|<| ") + 4:]
        badNews = msg
        goodNews = msg
    else:
        badNews = "Rejected."
        goodNews = "Accepted."

    if len(s) < 1 or matchesPattern(repository, s[0]):
        pass
    else: return (False, badNews)

    if len(s) < 2 or matchesPattern(branch, s[1]):
        pass
    else: return (False, badNews)

    if len(s) < 3 or matchesPattern(user, s[2]):
        pass
    else: return (False, badNews)

    if len(s) < 4 or matchesPattern(group, s[3]):
        pass
    else: return (False, badNews)

    if len(s) < 5 or matchesPattern(commitmsg, s[4]):
        pass
    else: return (False, badNews)

    return (True, goodNews)


def checkLines(conf, repository, branch, user, group, commitmsg):
        """ returns whether conf allows a commit, paired with an explanatory message"""
        for line in conf.splitlines():
            line = line.strip()
            # With Windows clients, empty lines were not recognized.
            # This might be due to some strange Unicode whitespace characters that require decoding
            if line is "" or line.decode(encoding='UTF-8', errors='ignore').isspace() or line.startswith("#"):
                pass
            elif line.startswith("+"):
                (accepted, message) = matches(line, repository, branch, user, group, commitmsg)
                if accepted: return (True, message)
            elif line.startswith("-"):
                (rejected, message) = matches(line, repository, branch, user, group, commitmsg)
                if rejected: return (False, message)
            else:
                return (False, "Commit Stop Check: Malformed configuration.")
        return (False, "Commit Stop Check: Rejected by default.")


def matchesPatternSyntax(pattern):
    try:
        re.compile(pattern)
        return (True, "ok.")
    except re.error:
        return (False, "The string '" + pattern + "' is not a pattern.")
                

def matchesSyntax(line):
    """ parses a configuration line and returns whether it conforms to the syntax"""

    line = line[1:]  # strip leading '+' or '-'
    s = line.split()

    (ok0, msg0) = matchesPatternSyntax(s[0])
    if len(s) < 1 or ok0:
        pass
    else: return (False, msg0)

    (ok1, msg1) = matchesPatternSyntax(s[1])
    if len(s) < 2 or matchesPatternSyntax(s[1]):
        pass
    else: return (False, msg1)

    (ok2, msg2) =  matchesPatternSyntax(s[2]);
    if len(s) < 3 or ok2:
        pass
    else: return (False, msg2)

    (ok3, msg3) =  matchesPatternSyntax(s[3]);
    if len(s) < 4 or ok3:
        pass
    else: return (False, msg3)

    (ok4, msg4) =  matchesPatternSyntax(s[4]);
    if len(s) < 5 or ok4:
        pass
    else: return (False, msg4)

    return (True, "ok.")


def checkLinesSyntax(conf):
        """ parses a configuration file and returns whether it conforms to the syntax"""
        for line in conf.splitlines():
            line = line.strip()
            # With Windows clients, empty lines were not recognized.
            # This might be due to some strange Unicode whitespace characters that require decoding
            if line is "" or line.decode(encoding='UTF-8', errors='ignore').isspace() or line.startswith("#"):
                pass
            elif line.startswith("+"):
                (syntaxIsOkay, syntaxMsg) = matchesSyntax(line)
                if not syntaxIsOkay: return (False, syntaxMsg)
            elif line.startswith("-"):
                (syntaxIsOkay, syntaxMsg) = matchesSyntax(line)
                if not syntaxIsOkay: return (False, syntaxMsg)
            else:
                return (False, "The line '"+line+"' does not start with '#', '+' or '-'.")
        return (True, "ok.")


def checkPrivilege2(arguments):
    """ checks whether the requested commit is allowed """
    if not arguments.__contains__("repository"):
        return(False, "Commit Stop Check: no repository given")
    elif not arguments.__contains__("branch"):
        return (False, "Commit Stop Check: no branch given")
    elif not arguments.__contains__("user"):
        return (False, "Commit Stop Check: no user given")
    else:
        repository = arguments["repository"].value
        branch = arguments["branch"].value
        user = arguments["user"].value
        if arguments.__contains__("group"):
            group = arguments["group"].value
        else:
            group = ""
        if arguments.__contains__("commitmsg"):
            commitmsg = arguments["commitmsg"].value
        else:
            commitmsg = ""
        
        conf = fetchLatestConfig()
        return checkLines(conf, repository, branch, user, group, commitmsg)


def checkPrivilege(arguments):
    """ interprets a GET request and returns whether the current permissions allow to commit """
    allowed, message = checkPrivilege2(arguments)
    if allowed:
        ret200(message)
    else: ret403(message)
