#!/bin/bash

flex -o choco.c choco.l
clang -o choco -ll choco.c
