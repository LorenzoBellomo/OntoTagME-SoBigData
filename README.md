# OntoTagME API Documentation
OntoTagME is an _Entity Linker_ that is built for working on biologically-relevant texts.
OntoTagME processes biological texts provided by the user and extracts a set of spot, linking them with the relevant page of WikiData. 
You can annotate snippets of various lengths of texts. 
OntoTagME is also fully integrated with [PubTator](https://www.ncbi.nlm.nih.gov/research/pubtator/), a Named Entity Recognition tool specialized for biology. 
If you need to annotate a biological paper (identified by a PubMed ID or a PubMed Central ID), then OntoTagME will integrate its results with the ones from PubTator, thus increasing the quality of the annotation. 
You can query OntoTagME through REST APIs as described in the following. 

## Version
OntoTagME is using a _biological subset_ of the English Wikidata dump, version: 2022-10

## How to Annotate
OntoTagME works in two different ways:
- **TEXT QUERY**: in this case only OntoTagME is used as a back-end
- **PAPER QUERY**: in this case, results from OntoTagME and PubTator are integrated together. If the paper is not present in PubTator, then the resulting annotations will be provided by OntoTagME only.

A generic annotation looks like the following. 
```json
{
    "wid": "Identifier of the entity",
    "spot": "textual fragment referring to the entity",
    "Word": "Title of the Wikidata page",
    "categories": "LIST of categories assigned to the entity",
    "start_pos": "index of the first character of the spot in the text",
    "end_pos": "index of the last character of the spot in the text",
    "section": "section where the entity was extracted",
    "annotation_mode": "info regarding which annotator found the annotation (PubTator or OntoTagME)",
    "wiki_url": "url of the wikidata page regarding the entity, if applicable"
}
```

## Endpoint URL
```
https://ontotagme-entity-linker.d4science.org/ 
```

## Annotate by PubMed ID
In order to get the annotations for a full text on PubMed Central or an abstract on PubMed, then you can use the endpoint
```
https://ontotagme-entity-linker.d4science.org/annotate_by_id
```
The only supported query is POST.
The annotation will be peformed by OntoTagME and enriched with PubTator.
### Parameters
- a_id - _required_- the article ID to annotate. Formatted like PMCxxxxxx for full-text annotations, and PMxxxxx for annotating abstracts only. 
- gcube-token - _required_ - the D4Science Service Authorization Token.
- mode - _defaults to 'pmc'_ - in this field, specify 'pm' if you want to annotate abstracts, or 'pmc' if you want to annotate full-texts. 
### EXAMPLE
To test this endpoint through CURL (change the gcube token with yours):
```
curl --location --request POST 'https://ontotagme-entity-linker.d4science.org/annotate_by_id' \
--header 'gcube-token: XXXX' \
--header 'Content-Type: application/json' \
--data-raw '{
    "a_id" : "PMC6982432"
}'
```
### HTTP Errors
- 501 (NOT IMPLEMENTED) - The resource you requested is not a valid OntoTagME service.
- 401 (UNAUTHORIZED) - You haven't provided a Service Authorization Token or it is not valid.
- 400 (BAD REQUEST) - There are issues with the parameters you have sent (or not sent). Check the response message for details.
- 500 (INTERNAL SERVER ERROR) - Something went wrong on the side of OntoTagME. 


## Annotate text snippet
In order to get the annotations for a single text snippet, use this url
```
https://ontotagme-entity-linker.d4science.org/annotate_by_text
```
The only supported query is POST.
The annotation will be peformed by OntoTagME alone.
### Parameters
- text - _required_- the text snippet to annotate
- gcube-token - _required_ - the D4Science Service Authorization Token.
### EXAMPLE
To test this endpoint through CURL (change the gcube token with yours):
```
curl --location --request POST 'https://ontotagme-entity-linker.d4science.org/annotate_by_text' \
--header 'gcube-token: XXXX' \
--header 'Content-Type: application/json' \
--data-raw '{
    "text" : "ESR1 mutations were more frequently observed in the circulating cell-free DNA of MBC patients than in PBC patients among the Chinese cohort."
}'
```
### HTTP Errors
- 501 (NOT IMPLEMENTED) - The resource you requested is not a valid OntoTagME service.
- 401 (UNAUTHORIZED) - You haven't provided a Service Authorization Token or it is not valid.
- 400 (BAD REQUEST) - There are issues with the parameters you have sent (or not sent). Check the response message for details.
- 500 (INTERNAL SERVER ERROR) - Something went wrong on the side of OntoTagME. 

## Annotate document divided in sections
When you have a document divided in sections, rather than using annotating the text fully, it is better to annotate the sections one by one. 
For this purpose, you can use the endpoint:
```
https://ontotagme-entity-linker.d4science.org/annotate_sections
```
The only supported query is POST.
The annotation will be peformed by OntoTagME.
### Parameters
- article - _required_- Dictionary where the keys are the names of the provided sections, and the values are the text snippets to be annotated.
- gcube-token - _required_ - the D4Science Service Authorization Token.
### EXAMPLE
To test this endpoint through CURL (change the gcube token with yours):
```
curl --location --request POST 'https://ontotagme-entity-linker.d4science.org/annotate_sections' \
--header 'gcube-token: XXXX' \
--header 'Content-Type: application/json' \
--data-raw '
    "article" : {
        "INTRO": "ESR1 mutation and its possible relation to endocrine therapy resistance in ER-positive breast cancers have been studied with respect to genetic sequencing data from Western patients but rarely from Chinese patients.",
        "RESULTS": The ESR1 mutation rate was 1% (3/297) in PBC patients and 18.6% (8/43) in MBC patients.",
        "CORE": "ESR1 mutations were more frequently observed in the circulating cell-free DNA of MBC patients than in PBC patients among the Chinese cohort."
}'
```
### HTTP Errors
- 501 (NOT IMPLEMENTED) - The resource you requested is not a valid OntoTagME service.
- 401 (UNAUTHORIZED) - You haven't provided a Service Authorization Token or it is not valid.
- 400 (BAD REQUEST) - There are issues with the parameters you have sent (or not sent). Check the response message for details.
- 500 (INTERNAL SERVER ERROR) - Something went wrong on the side of OntoTagME. 
