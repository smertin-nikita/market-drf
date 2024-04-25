FROM ubuntu:22.04 as base-build-image

RUN apt-get update && \
    apt-get install --no-install-recommends -y  \
    python3 \
    python3-dev \
    python3-venv \
    python3-pip \
    python3-wheel &&  \
    apt-get clean && rm -rf /var/lib/apt/lists/*


RUN python3 -m venv /home/backend/venv
ENV PATH="/home/backend/venv/bin:$PATH"

# Install requirements
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8


FROM base-build-image as dev-build-image

# Install dev requirements
COPY requirements-dev.txt requirements-dev.txt
RUN pip3 install -r requirements-dev.txt --no-cache-dir


FROM ubuntu:22.04 as runner-image

RUN apt-get update && apt-get install --no-install-recommends -y  \
    python3  \
    python3-venv && \
	apt-get clean && rm -rf /var/lib/apt/lists/* && \
    useradd -s /bin/bash --create-home backend

USER backend
COPY --from=dev-build-image /home/backend/venv /home/backend/venv

WORKDIR /home/backend
COPY src src


# activate virtual environment
ENV VIRTUAL_ENV=/home/backend/venv
ENV PATH="/home/backend/venv/bin:$PATH"

ENV APPLICATION_PATH=/home/backend/src
ENV DJANGO_SETTINGS_MODULE=base.settings

ENV PYTHONUNBUFFERED 1
