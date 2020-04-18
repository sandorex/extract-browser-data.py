FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true \
    TERM=xterm \
    DBUS_SESSION_BUS_ADDRESS=/dev/null

# install utilities and pyenv dependencies
RUN apt-get update -qqy
RUN apt-get install -qqy --no-install-recommends sudo coreutils build-essential \
   libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl \
   llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev \
   python-openssl git ca-certificates xvfb x11-utils wmctrl xdotool fluxbox git

# install firefox
RUN apt-get install -qqy --no-install-recommends firefox

# install chromium
RUN apt-get install -qqy --no-install-recommends chromium-browser

# cleanup
RUN apt autoremove -qqy \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# add the user
RUN useradd user --shell /bin/bash --create-home --uid 1000 \
   && usermod -a -G sudo user \
   && echo 'ALL ALL = (ALL) NOPASSWD: ALL' >> /etc/sudoers \
   && echo 'user:secret' | chpasswd

ENV HOME=/home/user \
   USER=user

# install pyenv (as user)
USER user

RUN curl 'https://pyenv.run' | bash

RUN echo 'export PATH="/home/user/.pyenv/bin:$PATH"' >> /home/user/.bashrc \
   && echo 'eval "$(pyenv init -)"' >> /home/user/.bashrc \
   && echo 'eval "$(pyenv virtualenv-init -)"' >> /home/user/.bashrc

RUN git clone 'https://github.com/momo-lab/xxenv-latest.git' /home/user/.pyenv/plugins/xxenv-latest

# install python versions
RUN /home/user/.pyenv/bin/pyenv latest install 3.6
RUN /home/user/.pyenv/bin/pyenv latest install 3.7
RUN /home/user/.pyenv/bin/pyenv latest install 3.8

# set global python versions (first one will be the default)
RUN /home/user/.pyenv/bin/pyenv latest global 3.6 3.7 3.8

# install tox
RUN /home/user/.pyenv/bin/pyenv exec pip3 --disable-pip-version-check --no-cache-dir install setuptools wheel \
   && /home/user/.pyenv/bin/pyenv exec pip3 --disable-pip-version-check --no-cache-dir install tox

# NOTE this is at the bottom to avoid rebuilding python versions to update the script
USER root

RUN mkdir -p /project \
   && chown -R user:user /project

COPY --chown=user:user entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ '/entrypoint.sh' ]

WORKDIR "/project"

USER user
