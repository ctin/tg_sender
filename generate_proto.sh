#!/bin/sh
SRC_DIR="./src/tg_sender"
DST_DIR=$SRC_DIR
poetry run protoc -I=$SRC_DIR --python_betterproto_out=$DST_DIR $SRC_DIR/tg_sender.proto
