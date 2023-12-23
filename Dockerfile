FROM python:3.11

RUN pip install numpy tornado torch

CMD ["python", "server.py"]