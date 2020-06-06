#Adding a comment to test Dockerfile versioning

FROM ubuntu

COPY helloworld.sh /opt/app/

COPY Dockerfile_versionManagement.py /opt/app/

COPY Dockerfile /opt/app/

WORKDIR /opt/app/

CMD sh helloworld.sh
