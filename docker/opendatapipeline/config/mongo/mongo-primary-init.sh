#!/bin/bash

sleep 10

if [ -f .env ]; then
  export $(grep -E 'MONGO_USERNAME|MONGO_PASSWORD|MONGO1_PORT|MONGO2_PORT' .env | xargs)
fi


echo 'Setting up replicaset'


MONGO_USERNAME=${MONGO_USERNAME:-askondata}
MONGO_PASSWORD=${MONGO_PASSWORD:-askondata}
MONGO1_PORT=${MONGO1_PORT:-27021}

until mongosh --port ${MONGO1_PORT} --eval "print(\"Connection establised\")"; do
    echo "Waiting for MongoDB to start"
    sleep 5
done


mongosh --port 27021  --eval "rs.initiate({

    _id : 'askOnDataReplicaSet',
    members: [
        { _id: 0 , host: 'open_data_pipeline_mongo_primary:27021', priority: 1 },
        { _id: 1 , host: 'open_data_pipeline_mongo_secondary:27022', priority: 0, votes: 0 },
        { _id: 2 , host: 'open_data_pipeline_mongo_tertiary:27023', priority: 0, votes: 0 }
    ]
})"

sleep 10

mongosh  --port 27021 --eval "db.getSiblingDB('admin').createUser({
    user: 'root',
    pwd: 'root',
    roles: [
        { role: 'root', db: 'admin' },
        { role: 'clusterAdmin', db: 'admin' }
    ]
})" 

sleep 5

mongosh --port 27021 -u root -p root  --eval "db.getSiblingDB('user_sessions').createUser({
    user: 'askondata',
    pwd: 'askondata',
    roles: [
        { role: 'readWrite', db: 'user_sessions' }
    ]
})"
