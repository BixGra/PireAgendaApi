FROM python:3.13

WORKDIR /etc/PireAgendaApi

COPY . /etc/PireAgendaApi/.

RUN pip install --upgrade pip && pip --no-cache-dir install -r /etc/PireAgendaApi/requirements.txt

ENV PYTHONPATH $PYTHONPATH:$PATH:/etc/PireAgendaApi/app/

ENV PATH /opt/conda/envs/env/bin:$PATH

ENV PROJECT_PATH /etc/PireAgendaApi/app/

EXPOSE 8000

ENTRYPOINT gunicorn -b 0.0.0.0:8000 -k uvicorn.workers.UvicornWorker --forwarded-allow-ips "*" app.main:app --threads 2 --workers 1 --timeout 1000 --graceful-timeout 30
