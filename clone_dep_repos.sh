#!/bin/sh
echo "Downloading the plugin source code that the project depends on to the upper-level directory..."
git clone https://github.com/Mooling0602/Auto-UUID-API-MCDR.git ../Auto-UUID-API-MCDR
echo "Finished: auto_uuid_api"
git clone https://github.com/Mooling0602/LocationAPI-MCDR.git ../LocationAPI-MCDR
echo "Finished: location_api"
echo "Done. If pyrightconfig.json exists, lsp will work fine."
