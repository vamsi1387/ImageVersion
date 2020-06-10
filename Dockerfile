#Adding a comment to test Dockerfile versioning

FROM ubuntu

COPY helloworld.sh /opt/app/

COPY Dockerfile_Management.sh /opt/app/

WORKDIR /opt/app/

CMD sh helloworld.sh
