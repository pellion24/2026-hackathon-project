from PyPDF2 import PdfReader
import sys

reader = PdfReader(sys.argv[1])
fields = reader.get_fields() or {}
for k in sorted(fields.keys()):
    print(k)
