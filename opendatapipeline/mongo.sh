#!/bin/bash
echo "Executing mongosh file."
sleep 10
until mongosh  --eval "print(\"Connection establised\")"; do
    echo "Waiting for MongoDB to start"
    sleep 5
done

mongosh --eval "rs.initiate({
_id : 'rs0',
    members: [
        { _id: 0 , host: 'localhost:27017'}
    ]
})"

mongosh  --eval "db.getSiblingDB('admin').createUser({
    user: 'root',
    pwd: 'root',
    roles: [
        { role: 'root', db: 'admin' },
        {role:'clusterAdmin', db: 'admin'}
    ]
})"


mongosh -u root -p root  --eval "db.getSiblingDB('user_sessions_test').createUser({
    user: 'admin',
    pwd: 'admin',
    roles: [
        { role: 'readWrite', db: 'user_sessions_test' }
    ]
})"