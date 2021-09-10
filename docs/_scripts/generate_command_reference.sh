#!/bin/bash

COMMAND=$1
OUTFILE="docs/docs/command-reference/$COMMAND.md"

echo "# $COMMAND Command" > $OUTFILE
echo '' >> $OUTFILE
echo '```bash' >> $OUTFILE
echo "nbautoexport $COMMAND --help" >> $OUTFILE
echo '```' >> $OUTFILE
echo '' >> $OUTFILE
echo '```' >> $OUTFILE
echo "$(nbautoexport $COMMAND --help)" >> $OUTFILE
echo '```' >> $OUTFILE
