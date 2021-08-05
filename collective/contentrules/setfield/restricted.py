# -*- coding:utf-8 -*-
from AccessControl import allow_type, ModuleSecurityInfo
from RestrictedPython import compile_restricted

import AccessControl.ZopeGuards as ZopeGuards
import datetime
import re


# Make useful modules visible
for name in ("datetime", "time", "re"):
    ModuleSecurityInfo(name).setDefaultAccess("allow")
# Include their key types
allow_type(type(re.compile("")))
allow_type(type(re.match("x", "x")))
allow_type(type(datetime.date))  # Make sure we get class methods
allow_type(type(datetime.datetime))  # class methods
allow_type(type(datetime.date(2017, 1, 1)))
allow_type(type(datetime.datetime(2017, 1, 1)))
allow_type(type(datetime.timedelta(1)))


class PyScript(object):
    # set up this way in case we want to do some caching at some
    # point in the future.

    def __init__(self, code):
        self.code = compile_restricted(code, "<string>", "exec")

    def execute(self, my_locals=None, output=None):
        my_globals = ZopeGuards.get_safe_globals()
        my_globals["_getattr_"] = ZopeGuards.guarded_getattr
        if my_locals is None:
            my_locals = {}
        exec(self.code, my_globals, my_locals)
        return my_locals
