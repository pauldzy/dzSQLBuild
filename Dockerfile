FROM ubuntu

LABEL maintainer="Paul Dziemiela <Paul.Dziemiela@erg.com>"

RUN \
  apt-get update                       && \
  apt-get install -y python3              \
                     python3-dev          \
                     python3-pip          \
                     python3-virtualenv   \
                     dos2unix             \
                     wkhtmltopdf          \
                     naturaldocs       && \
  rm -rf /var/lib/apt/lists/*          && \
  cd /usr/local/bin                    && \
  ln -s /usr/bin/python3 python
  
COPY ./src /home/ubuntu/src

RUN \
  mkdir -p /home/ubuntu/target
  
CMD ["python","/home/ubuntu/src/dzsqlbuild.py" ]