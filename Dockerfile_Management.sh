
addVersion()
{
  val=$1
  dotCount=`echo $1 | tr -cd '.'| wc -c`
  #if there is no version tag yet, let's start at 0.0.0
  if [ -z "$val" ]; then
     #No existing version, starting at 0.0.0
     echo "0.0.0"
     exit    
  fi
  if [ $dotCount -eq 0 ]
  then
      val=`expr $val + 1`
  else
      val=`echo $val | awk -F. -v OFS=. 'NF==1{print ++$NF}; NF>1{if(length($NF+1)>length($NF))$(NF-1)++; $NF=sprintf("%0*d", length($NF), ($NF+1)%(10^length($NF))); print}'`
  fi
  echo $val 
}

USERNAME=vamsi1387
IMAGE=helloworld
docker image pull -a $USERNAME/$IMAGE
OLD_VERSION=`docker images | grep -w $IMAGE | grep -v latest | awk '{print $2}' | sort | tail -1`
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
