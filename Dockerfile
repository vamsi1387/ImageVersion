#Adding a comment to test Dockerfile versioning

FROM ubuntu

COPY helloworld.sh /opt/app/

WORKDIR /opt/app/

COPY helloworld.sh /opt/app/

CMD sh helloworld.sh
