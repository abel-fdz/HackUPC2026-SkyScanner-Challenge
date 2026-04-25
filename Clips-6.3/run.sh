#!/usr/bin/env bash
# Script para ejecutar CLIPS 6.3 con Wine

cd "$(dirname "$0")"
cd ..
wine ./Clips-6.3/clips.exe "$@"
