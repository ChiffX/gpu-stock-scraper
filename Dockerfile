#https://github.com/joyzoursky/docker-python-chromedriver
FROM joyzoursky/python-chromedriver
WORKDIR /usr/workspace
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "/usr/workspace/main.py" ]
