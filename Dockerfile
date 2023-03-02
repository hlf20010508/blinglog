FROM python:3.8.16-alpine3.17
WORKDIR /blinglog
COPY ./ ./
RUN pip install --no-cache-dir pipenv &&\
    pipenv sync &&\
    pipenv --clear &&\
    mkdir logs &&\
    touch blog.log
