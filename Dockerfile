#Adding a comment to test Dockerfile versioning

FROM ubuntu

COPY helloworld.sh /opt/app/

VERSION .

WORKDIR /opt/app/

CMD sh helloworld.sh
