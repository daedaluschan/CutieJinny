FROM python:3

WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt

RUN rm -Rf bin include lib
RUN mkdir logs

VOLUME /app/logs

CMD python ./CuteJin.py