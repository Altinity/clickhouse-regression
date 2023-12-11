FROM ubuntu:latest
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y upgrade && apt-get -y install dpkg-sig gnupg2 apt-utils curl python3 python3-venv unzip libssl-dev && apt clean all
# install aws cli to get packages
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN rm -f awscliv2.zip
COPY requirements.txt /requirements.txt
RUN python3 -m venv --system-site-packages /ansible-venv && \
    /ansible-venv/bin/python3 -m pip install -U pip && \
    /ansible-venv/bin/python3 -m pip install -r /requirements.txt && \
    /ansible-venv/bin/python3 -m pip cache purge && \
    for a in /ansible-venv/bin/ansible*; do ln -s $a /usr/local/bin/$(basename $a); done
COPY ansible-collections.yml /ansible-collections.yml
RUN ansible-galaxy collection install -r /ansible-collections.yml
RUN ln -s /usr/lib/gnupg2/gpg-preset-passphrase /usr/local/bin/gpg-preset-passphrase
