FROM ubuntu

LABEL maintainer="Paul Dziemiela <Paul.Dziemiela@erg.com>"

RUN \
  apt-get update                       && \
  apt-get install -y python3              \
                     python3-dev          \
                     python3-pip          \
                     python3-virtualenv   \
                     dos2unix             \
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
   wget -q https://downloads.wkhtmltopdf.org/0.12/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb &&\
   dpkg -i wkhtmltox_0.12.5-1.bionic_amd64.deb
  
COPY ./src /home/ubuntu/src

RUN \
  mkdir -p /home/ubuntu/target         && \
  mkdir -p /home/ubuntu/ndocs/input    && \
  mkdir -p /home/ubuntu/ndocs/output   && \
  mkdir -p /home/ubuntu/ndocs/project
  
CMD ["python","/home/ubuntu/src/dzsqlbuild.py" ]