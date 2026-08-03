from rest_framework.views import APIView
from rest_framework.response import Response
from PyPDF2 import PdfReader
import re

class ResumeParserAPIView(APIView):

    def post(self,request):
        resume=request.FILES.get("resume")
        if not resume:
            return Response(
                {
                    "error":"Resume File is Required"
                },
                status=400
            )

        reader=PdfReader(resume)
        text=""
        for page in reader.pages:
            extracted=page.extract_text()
            if extracted:      # Prevents errors if a page has no extractable text
                text+=extracted

        text=text.strip()
        text=re.sub(r"\n+","\n",text)
        text=re.sub(r"[ \t]+","",text)
        lines=[line.strip() for line in text.split("\n")]
        text="\n".join(lines)
        return Response({
            "text":text
        })


