
FROM python:3.12.5


WORKDIR /app


COPY requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt


COPY . /app/


EXPOSE 8000


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bilimber.wsgi:application"]