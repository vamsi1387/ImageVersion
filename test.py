#! /usr/bin/env python
from __future__ import print_function
import os,subprocess,sys
class FileVersioning(object):
  __slots__ = ["val"]
  def __init__(self, value=''):
    self.val = value
  def setValue(self, value=None):
    self.val = value
    return value

def GetVariable(name, local=locals()):
  if name in local:
    return local[name]
  if name in globals():
    return globals()[name]
  return None

def Make(name, local=locals()):
  ret = GetVariable(name, local)
  if ret is None:
    ret = FileVersioning(0)
    globals()[name] = ret
  return ret


Make("gitdir").setValue(os.popen("git rev-parse --git-dir").read().rstrip("\n"))
print(gitdir.val)

Make("hook").setValue(os.popen(str(gitdir.val)+"/hooks/post-commit").read().rstrip("\n"))

# disable post-commit hook temporarily
#os.chmod('hook', 0o744)
