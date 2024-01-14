#FROM python:3.10-slim-buster
#
#ENV PYTHONUNBUFFERED 1
#ENV PYTHONDONTWRITEBYTECODE 1
#
#RUN apt-get update \
#  # dependencies for building Python packages
#  && apt-get install -y build-essential \
#  # psycopg2 dependencies
#  && apt-get install -y libpq-dev \
#  # Additional dependencies
#  && apt-get install -y telnet netcat \
#  # cleaning up unused files
#  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
#  && rm -rf /var/lib/apt/lists/*
#
## Requirements are installed here to ensure they will be cached.
#COPY ./requirements.txt /requirements.txt
#RUN pip install -r /requirements.txt
#
## Copy the api directory
#COPY ./ /app
#
## Copy the shared_enum directory
#COPY ./shared_enum /app/shared_enum
#
#COPY ./compose/api/entrypoint /entrypoint
#RUN sed -i 's/\r$//g' /entrypoint
#RUN chmod +x /entrypoint
#
#COPY ./compose/api/start /start
#RUN sed -i 's/\r$//g' /start
#RUN chmod +x /start
#
## Set the working directory
#WORKDIR /app
#ENV PYTHONPATH=/app
#
#ENTRYPOINT ["/entrypoint"]
