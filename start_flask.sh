helpFunction()
{
   echo ""
   echo "Usage: $0 -p PORT"
   echo -e "\t-p host machine's port for apps in Docker's container"
   exit 1 # Exit script after printing help
}

if [ $# -eq 0 ]
then
    echo "No parameters were provided";
    helpFunction
fi

while getopts "p:" opt
do
   case "$opt" in
      p ) PORT="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$PORT" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
imageName=jde_flask
port1=$PORT
port2=8000

# Sensitive info
echo "Type value for variable SASPASS:"
read -s SASPASS
export SASPASS

docker build -f ./etc/flask/Dockerfile -t $imageName ./

docker run -it \
   -p $port1:$port2 \
   --env-file "$(pwd)/etc/flask/.env" \
   -e SASPASS \
   -v "$(pwd)/":/main \
   -v "$(pwd)/logs/jde":/logs \
   -v /etc/localtime:/etc/localtime:ro \
   $imageName /bin/bash
