FROM ubuntu:20.04

COPY . /app/

RUN apt-get update && \
  apt-get install -y libaio1 libaio-dev curl unzip vim git less && \
  apt-get install -y pip && \
  pip install --upgrade pip && \
  pip install -r /app/requirements.txt

# Write to .bashrc:
WORKDIR /app

CMD ["sh", "-c", "cd /app && bash"]
