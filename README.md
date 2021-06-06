# PydisPixels Painter
This is the script I'm using to join in on the [python discord pixels event](https://pixels.pythondiscord.com)!

## Setup
Oh look, a very convenient shell script!
```shell
curl https://raw.githubusercontent.com/EEKIM10/pydis-pixel/master/install.sh | bash
```

**BEFORE YOU RUN!**

You must first get an API token from https://pixels.pythondiscord.com/show_token.
Once you've done that, create a file called `auth.txt`, and paste it in there. It must be in your current working
directory.

### Looping
(basically, native 24/7 running)

You can specify if the program should loop itself with the command line argument `--loop`

Note: looping will use the same input values you're asked when you start the program.
This is useful for "protecting" one of your drawings.

```shell
$ python3 main.py --loop once  # will loop once
$ python3 main.py --loop 2  # will loop two times
$ python3 main.py  # will loop once
$ python3 main.py --loop infinite
```

### Headless running
If you want to run this script without a console to take inputs (e.g. via a crontab or whatever),
you can pass command line arguments for every input:
    
```shell
# Setting where the source image is
$ python3 main.py --image /path/to/image  # path can be relative, absolute, or a HTTP[S] URI.

# Controlling cursor boundaries
# -X: The start of the cursor (horizontally, left)
# -Y: The start of the cursor (vertically, top)
# -H: The end of the cursor (horizontally, right)
# -V: The end of the cursor (vertically, bottom)
$ python3 main.py -X 0 -Y 0 -H 240 -V 135

# Painting a 12x16 image called "box.png" (this command won't ask for any input whatsoever):
$ python3 main.py -X 100 -Y 100 -H 112 -V 116 -I $HOME/Downloads/box.png
```
