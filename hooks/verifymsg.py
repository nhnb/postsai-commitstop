#!/usr/bin/env python3

'''
 -- commit permission check for CVS

This script should be invoked by the verifymsg file in CVSROOT.

.* /usr/local/bin/verifymsg.py --repository=nameofrepo --url=https://example.com/postsai/extensions/commitstop/api.py --msgfile=%l

@author:     nhnb
@license:    MIT
'''

import base64
import getopt
import http.client
import os
import re
import subprocess
import sys
import urllib.parse


class PermissionChecker:

    def __init__(self):
        self.urls = []
        self.repository = None
        self.msg_file = None

    def read_commandline_arguments(self):
        """parse command line arguments"""

        try:
            opts, args = getopt.getopt(sys.argv[1:], "", ["url=", "repository=", "msgfile="])
        except:
            print("Command line: --repository=name --url=https://example.com/postsai/extensions/commitstop/api.py --msgfile=%l")
            sys.exit(2)

        for o, a in opts:
            if o == "--url":
                self.urls.append(a)
            elif o == "--repository":
                self.repository = a
            elif o == "--msgfile":
                self.msg_file = a

        if self.repository is None or len(self.urls) == 0:
            print("Command line: --repository=name --url=https://example.com/postsai/extensions/commitstop/api.py --msgfile=%l")
            sys.exit(2)


    def read_user(self):
        """ reads author from $CVS_USER or $USER"""

        if "CVS_USER" in os.environ:
            self.user = os.environ["CVS_USER"]
        else:
            self.user = os.environ["USER"]


    def read_branch(self):
        """Read the branchname by invoking cvsstatus"""

        self.branch = "HEAD"

        cvs = subprocess.Popen(["/usr/bin/cvs", "-qn", "status"],
                               stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
        stdout = cvs.communicate()[0].decode()
        for row in stdout.splitlines():
            if "Sticky Tag:" in row:
                m = re.search(r"[ \t]*Sticky Tag:[ \t]*([^( \t]*)", row)
                branch = m.group(1)
                if branch != "(none)" and branch != "":
                    self.branch = branch
                return


    def read_commitmsg(self):
        with open(self.msg_file, "r") as f:
            self.commitmsg = f.read()



    def generate_query_string(self):
        """generates the url query string based on previously read information"""

        return "repository=" + urllib.parse.quote(self.repository) \
            + "&branch=" + urllib.parse.quote(self.branch) \
            + "&user=" + urllib.parse.quote(self.user) \
            + "&commitmsg=" + urllib.parse.quote(self.commitmsg[0:7000])


    def query_webservice(self):
        urlsuffix = "?" + self.generate_query_string()

        for url in self.urls:
            u = urllib.parse.urlparse(url)

            # Connect to server
            if u.scheme == "https":
                con = http.client.HTTPSConnection(u.hostname, u.port)
            else:
                con = http.client.HTTPConnection(u.hostname, u.port)

            # Send request
            headers = {"Content-Type": "application/json"}
            if u.username is not None and u.password is not None:
                credentials = base64.b64encode(f"{u.username}:{u.password}".encode()).decode()
                headers["Authorization"] = "Basic " + credentials
            url_prefix = u.scheme + "://" + u.hostname + u.path
            con.request("GET", url_prefix + urlsuffix, None, headers)

            # Verify response, forward messages, set exit code
            response = con.getresponse()
            print(response.read().decode())
            if response.status != 200:
                sys.exit(1)

        sys.exit(0)


def main(argv=None):
    checker = PermissionChecker()
    checker.read_commandline_arguments()
    checker.read_user()
    checker.read_branch()
    checker.read_commitmsg()
    checker.query_webservice()


if __name__ == "__main__":
    sys.exit(main())
