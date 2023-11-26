rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install build
rm -rf dist
rm -rf site-packages
rm -rf lib.egg-info
pip install --platform=manylinux2014_x86_64 --implementation=cp --target=site-packages --only-binary=:all: --upgrade oracledb
python -m build
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install dist/lib-0.0.1-py3-none-any.whl --force-reinstall
python -c "import oracledb; print(oracledb.version)"
