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


n = len(sys.argv)
if n == 1:
        print("Usage: python "+sys.argv[0]+"  <Docker_Username> <Image_Name> <Release_Type>")
        print("\tRelease_Type can be major/minor/patch")
        print("Example: python "+sys.argv[0]+"  vamsi1387 helloworld patch")
        exit()
elif n==3:
        Make("USERNAME").setValue(sys.argv[1])
	Make("IMAGE").setValue(sys.argv[2])
        Make("TYPE").setValue("PATCH")
elif n==4:
        Make("USERNAME").setValue(sys.argv[1])
	Make("IMAGE").setValue(sys.argv[2])
        Make("TYPE").setValue(sys.argv[3])

#USERNAME=FileVersioning("vamsi1387")
#IMAGE=FileVersioning("helloworld")
#TYPE=FileVersioning("PATCH")
_rc0 = subprocess.call(["docker image pull -a "+str(USERNAME.val)+"/"+str(IMAGE.val)],shell=True)

Make("OLD_VERSION").setValue(os.popen("docker images | grep -w "+str(IMAGE.val)+" |grep -iv latest |  awk '{print $2}' | sort -V | tail -1").read().rstrip("\n"))
print("OLD_VERSION:"+str(OLD_VERSION.val))
Make("NEW_VERSION").setValue(addVersion(str(OLD_VERSION.val),str(TYPE.val)))
print("New_Version: "+str(NEW_VERSION.val))

#building the image
_rc0 = subprocess.call(["docker build -t "+str(USERNAME.val)+"/"+str(IMAGE.val)+":latest ."],shell=True)

Make("gitdir").setValue(os.popen("git rev-parse --git-dir").read().rstrip("\n"))
hook=str(gitdir.val)+"/hooks/post-commit"
# disable post-commit hook temporarily
os.chmod(hook, 0o644)

# tag it
_rc0 = subprocess.call(["git add -A"],shell=True)
_rc0 = subprocess.call(["git commit --amend -m 'version '"+str(NEW_VERSION.val)],shell=True)
_rc0 = subprocess.call(["git tag -a "+str(NEW_VERSION.val)+" -m 'version'"+str(NEW_VERSION.val)],shell=True)
_rc0 = subprocess.call(["git push -f"],shell=True)
_rc0 = subprocess.call(["git push --tags"],shell=True)
_rc0 = subprocess.call(["docker tag "+str(USERNAME.val)+"/"+str(IMAGE.val)+":latest "+str(USERNAME.val)+"/"+str(IMAGE.val)+":"+str(NEW_VERSION.val)],shell=True)

# enable it again
os.chmod(hook, 0o755)

# push the images to docker repo
_rc0 = subprocess.call(["docker push "+str(USERNAME.val)+"/"+str(IMAGE.val)+":latest"],shell=True)
_rc0 = subprocess.call(["docker push "+str(USERNAME.val)+"/"+str(IMAGE.val)+":"+str(NEW_VERSION.val)],shell=True)
