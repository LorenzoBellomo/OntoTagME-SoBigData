#!/bin/sh

cd /opt
CONTAINER_ALREADY_STARTED="CONTAINER_ALREADY_STARTED_PLACEHOLDER"
if [ ! -e $CONTAINER_ALREADY_STARTED ]
then
  touch $CONTAINER_ALREADY_STARTED
   cp -r /opt/multi-tagme-master_final/converters/repository tagme
   cp config.sample.xml tagme
   cp config.sample.xml multi-tagme-master_final/rest-service
   cp WikipediaAnchorParser.java tagme/src/it/acubelab/tagme/preprocessing/anchors
   cp BestAnchors.java tagme/src/it/acubelab/tagme/preprocessing
   cp wikipatterns.properties tagme/repository

   cd tagme
   ant get-deps

   cd /opt/multi-tagme-master_final/converters
   echo "\nDownloading necessary files...\n"
   python3 downloader.py
   unzip final_csv.zip
   rm final_csv.zip
   echo "\nConversion csv2tagme...\n"
   python3 csv_2_tagme.py

   rm category.csv
   rm page.csv
   rm pagelinks.csv

   echo "TAGME CONFIGURATION"
   TAGME_PATH="/opt/tagme"

   # removing current data
   mv sql_tagme/enwiki-latest-page.sql            "$TAGME_PATH/repository/en/source/enwiki-latest-page.sql"
   mv sql_tagme/enwiki-latest-pagelinks.sql       "$TAGME_PATH/repository/en/source/enwiki-latest-pagelinks.sql"
   mv sql_tagme/enwiki-latest-pages-articles.xml  "$TAGME_PATH/repository/en/source/enwiki-latest-pages-articles.xml"
   mv sql_tagme/enwiki-latest-redirect.sql        "$TAGME_PATH/repository/en/source/enwiki-latest-redirect.sql"

   cd /opt/tagme/stopwords
   cp en.stopword mice.stopword

   echo "BEGIN TAGME INDEXING"
   cd $TAGME_PATH;
   ant index.light -Dconfig.file=config.sample.xml -Dmem=4G -Dlang=en
   ant index.light -Dconfig.file=config.sample.xml -Dmem=4G -Dlang=mice
fi

echo "START ADAPTER SERVER"
cd /opt/multi-tagme-master_final/adapter_rest
python3 app.py &

echo "START SERVER"
cd /opt/multi-tagme-master_final/rest-service
gradle ant_build
gradle bootRun > log.txt