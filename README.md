# PydisPixels Painter
This is the script I'm using to join in on the [python discord pixels event](https://pixels.pythondiscord.com)!

## Setup
Oh look, a very convenient shell script!
```shell
git clone https://github.com/EEKIM10/pydis-pixel
cd pydis-pixel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

**BEFORE YOU RUN!**

You must first get an API token from https://pixels.pythondiscord.com/show_token.
Once you've done that, create a file called `auth.txt`, and paste it in there. It must be in your current working
directory.

### Debugging
You can enable dev/verbose mode by adding `dev` to your runtime argument list:
```shell
$ python3 main.py dev
```

### Looping
(basically, native 24/7 running)

You can specify `loop [count]` in your runtime argument list, like the following:

Note: looping will use the same input values you're asked when you start the program.
This is useful for "protecting" one of your drawings.

```shell
$ python3 main.py loop  # will loop forever, unless a fatal error is raised
$ python3 main.py loop 5  # will loop 5 times, then quits.
```
