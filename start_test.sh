helpFunction()
{
   echo ""
   echo "Usage: $0 [-m]"
   echo -e "\tUse option -m for writing custom pytest commands"
   exit 1 # Exit script after printing help
}

while getopts "m" opt
do
   case "$opt" in
      m ) MODE="MANUAL" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$MODE" ]
then
   START_COMMAND="python -m pytest"
else
   START_COMMAND="/bin/bash"
fi

echo $START_COMMAND

imageName=jde_test

docker build -f ./etc/flask/Dockerfile -t $imageName ./

docker run -it \
   -v "$(pwd)/":/main \
   -v /etc/localtime:/etc/localtime:ro \
   $imageName $(echo $START_COMMAND)