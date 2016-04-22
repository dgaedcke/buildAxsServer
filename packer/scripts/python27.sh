PYTHON_VERSION=2.7.8
PYTHON_NAME="Python-$PYTHON_VERSION"

pushd .
cd /tmp
echo "=> Downloading Python $PYTHON_VERSION"
wget "https://www.python.org/ftp/python/2.7.8/${PYTHON_NAME}.tgz"
tar xf "${PYTHON_NAME}.tgz"
cd "$PYTHON_NAME"
echo "=> Compiling and installing Python $PYTHON_VERSION"
./configure --prefix=/opt/python2.7
make -j5
make install
rm -rf "${PYTHON_NAME}.tgz" "${PYTHON_NAME}/"
popd
