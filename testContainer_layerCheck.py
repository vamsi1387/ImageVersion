#!/usr/bin/env python
from __future__ import print_function
import os,subprocess,sys
	
class ImageVersioning(object):
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
    ret = ImageVersioning(0)
    globals()[name] = ret
  return ret

def Array(value):
  if isinstance(value, list):
    return value
  if isinstance(value, basestring):
    return value.strip().split(' ')
  return [ value ]

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
    dotCount=ImageVersioning(os.popen("echo "+str(_p1)+" | tr -cd \".\"| wc -c").read().rstrip("\n"))
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
            if (str(type.val) == "PATCH" or str(type.val) == "MINOR"):
            	Make("patchVersion").setValue(os.popen("expr "+str(patchVersion.val)+" + 1").read().rstrip("\n"))
	    else:
                Make("majorVersion").setValue(os.popen("expr "+str(majorVersion.val)+" + 1").read().rstrip("\n"))
                Make("minorVersion").setValue(0)
                Make("patchVersion").setValue(0)
	    Make("ver").setValue(str(majorVersion.val)+"."+str(patchVersion.val))
    return ver.val



containerid=ImageVersioning(os.popen("docker container ls | grep -v CONTAINER | awk '{print $1}'").read().rstrip("\n"))
if (str(containerid.val) == '' ):
    print("No containers are running")
else:
    for Make("i").val in Array(containerid.val):
	#print(i.val)
    	Make("da").setValue(os.popen("docker diff "+str(i.val)).read().rstrip("\n"))
   	if (str(da.val) == ''):
		continue
    	else:
		Make("IMAGE").setValue(os.popen("docker ps | grep "+str(i.val)+" | awk '{print $2}' | cut -d '/' -f2 | cut -d ':' -f1").read().rstrip("\n"))
        	# total arguments 
		n = len(sys.argv)
		if n == 1:
		        print("Usage: python "+sys.argv[0]+"  <Docker_Username> <Release_Type>")
			print("\tRelease_Type can be major/minor/patch")
			print("Example: python "+sys.argv[0]+"  vamsi1387 patch")
			exit()
		elif n==2:
			Make("USERNAME").setValue(sys.argv[1])
        		Make("TYPE").setValue("PATCH")
		elif n==3:
			Make("USERNAME").setValue(sys.argv[1])
			Make("TYPE").setValue(sys.argv[2])
		#docker image pull -a $USERNAME/$IMAGE
        	Make("OLD_VERSION").setValue(os.popen("docker images | grep -w "+str(IMAGE.val)+" |grep -iv latest |  awk '{print $2}' | sort -V | tail -1").read().rstrip("\n"))
        	print("OLD_VERSION:"+str(OLD_VERSION.val))
		Make("NEW_VERSION").setValue(addVersion(str(OLD_VERSION.val),str(TYPE.val)))
	        print("New_Version: "+str(NEW_VERSION.val))
		subprocess.call(["docker commit "+str(i.val)+" "+str(USERNAME.val)+"/"+str(IMAGE.val)+":"+str(NEW_VERSION.val)],shell=True)
		if (str(NEW_VERSION.val) != "0.0.0" ):
    			Make("OLD_LAYER_COUNT").setValue(os.popen("docker history "+str(USERNAME.val)+"/"+str(IMAGE.val)+":"+str(OLD_VERSION.val)+" | wc -l").read().rstrip("\n"))
    			Make("OLD_SIZE_COUNT").setValue(os.popen("docker images --format \"{{.Repository}} {{.Tag}} {{.Size}}\" | grep "+str(USERNAME.val)+"/"+str(IMAGE.val)+" | grep -w "+str(OLD_VERSION.val)+" | awk '{print $NF}' | grep -Eo \"[+-]?[0-9]+([.][0-9]+)?\"").read().rstrip("\n"))
    			Make("NEW_LAYER_COUNT").setValue(os.popen("docker history "+str(USERNAME.val)+"/"+str(IMAGE.val)+":"+str(NEW_VERSION.val)+" | wc -l").read().rstrip("\n"))
    			Make("NEW_SIZE_COUNT").setValue(os.popen("docker images --format \"{{.Repository}} {{.Tag}} {{.Size}}\" | grep "+str(USERNAME.val)+"/"+str(IMAGE.val)+" | grep -w "+str(NEW_VERSION.val)+" | awk '{print $NF}' | grep -Eo \"[+-]?[0-9]+([.][0-9]+)?\"").read().rstrip("\n"))
    			print("OLD_LAYER_COUNT:"+OLD_LAYER_COUNT.val+" "+"OLD_SIZE_COUNT:"+OLD_SIZE_COUNT.val)
    			print("NEW_LAYER_COUNT:"+NEW_LAYER_COUNT.val+" "+"NEW_SIZE_COUNT:"+NEW_SIZE_COUNT.val)
    			if (int(OLD_LAYER_COUNT.val) != int(NEW_LAYER_COUNT.val)) or (int(OLD_SIZE_COUNT.val) != int(NEW_SIZE_COUNT.val)):
        			print("Both the versions are different")
				subprocess.call(["docker push "+str(USERNAME.val)+"/"+str(IMAGE.val)+":"+str(NEW_VERSION.val)],shell=True)
				subprocess.call(["docker tag "+str(USERNAME.val)+"/"+str(IMAGE.val)+":"+str(NEW_VERSION.val+" "++str(USERNAME.val)+"/"+str(IMAGE.val)+":latest")],shell=True)
    			else:
        			print("Both the versions are same. No need to create the new version of Image")
				subprocess.call(["docker rmi "+"-f "+str(USERNAME.val)+"/"+str(IMAGE.val)+":"+str(NEW_VERSION.val)],shell=True)
		else: 
                	print("Both the versions are different. Pushing the new version to Repo")
                	subprocess.call(["docker push "+str(USERNAME.val)+"/"+str(IMAGE.val)+":"+str(NEW_VERSION.val)],shell=True)
			subprocess.call(["docker tag "+str(USERNAME.val)+"/"+str(IMAGE.val)+":"+str(NEW_VERSION.val+" "++str(USERNAME.val)+"/"+str(IMAGE.val)+":latest")],shell=True)
