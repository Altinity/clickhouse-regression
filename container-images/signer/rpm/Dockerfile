FROM fedora:latest
RUN dnf -y update && \
    dnf -y install rpm-build rpm-sign gnupg2 createrepo python3 openssl && \
    dnf clean all
# install aws cli to get packages
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN rm awscliv2.zip
COPY requirements.txt /requirements.txt
RUN python3 -m venv --system-site-packages /ansible-venv && \
    /ansible-venv/bin/python3 -m pip install -U pip && \
    /ansible-venv/bin/python3 -m pip install -r /requirements.txt && \
    /ansible-venv/bin/python3 -m pip cache purge && \
    for a in /ansible-venv/bin/ansible*; do ln -s $a /usr/local/bin/$(basename $a); done
COPY ansible-collections.yml /ansible-collections.yml
RUN ansible-galaxy collection install -r /ansible-collections.yml
RUN ln -s /usr/libexec/gpg-preset-passphrase /usr/local/bin/gpg-preset-passphrase
