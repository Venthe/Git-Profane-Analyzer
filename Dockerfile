FROM docker.io/python:3.6.13

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir --requirement requirements.txt

COPY analyzer.py ./

ENTRYPOINT [ "python3", "./analyzer.py" ]