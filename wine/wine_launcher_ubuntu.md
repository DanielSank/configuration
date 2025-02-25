Make a desktop launcher file `myprogram.desktop` with the following contents:

    [Desktop Entry]
    Name=myprogram
    comment=whatever
    Exec=/home/daniel/bin/myprogram.sh
    Terminal=false
    Type=Application
    GenericName=whatever
    Icon=/home/daniel/Pictures/icons/myprogram-icon.png

Then create `/home/daniel/bin/myprogram.sh` with the following contents:

    #!/bin/bash

    export ENVIRONMENT_VAR=whatever

    cd $HOME/src/location/of/executable

    WINEPREFIX="$HOME/.wine" wine myprogram.exe

Make sure this file can be executed.
