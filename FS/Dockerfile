FROM python:3.9

# Set up a working folder and install the pre-reqs
WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask

EXPOSE 9090

CMD [ "python", "run.py" ]