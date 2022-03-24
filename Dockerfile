FROM python:3
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN apt-get update && apt-get install -y python3-opencv
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["python", "-m", "scheduler"]

