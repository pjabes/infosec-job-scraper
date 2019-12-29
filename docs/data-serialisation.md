# Data Serialisation 
The amount of data used within this in no way compares that to "big data".  However, this fact does not mean that particular care was made with respect to data serialisation and storage.

## Format
Comma Seperated Values (CSVs) were selected as the chosen storage format due to their tried and tested compatiblility.  

## Storage Format
Given that a keyword search is given for all of the data that we recieve.  We use a hash of the UID provided in the jobs to track whether it has been found previously.  