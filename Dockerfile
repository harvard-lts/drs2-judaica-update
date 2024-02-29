FROM ubuntu:20.04

COPY requirements.txt /tmp/

RUN apt-get update && \
  apt-get install -y libaio1 libaio-dev curl unzip vim git less && \
  apt-get install -y pip && \
  pip install --upgrade pip && \
  pip install -r /tmp/requirements.txt

RUN useradd --create-home drsadm

COPY --chown=drsadm . /home/drsadm/bin
RUN chmod 755 /home/drsadm/bin/*.py

# Write to .bashrc:
WORKDIR /home/drsadm/bin

COPY change_id.sh /root/change_id.sh
RUN chmod 755 /root/change_id.sh && \
   /root/change_id.sh -u 61 -g 199

USER drsadm
ENV PATH="$PATH:/home/drsadm/bin"

CMD ["sh", "-c", "cd /app && bash"]
