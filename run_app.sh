#!/bin/bash

# Inspired by https://www.fosstechnix.com/shell-script-to-build-docker-image/

echo "Checking to see if image exists"
result=$( docker images -q file-directory-api-image )
if [[ -n "$result" ]]; then
echo "Image exists"
docker rmi -f file-directory-api-image
else
echo "No such image"
fi

echo "building the docker image"
docker image build --tag file-directory-api-image .

result=$( docker ps -q -f name=file-directory-api-container )
if [[ $? -eq 0 ]]; then
echo "Container exists"
docker container rm -f file-directory-api-container
echo "Deleted the existing docker container"
else
echo "No such container"
fi

echo "Deploying the container"
read -p 'Root Directory: ' pathvar
docker run -itd -e ROOT_PATH=$pathvar --publish 8080:8080 --name file-directory-api-container -v $pathvar:$pathvar file-directory-api-image
