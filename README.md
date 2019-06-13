# dzSQLBuild
Docker application to build SQL deployment scripts with documentation.

## Usage

```
./windows.ps1 C:\Users\PDziemiela\Documents\GitHub\DZ_WKT
```

or 

```
./linux.sh /home/pdziemie/github/DZ_WKT
```

The need for different batch scripts on Windows verses Linux is about passing in the uid so that your output files have your ownership (not root).  The windows version just avoids the logic.




