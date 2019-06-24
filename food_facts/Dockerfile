FROM python:3.6.3
ENV PYTHONUNBUFFERED 1
ENV SERVICE_NAME carbon
# ENV API_VERSION 1
ARG API_VERSION
ENV API_VERSION=${API_VERSION}
RUN mkdir -p /usr/src/app
COPY *.joblib /usr/src/app/
COPY *.py /usr/src/app/
COPY requirements.txt /usr/src/app/
WORKDIR /usr/src/app
RUN pip install -r requirements.txt
RUN pip install joblib
EXPOSE 5000
CMD ["python", "app.py"]

