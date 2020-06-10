
#addVersion()
#{
#  val=$1
#  dotCount=`echo $1 | tr -cd '.'| wc -c`
  #if there is no version tag yet, let's start at 0.0.0
#  if [ -z "$val" ]; then
     #No existing version, starting at 0.0.0
#     echo "0.0.0"
#     exit    
#  fi
#  if [ $dotCount -eq 0 ]
#  then
#      val=`expr $val + 1`
#  else
#      val=`echo $val | awk -F. -v OFS=. 'NF==1{print ++$NF}; NF>1{if(length($NF+1)>length($NF))$(NF-1)++; $NF=sprintf("%0*d", length($NF), ($NF+1)%(10^length($NF))); print}'`
#  fi
#  echo $val 
#}

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


USERNAME=vamsi1387
IMAGE=helloworld
docker image pull -a $USERNAME/$IMAGE
OLD_VERSION=`docker images | grep -w $IMAGE | grep -v latest | awk '{print $2}' | sort -V | tail -1`
NEW_VERION=$(addVersion $OLD_VERSION)
echo "New_Version: $NEW_VERION"
# building the image
docker build -t $USERNAME/$IMAGE:latest .
# tag it
git tag -a "$NEW_VERION" -m "version $NEW_VERION"
git push --tags
docker tag $USERNAME/$IMAGE:latest $USERNAME/$IMAGE:$NEW_VERION
# push it
docker rmi -f $USERNAME/$IMAGE:latest
docker push $USERNAME/$IMAGE:$NEW_VERION
