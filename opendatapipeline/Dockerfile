FROM python:3.10.12-slim

# Env variable for Oracle client libraries
ENV ORACLE_HOME=/opt/oracle/instantclient
ENV LD_LIBRARY_PATH=$ORACLE_HOME
ENV PATH=$ORACLE_HOME:$PATH

# Install dependencies
RUN apt-get update && apt-get install -y \
    libaio1 \
    && apt-get clean \
    && apt-get install -y unzip \
    && rm -rf /var/lib/apt/lists/*

# Download and install Oracle Instant Client
RUN apt-get update && apt-get install -y curl \
    && curl -L -o instantclient-basic-linux.x64.zip https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip \
    && mkdir -p /opt/oracle \
    && unzip instantclient-basic-linux.x64.zip -d /opt/oracle/ \
    && rm instantclient-basic-linux.x64.zip \
    && a=`ls -1 /opt/oracle | grep "instantclient_"` \
    && ln -s /opt/oracle/$a /opt/oracle/instantclient

# Download and install ODBC driver
# 1. Install prerequisites
RUN apt-get update && apt-get install -y curl gnupg2

# 2. Add Microsoft's repository for the SQL Server Driver (Debian 11 example)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

# 3. Install unixODBC and the Microsoft ODBC Driver 18
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y \
    unixodbc \
    unixodbc-dev \
    msodbcsql18 \
    mssql-tools18

# 4. Add the tools to your PATH (helpful for debugging)
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc

ENV APP_ENVIRONMENT=prod
ENV MONGO_USERNAME=askondata
ENV MONGO_PASSWORD=askondata
ENV MONGO_PORT=27021
ENV AIRFLOW_USERNAME=askondata
ENV AIRFLOW_PASSWORD=askondata
ENV AIRFLOW_HOME=/opt/airflow
ENV OLLAMA_IP=askondata_ollama
RUN apt-get -qq update && apt-get -qq install -y curl
COPY entrypoint.sh entrypoint.sh
ENTRYPOINT ["/bin/bash","/entrypoint.sh"]
EXPOSE 3001
CMD bash -c "python -m src.run"
