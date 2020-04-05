FROM ubuntu:18.04

ARG build

ENV DEBIAN_FRONTEND=noninteractive \
    DEBCONF_NONINTERACTIVE_SEEN=true

COPY build.sh /
RUN chmod +x /build.sh \
   && bash /build.sh $build \
   && rm -rf /build.sh

RUN useradd user --shell /bin/bash --create-home \
   && usermod -a -G sudo user \
   && echo 'ALL ALL = (ALL) NOPASSWD: ALL' >> /etc/sudoers \
   && echo 'user:secret' | chpasswd

ENV HOME=/home/user

VOLUME [ "/profile" ]
RUN mkdir -p /profile /project /env \
   && chown -R user:user /project /profile /env

COPY --chown=user:user entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

WORKDIR "/project"
