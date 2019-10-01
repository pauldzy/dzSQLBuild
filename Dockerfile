FROM ubuntu

LABEL maintainer="Paul Dziemiela <Paul.Dziemiela@erg.com>"

ARG DZBASE
ARG DZGITBASE
ARG DZPYSRC

ENV DZBASE="${DZBASE}"                              \
    DZGITBASE="${DZGITBASE}"                        \
    DZPYSRC="${DZPYSRC}"

RUN \
  apt-get update                                  &&\
  apt-get install -y python3                        \
                     python3-dev                    \
                     python3-pip                    \
                     python3-virtualenv             \
                     dos2unix                       \
                     git                            \
                     wget                           \
                     fontconfig                     \
                     libjpeg-turbo8                 \
                     libxrender1                    \
                     naturaldocs                    \
                     xvfb                           \
                     xfonts-75dpi                 &&\
  rm -rf /var/lib/apt/lists/*                     &&\
  cd /usr/local/bin                               &&\
  ln -s /usr/bin/python3 python                   &&\
  wget -q https://downloads.wkhtmltopdf.org/0.12/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb &&\
  dpkg -i wkhtmltox_0.12.5-1.bionic_amd64.deb     &&\
  mkdir -p $DZPYSRC
  
COPY ./src $DZPYSRC

RUN \
  mkdir -p $DZBASE                                &&\
  mkdir -p $DZGITBASE                             &&\
  mkdir -p $DZBASE/scratch                        &&\
  mkdir -p $DZBASE/ndocs/input                    &&\
  mkdir -p $DZBASE/ndocs/output                   &&\
  mkdir -p $DZBASE/ndocs/project                  &&\
  chmod -R 777 $DZBASE $DZGITBASE $DZPYSRC
  
CMD python $DZPYSRC/dzsqlbuild.py

