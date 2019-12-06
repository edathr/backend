FROM python:3.7
MAINTAINER Lionell Loh

COPY . /app
WORKDIR /app
RUN rm -rf migrations
ENV FLASK_APP run.py
ENV FLASK_CONFIG development
RUN pip3 install -r requirements.txt

EXPOSE 5000


#ENTRYPOINT ["python3"]
#CMD ["run.py"]

RUN chmod u+x ./flask-migrate.sh
ENTRYPOINT ["./flask-migrate.sh"]
