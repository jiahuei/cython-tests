# OOO

A basic FastAPI SQLite counter app.

## Compiling the Library

1. Create an environment with `gcc`: `micromamba create -n test312 python=3.12 gcc`
2. Activate: `micromamba activate test312`
3. Install dependencies: `pip install . && pip uninstall ooo`
4. Compile: `python build.py`
5. Run the server: `python server.py`
6. Test it: `curl -X PUT localhost:6969/api/v1/counters/sqlite/increment?name=abc`
