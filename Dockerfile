FROM ubuntu:bionic

LABEL maintainer="Paul Dziemiela <Paul.Dziemiela@erg.com>"

ARG wkttopdfdeb=wkhtmltox_0.12.6-1.bionic_amd64.deb
ARG    wkttopdf=https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.bionic_amd64.deb

RUN \
  apt-get update                       && \
  apt-get install -y python3              \
                     python3-dev          \
                     python3-pip          \
                     python3-virtualenv   \
                     dos2unix             \
                     git                  \
                     wget                 \
                     fontconfig           \
                     libjpeg-turbo8       \
                     libxrender1          \
                     naturaldocs          \
                     xvfb                 \
                     xfonts-75dpi      && \
  rm -rf /var/lib/apt/lists/*          && \
  cd /usr/local/bin                    && \
  ln -s /usr/bin/python3 python

RUN \
  wget -q ${wkttopdf}                  && \
  dpkg -i ${wkttopdfdeb}
  
COPY ./src /home/ubuntu/src

RUN \
  mkdir -p /home/ubuntu/target         && \
  mkdir -p /home/ubuntu/gittrg         && \
  mkdir -p /home/ubuntu/ndocs/input    && \
  mkdir -p /home/ubuntu/ndocs/output   && \
  mkdir -p /home/ubuntu/ndocs/project  && \
  chmod -R 777 /home/ubuntu
  
CMD ["python","/home/ubuntu/src/dzsqlbuild.py" ]