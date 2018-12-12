FROM fedora

RUN dnf -q -y install ruby-devel gcc make rpm-build libffi-devel
RUN gem install --no-ri --no-rdoc fpm
RUN mkdir /poco
VOLUME /poco
CMD ["bash"] 
