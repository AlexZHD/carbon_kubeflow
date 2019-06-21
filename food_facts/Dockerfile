# FROM ubuntu:latest
# RUN apt-get update -y
# RUN apt-get install -y python-pip python-dev build-essential
FROM python:3.6.3
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /usr/src/app
COPY *.joblib /usr/src/app/
COPY *.py /usr/src/app/
COPY requirements.txt /usr/src/app/
WORKDIR /usr/src/app
RUN pip install -r requirements.txt
RUN python -m pip install --user numpy
RUN pip install -U scikit-learn
RUN pip install joblib
EXPOSE 5000

CMD ["python", "app.py"]

# ENTRYPOINT ["python"]
# CMD ["app.py"]

