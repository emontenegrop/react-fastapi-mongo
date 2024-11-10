#! /bin/bash

# for i in {1..1000}
# do
# curl -X 'POST' \
#   'http://172.27.9.50:8092/api/v1/document_file/' \
#   -H 'accept: application/json' \
#   -H 'Content-Type: multipart/form-data' \
#   -F 'file=@test.pdf;type=application/pdf' \
#   -F 'document={ "file_type_id": 666, "aplication_id": "FILES", "created_by": 456, "person_id": 456 }'
#   echo -e "\nDOCUMENTO : [ " $i " ] "
# done

for i in {1..1000}
do
curl -X 'POST' \
 'http://172.27.9.50:8092/api/v1/document_file/signed_validate/' \
 -H 'accept: application/json' \
 -H 'Content-Type: multipart/form-data' \
 -F 'file=@test-signed.pdf;type=application/pdf' \
 -F 'document={ "file_type_id": 666, "aplication_id": "FILES", "created_by": 123, "person_id": 123 }' \
 -F 'cedula_ruc=1715376352'
 echo -e "\nDOCUMENTO : [ " $i " ] "
done
