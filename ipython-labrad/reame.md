Source `ipython.sh` to start the session.
When you do this it will try to run ipython with user profile "daniel".
For that to work, there needs to be an ipython profile with that name; at this writing it lives in `~/.ipython/profile_daniel`.
Inside that directory there is a file `ipython_config.py`.
Put the `ipython_config.py` from this repository in that location.
There is a line like
```
c.InteractiveShellApp.exec_files = ['path/to/python-labrad.py']
```
and the `python-labrad.py` file can be anywhere you want.

