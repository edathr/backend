FROM mongo:4.2

ENV DATABASE=50043db
ENV COLLECTION=kindle_metadata2
ENV FILEPATH=../processed_metadata.json

COPY processed_metadata.json ./
COPY mongodb_entrypoint.sh ./docker-entrypoint-initdb.d/

RUN chmod u+x ./docker-entrypoint-initdb.d/mongodb_entrypoint.sh
#ENTRYPOINT ["./mongodb_entrypoint.sh"]