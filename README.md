# recon_knife
Toolset of the most popular recon tools

### Description
Dockerfile - is docker image which is a copy of [bbht](https://github.com/nahamsec/bbht/ "bbht") by @nahamsec.

For building you have to fill (aws_credentials.txt)[https://github.com/slinkinone/recon_knife/aws_credentials.txt] file with own aws credential values and then build recon container via the following command:

```bash
docker build --tag recon .
```

For working with container use the followin command:
```bash
export ABS_PATH_TO_RECON_IO_DIR=IO_DIR_ABS_PATH
docker run -it -v $ABS_PATH_TO_RECON_IO_DIR:/data/io_dir recon bash
```

Now you have a shared folder which is located in /data/io_dir folder within container. When container stops all files and modifications will be saved in this folder.

Also, you are able to connect to existing container via getiing container ID and attaching to it.

```bash
docker ps # get all running container
docker attach container_id
docker kill container_id
```

### Today
Now, I'm working on moving [lazyrecon](https://github.com/nahamsec/lazyrecon "lazyrecon") bash script functionality script to python script. It will get more structured version of lazyrecon script with fixed mistakes.

I make notes in the code which can be found by "**TODO**" or "**TODO-CHECKME**" in places that require optimization (usually avoid unsing temporary files) and things from origianl code which I haven't completely understood.

### TODO
* Check [recon.py](https://github.com/slinkinone/recon_knife/blob/master/scripts/recon.py) for mistakes (compare with the original script);
* Screenshots support;
* Fix **TODO** and **TODO-CHECKME** in the code;
* Django template;

Notes:
* [recon.py](https://github.com/slinkinone/recon_knife/blob/master/scripts/recon.py) requires [python3](https://www.python.org/download/releases/3.0/);