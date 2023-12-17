FROM python:3.9
COPY . .
RUN pip install mysql-connector-python beautifulsoup4 requests
CMD ["python", "script.py"]