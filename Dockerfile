# pull official base image
FROM python:3.11.4-slim-buster

# create directory for the app user
RUN addgroup --system app && adduser --system --group app


WORKDIR /app

# copy project
COPY . .

# install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends netcat
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN python3 manage.py collectstatic



# chown all the files to the app user
RUN chown -R app:app /app

# change to the app user
USER app
