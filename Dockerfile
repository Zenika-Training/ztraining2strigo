FROM python:3-alpine

COPY src/ /usr/local/lib/extra/
ENV PYTHONPATH=/usr/local/lib/extra

VOLUME ["/training"]
WORKDIR /training

ENTRYPOINT ["python3", "-m", "ztraining2strigo"]
CMD ["--help"]
