#!/bin/sh

tar -xvzf $1
mv RESP.TW.*.*.H/* ./RESP
rm -r RESP.TW.*.*.H
rm $1
