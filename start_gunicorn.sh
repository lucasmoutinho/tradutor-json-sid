helpFunction()
{
   echo ""
   echo "Usage: $0 -m MODE -p PORT"
   echo -e "\t-m Used as version of Docker image and path for config files. Ensure that all necessary files are located at ./etc/gunicorn/\$MODE"
   echo -e "\t-p host machine's port for apps in Docker's container"
   exit 1 # Exit script after printing help
}

if [ $# -eq 0 ]
then
   echo "No parameters were provided";
   helpFunction
fi

while getopts "m:p:" opt
do
   case "$opt" in
      m ) MODE="$OPTARG" ;;
      p ) PORT="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$MODE" ] || [ -z "$PORT" ]
then
   echo "MODE and/or PORT are missing";
   helpFunction
fi

# Check if path is correct
CONFIGDIR="$(pwd)/etc/gunicorn/$MODE"
if ! [ -d "$CONFIGDIR" ]
then
   echo "Directory $CONFIGDIR doesn't exist";
   helpFunction
fi

# Begin script in case all parameters are correct
imageName=jde_gunicorn:$MODE
port1=$PORT
port2=8000
GUNICORNCONFIG="$CONFIGDIR/gunicorn_config.py"
GUNICORNLOGCONFIG="$CONFIGDIR/gunicorn_logconfig.json"
ENVFILE="$CONFIGDIR/.env"

# Sensitive info
echo "Type value for variable SASPASS:"
read -s SASPASS
export SASPASS

# Build and run
docker build --build-arg MODE=$MODE -f "$(pwd)/etc/gunicorn/Dockerfile" -t $imageName ./

# Construct command and run it
DTTM=`date '+%Y-%m-%d_%H-%M-%S'`
# CMD="docker run -d -p $port1:$port2"
CMD="docker run -p $port1:$port2"
CMD="${CMD} --env-file \"$ENVFILE\""
CMD="${CMD} -e SASPASS"
CMD="${CMD} -v \"$(pwd)/logs/jde/gunicorn/logs_$DTTM\":/logs"
CMD="${CMD} -v \"$GUNICORNLOGCONFIG\":/tmp/gunicorn_logconfig.json:ro"
CMD="${CMD} $imageName"

eval ${CMD}