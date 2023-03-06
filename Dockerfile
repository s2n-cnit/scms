FROM python:3.7-slim

RUN apt-get update -y
RUN apt-get install git httpie jq fish gcc g++ micro iputils-ping curl -y

RUN bash -c "$(curl -fsSL https://raw.githubusercontent.com/alexcarrega/oh-my-bash/master/tools/install.sh)"

ARG NOCACHE=true
RUN git clone https://github.com/s2n-cnit/scms /opt/scms
RUN chgrp -R 0 /opt/scms && chmod -R g=u /opt/scms
WORKDIR /opt/scms

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "/bin/bash", "scripts/start.sh" ]

ENV SCMS_PORT=9999
EXPOSE $SCMS_PORT
