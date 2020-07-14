# Execute: `make docker`

FROM ubuntu:18.04
RUN set -ex \
    && apt update \
    && apt install -y virtualenv python3.7 python-pip git \
    && apt clean -y

COPY requirements.txt /tmp/ 
WORKDIR /mdtocf
RUN set -ex \
    && virtualenv --python=python3.7 venv \
    && chmod +x venv/bin/activate \
    && . venv/bin/activate \
    && python -m pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt

COPY . /mdtocf

ENV PYTHONPATH "/mdtocf"
ENTRYPOINT [ "/mdtocf/venv/bin/python" , "-m", "mdtocf.mdtocf" ]
CMD [ "-c" ]
