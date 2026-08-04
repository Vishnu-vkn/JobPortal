from rest_framework.views import APIView
from rest_framework.response import Response
from PyPDF2 import PdfReader
import re
from .skills import SKILLS,EDUCATION

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
        lines=[line.strip() for line in text.split("\n") if line.strip()]
        text="\n".join(lines)

        #name
        name=lines[0] if lines else None

        #skills
        found_skills = []

        for skill in SKILLS:
            if skill.lower() in text.lower():
                found_skills.append(skill)

        #experience
        experience=None
        match=re.search(r"(\d+)\s+years?",text,re.IGNORECASE)

        if match:
            experience=int(match.group(1))

        #education
        education=None
        for degree in EDUCATION:
            if degree.lower() in text.lower():
                education=degree
                break

        email = None

        match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",text)

        if match:
            email = match.group()

        phone = None

        match = re.search(r"\+?\d[\d\s-]{8,}\d", text)

        if match:
            phone = match.group()

        return Response({
            "name":name,
            "email": email,
            "phone":phone,
            "skills":found_skills,
            "experience":experience,
            "education":education
        })


