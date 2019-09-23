#!/bin/bash
# Ignore E309:
#   Add missing blank line (after class declaration).
# PEP8 is ambiguous here.
# http://www.python.org/dev/peps/pep-0008/#blank-lines
# In "Blank Lines":
#  Method definitions inside a class are separated by a single blank line.
# Autopep8 interprets this to mean "add a line after the class
# declaration."  There already is sufficient visual separation when a
# docstring follows, and PEP8 won't catch this, so ignore it for now.
autofix () {
    autopep8 -r --in-place $1 --ignore=E309
}

autofix fwd_api
autofix test
