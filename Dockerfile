FROM python:3.12

RUN pip install numpy tornado

CMD ["python", "server.py"]