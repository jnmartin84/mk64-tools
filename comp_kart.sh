#!/bin/bash
for filename in kart*.raw; do
#    pvrtex -i "$filename" -f PAL8BPP -o "$filename.raw"
    encode "$filename"
done
