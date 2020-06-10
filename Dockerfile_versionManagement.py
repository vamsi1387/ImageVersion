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

def addVersion (_p1,_p2) :
    global ver
    global type
    global dotCount
    global majorVersion
    global minorVersion
    global patchVersion

    Make("ver").setValue(_p1)
    if (str(_p2) == '' ):
        Make("type").setValue("PATCH")
    else:
        Make("type").setValue(os.popen("echo "+str(_p2)+" | tr [a-z] [A-Z]").read().rstrip("\n"))
    dotCount=FileVersioning(os.popen("echo "+str(_p1)+" | tr -cd \".\"| wc -c").read().rstrip("\n"))
    #if there is no version tag yet, let's start at 0.0.0
    if ( str(ver.val) == '' or str(ver.val) == "<none>" ):
	#No existing version, starting at 0.0.0
        print("0.0.0")
        exit()
    if (int(dotCount.val) == 0 ):
        Make("ver").setValue(os.popen("expr "+str(ver.val)+" + 1").read().rstrip("\n"))
    else:
        if (int(dotCount.val) == 2 ):
            Make("majorVersion").setValue(os.popen("echo "+str(_p1)+" | cut -d \".\" -f1").read().rstrip("\n"))
            Make("minorVersion").setValue(os.popen("echo "+str(_p1)+" | cut -d \".\" -f2").read().rstrip("\n"))
            Make("patchVersion").setValue(os.popen("echo "+str(_p1)+" | cut -d \".\" -f3").read().rstrip("\n"))
            if (str(type.val) == "PATCH" ):
                Make("patchVersion").setValue(os.popen("expr "+str(patchVersion.val)+" + 1").read().rstrip("\n"))
            elif (str(type.val) == "MINOR" ):
                Make("minorVersion").setValue(os.popen("expr "+str(minorVersion.val)+" + 1").read().rstrip("\n"))
            else:
                Make("majorVersion").setValue(os.popen("expr "+str(majorVersion.val)+" + 1").read().rstrip("\n"))
                Make("minorVersion").setValue(0)
                Make("patchVersion").setValue(0)
            Make("ver").setValue(str(majorVersion.val)+"."+str(minorVersion.val)+"."+str(patchVersion.val))
        elif (int(dotCount.val) == 1 ):
            Make("majorVersion").setValue(os.popen("echo "+str(_p1)+" | cut -d \".\" -f1").read().rstrip("\n"))
            Make("patchVersion").setValue(os.popen("echo "+str(_p1)+" | cut -d \".\" -f2").read().rstrip("\n"))
            if (str(type.val) == "PATCH" ):
                Make("patchVersion").setValue(os.popen("expr "+str(patchVersion.val)+" + 1").read().rstrip("\n"))
            elif (str(type.val) == "MINOR" ):
                Make("minorVersion").setValue(os.popen("expr "+str(minorVersion.val)+" + 1").read().rstrip("\n"))
            else:
                Make("majorVersion").setValue(os.popen("expr "+str(majorVersion.val)+" + 1").read().rstrip("\n"))
                Make("patchVersion").setValue(0)
            Make("ver").setValue(str(majorVersion.val)+"."+str(patchVersion.val))
    return ver.val



USERNAME=FileVersioning("vamsi1387")
IMAGE=FileVersioning("helloworld")
TYPE=FileVersioning("PATCH")
_rc0 = subprocess.call(["docker image pull -a "+str(USERNAME.val)+"/"+str(IMAGE.val)],shell=True)

Make("OLD_VERSION").setValue(os.popen("docker images | grep -w "+str(IMAGE.val)+" |grep -iv latest |  awk '{print $2}' | sort -V | tail -1").read().rstrip("\n"))
print("OLD_VERSION:"+str(OLD_VERSION.val))
Make("NEW_VERSION").setValue(addVersion(str(OLD_VERSION.val),str(TYPE.val)))
print("New_Version: "+str(NEW_VERSION.val))

#building the image
_rc0 = subprocess.call(["docker build -t "+str(USERNAME.val)+"/"+str(IMAGE.val)+":latest ."],shell=True)
# tag it
_rc0 = subprocess.call(["git tag -a "+str(NEW_VERSION.val)+" -m 'version'"],shell=True)
_rc0 = subprocess.call(["git push --tags"],shell=True)
_rc0 = subprocess.call(["docker tag "+str(USERNAME.val)+"/"+str(IMAGE.val)+":latest "+str(USERNAME.val)+"/"+str(IMAGE.val)+":"+str(NEW_VERSION.val)],shell=True)
# push it
_rc0 = subprocess.call(["docker rmi -f "+str(USERNAME.val)+"/"+str(IMAGE.val)+":latest"],shell=True)
_rc0 = subprocess.call(["docker push "+str(USERNAME.val)+"/"+str(IMAGE.val)+":"+str(NEW_VERSION.val)],shell=True)
