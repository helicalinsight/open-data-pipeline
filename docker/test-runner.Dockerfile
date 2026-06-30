FROM python:3.10.12-slim

# Install system dependencies including Java
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    openssl \
    openjdk-17-jdk \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME for PySpark
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

WORKDIR /workspace

COPY core/ /workspace/core/
COPY askondata/ /workspace/askondata/
COPY spark_server_app/ /workspace/spark_server_app/
COPY dlt_server_app/ /workspace/dlt_server_app/

# Install PySpark and MongoDB dependencies
RUN pip install --no-cache-dir \
    pyspark==3.3.3 \
    pymongo==4.6.1 \
    mongomock==4.1.2 \
    bson==0.5.10 \
    pandas==2.0.3 \
    pyyaml==6.0.1

# install dependencies
RUN cd askondata && \
    python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    cd inbuilt_modules/helper && pip install . && \
    pip install --no-cache-dir -r requirements.txt && \
    cd ../../ && \
    cd ../spark_server_app && \
    pip install --no-cache-dir -r requirements.txt && \
    \
    cd ../dlt_server_app && \
    pip install --no-cache-dir -r requirements.txt && \
    cd ..

# Debugger for Python
RUN pip install --no-cache-dir debugpy==1.8.2

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Default command is overridden by compose
CMD ["bash"]