#!/bin/bash

addVersion()
{
  val=$1
  if [ -z "$2" ]; then
    type=PATCH
  else
    type=`echo $2 | tr [a-z] [A-Z]`
  fi
  dotCount=`echo $1 | tr -cd '.'| wc -c`
  #if there is no version tag yet, let's start at 0.0.0
  if [ -z "$val" ] || [ "$val" == "<none>" ] ; then
     #No existing version, starting at 0.0.0
     echo "0.0.0"
     exit
  fi
  if [ $dotCount -eq 0 ]
  then
      val=`expr $val + 1`
  else
      if [ $dotCount -eq 2 ]; then
           majorVersion=`echo $1 | cut -d '.' -f1`
           minorVersion=`echo $1 | cut -d '.' -f2`
           patchVersion=`echo $1 | cut -d '.' -f3`
           if [ "$type" == PATCH ]; then
                patchVersion=`expr $patchVersion + 1`
           elif [ "$type" == MINOR ]; then
                minorVersion=`expr $minorVersion + 1`
           else
                majorVersion=`expr $majorVersion + 1`
                minorVersion=0
                patchVersion=0
           fi
           val=$majorVersion"."$minorVersion"."$patchVersion
      elif [ $dotCount -eq 1 ]; then
          majorVersion=`echo $1 | cut -d '.' -f1`
          patchVersion=`echo $1 | cut -d '.' -f2`
           if [ "$type" == PATCH ]; then
                patchVersion=`expr $patchVersion + 1`
           elif [ "$type" == MINOR ]; then
                minorVersion=`expr $minorVersion + 1`
           else
                majorVersion=`expr $majorVersion + 1`
                patchVersion=0
           fi
           val=$majorVersion"."$patchVersion
      fi
  fi
  echo $val
}



if [ $# -eq 0 ]; then
	echo "Usage: sh $0 <Docker_Username> <Release_Type>"
	echo "	Docker_Username is docker repo username"
	echo "	Release_Type can be major/minor/patch"
        echo "Example: sh $0 vamsi1387 patch"
	exit
else
containerid=`docker container ls | grep -v CONTAINER | awk '{print $1}'`
if [ -z "$containerid" ]; then
	echo "No containers are running"
else
	for i in $containerid
	do
	  echo $i
	  da=`docker diff $i`
 	  if [ -z "$da" ]
	  then    
		echo "no changes in container"
	  else
		#IMAGE_ID=`docker ps --format='{{.Image}}' -n 1 | cut -d ":" -f1 | cut -d ":" -f1`
        	IMAGE=`docker ps | grep $i | awk '{print $2}' | cut -d "/" -f2 | cut -d ":" -f1`
		USERNAME=$1
		TYPE=$2
		#docker image pull -a $USERNAME/$IMAGE
        	OLD_VERSION=`docker images | grep -w $IMAGE | grep -v latest | awk '{print $2}' | sort -V | tail -1`
		echo $OLD_VERSION
        	NEW_VERSION=`addVersion $OLD_VERSION $TYPE`
        	echo "New_Version: $NEW_VERSION"
        	docker commit $i $USERNAME/$IMAGE:$NEW_VERSION
                if [ "$NEW_VERSION" != "0.0.0" ]; then
                	OLD_LAYER_COUNT=`docker history $USERNAME/$IMAGE:$OLD_VERSION | wc -l`
			##docker inspect vamsi1387/helloworld:0.1.9 | sed -n '/Layers/,/]/p' | wc -l -- Lawyers count also can be obtained using this command.
                	OLD_SIZE_COUNT=`docker images --format "{{.Repository}} {{.Tag}} {{.Size}}" | grep $USERNAME/$IMAGE | grep -w $OLD_VERSION | awk '{print $NF}' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'`
                	NEW_LAYER_COUNT=`docker history $USERNAME/$IMAGE:$NEW_VERSION | wc -l`
                	NEW_SIZE_COUNT=`docker images --format "{{.Repository}} {{.Tag}} {{.Size}}" | grep $USERNAME/$IMAGE | grep -w $NEW_VERSION | awk '{print $NF}' | grep -Eo '[+-]?[0-9]+([.][0-9]+)?'`
			echo "Old Version Details: " $OLD_LAYER_COUNT $OLD_SIZE_COUNT
			echo "New Version Details: " $NEW_LAYER_COUNT $NEW_SIZE_COUNT
			if [ $OLD_LAYER_COUNT != $NEW_LAYER_COUNT ] || [ $OLD_SIZE_COUNT != $NEW_SIZE_COUNT ]; then
				echo "Both the versions are different. Pushing the new version to Repo"
				docker push $USERNAME/$IMAGE:$NEW_VERSION
				docker tag $USERNAME/$IMAGE:$NEW_VERSION $USERNAME/$IMAGE:latest
			else
				echo "Both the versions are same. No need to create the new version of Image" 
				docker rmi -f $USERNAME/$IMAGE:$NEW_VERSION
			fi			
		else
			echo "Both the versions are different. Pushing the new version to Repo"
			docker push $USERNAME/$IMAGE:$NEW_VERSION
			docker tag $USERNAME/$IMAGE:$NEW_VERSION $USERNAME/$IMAGE:latest
		fi
  	  fi
	done
fi
fi
