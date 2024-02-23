FROM ubuntu:20.04

COPY . /app/

RUN apt-get update && \
  apt-get install -y libaio1 libaio-dev curl unzip vim git less && \
  apt-get install -y pip && \
  pip install --upgrade pip && \
  pip install -r /app/requirements.txt

RUN useradd --create-home drsadm

# Write to .bashrc:
WORKDIR /app

COPY change_id.sh /root/change_id.sh
RUN chmod 755 /root/change_id.sh && \
   /root/change_id.sh -u 55017 -g 0

USER drsadm

CMD ["sh", "-c", "cd /app && bash"]
