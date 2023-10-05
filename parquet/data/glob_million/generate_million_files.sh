#!/bin/bash

# Loop through all possible three-letter extensions
for extension in {a..z}{a..z}{a..z}; do
  touch "file.$extension"
done

