#!/usr/bin/env bash

set -e
set -x

OUTPUT_PATH=${1:-.}

function build_from_pypi {
    PACKAGE_NAME=$1

    if [ -z $2 ]; then
        PACKAGE_VERSION=""
    else
        PACKAGE_VERSION="==$2"
    fi
    POSTINST_TMP=postinst-${PACKAGE_NAME}
    PREREM_TMP=prerm-${PACKAGE_NAME}
    cp postinst ${POSTINST_TMP}
    cp prerm ${PREREM_TMP}
    sed -i 's/{package_name}/python3-'${PACKAGE_NAME}'/' ${POSTINST_TMP}
    sed -i 's/{package_name}/python3-'${PACKAGE_NAME}'/' ${PREREM_TMP}

    fpm --input-type "python" \
        --output-type "deb" \
        --architecture "amd64" \
        --verbose \
        --python-package-name-prefix "python3"\
        --python-bin "/usr/bin/python3" \
        --exclude "*.pyc" \
        --exclude "*.pyo" \
        --maintainer "Hyperledger <hyperledger-indy@lists.hyperledger.org>" \
        --after-install ${POSTINST_TMP} \
        --before-remove ${PREREM_TMP} \
        --package ${OUTPUT_PATH} \
        ${PACKAGE_NAME}${PACKAGE_VERSION}

    rm ${POSTINST_TMP}
    rm ${PREREM_TMP}
}

build_from_pypi ioflo 1.5.4
build_from_pypi orderedset 2.0
build_from_pypi base58 0.2.4
build_from_pypi prompt-toolkit 0.57
build_from_pypi rlp 0.5.1
build_from_pypi sha3 0.2.1
build_from_pypi raet 0.6.6
build_from_pypi pyzmq 16.0.2
build_from_pypi intervaltree 2.1.0
build_from_pypi portalocker 0.5.7
build_from_pypi sortedcontainers 1.5.7
