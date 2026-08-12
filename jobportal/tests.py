from datetime import date, timedelta
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import CustomUser

from .models import (
    Employer,
    Candidate,
    Job,
    Application,
    JobType,
)


class JobFlowTest(APITestCase):

    def setUp(self):
        # Create employer user
        self.employer_user = CustomUser.objects.create_user(
            username="employer1",
            email="employer1@example.com",
            password="Test@123",
            role=CustomUser.Role.EMPLOYER,
        )

        # Create approved employer
        self.employer = Employer.objects.create(
            user=self.employer_user,
            company_name="Test Company",
            is_approved=True,
        )

        # Common job data
        self.job_data = {
            "title": "Python Developer",
            "description": "Looking for a Python developer.",
            "skills": "Python, Django, REST API",
            "experience": 1.0,
            "salary": 5000.00,
            "location": "Kochi",
            "job_type": "Full Time",
            "status": True,
            "is_featured": False,
            "deadline": date.today() + timedelta(days=30),
            "is_flagged": False,
            "minimum_score": 60,
        }

    def test_approved_employer_can_create_job(self):

        self.client.force_authenticate(user=self.employer_user)

        response = self.client.post("/api/jobs/", self.job_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Job.objects.filter(
                title="Python Developer", employer=self.employer
            ).exists()
        )

    def test_unapproved_employer_cannot_create_job(self):

        self.employer.is_approved = False
        self.employer.save()

        self.client.force_authenticate(user=self.employer_user)

        response = self.client.post("/api/jobs/", self.job_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertFalse(Job.objects.filter(title="Python Developer").exists())

    def test_candidate_cannot_create_job(self):

        candidate_user = CustomUser.objects.create_user(
            username="candidate1",
            email="candidate1@example.com",
            password="Test@123",
            role=CustomUser.Role.CANDIDATE,
        )

        self.client.force_authenticate(user=candidate_user)

        response = self.client.post("/api/jobs/", self.job_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Job.objects.count(), 0)

    def test_unauthenticated_user_cannot_create_job(self):

        response = self.client.post("/api/jobs/", self.job_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(Job.objects.count(), 0)


class ApplicationFlowTest(APITestCase):

    def setUp(self):
        # Create employer user
        self.employer_user = CustomUser.objects.create_user(
            username="employer_apply",
            email="employer_apply@example.com",
            password="Test@123",
            role=CustomUser.Role.EMPLOYER,
        )

        # Create approved employer
        self.employer = Employer.objects.create(
            user=self.employer_user,
            company_name="Test Company",
            is_approved=True,
        )

        # Create job
        self.job = Job.objects.create(
            employer=self.employer,
            title="Python Developer",
            description="Looking for a Python developer.",
            skills="Python, Django",
            experience=1.0,
            salary=5000.00,
            location="Dubai",
            job_type=JobType.FULL_TIME,
            status=True,
            is_featured=False,
            deadline=date.today() + timedelta(days=30),
            is_flagged=False,
            minimum_score=60,
        )

        # Create candidate user
        self.candidate_user = CustomUser.objects.create_user(
            username="candidate_apply",
            email="candidate_apply@example.com",
            password="Test@123",
            role=CustomUser.Role.CANDIDATE,
        )

        # Create fake resume
        self.resume = SimpleUploadedFile(
            "resume.pdf",
            b"Dummy resume content",
            content_type="application/pdf",
        )

        # Create candidate
        self.candidate = Candidate.objects.create(
            user=self.candidate_user,
            resume=self.resume,
        )

        # Authenticate candidate
        self.client.force_authenticate(user=self.candidate_user)

    @patch("jobportal.views.check_eligibility")
    @patch("jobportal.views.calculate_ats_score")
    @patch("jobportal.tasks.send_application_received_email_task.delay")
    def test_candidate_can_apply_for_job(
        self,
        mock_email,
        mock_ats,
        mock_eligibility,
    ):

        mock_ats.return_value = {
            "score": 85,
            "matched_skills": ["Python", "Django"],
        }

        response = self.client.post(f"/api/jobs/{self.job.id}/apply/", format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Application.objects.filter(candidate=self.candidate, job=self.job).exists()
        )

        application = Application.objects.get(candidate=self.candidate, job=self.job)

        self.assertEqual(application.ats_score, 85)

        self.assertEqual(application.matched_skills, ["Python", "Django"])

    def test_candidate_cannot_apply_twice(self):

        # Create existing application
        Application.objects.create(
            candidate=self.candidate,
            job=self.job,
            resume_snapshot=self.resume,
            ats_score=85,
            matched_skills=["Python", "Django"],
        )

        response = self.client.post(f"/api/jobs/{self.job.id}/apply/", format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            Application.objects.filter(candidate=self.candidate, job=self.job).count(),
            1,
        )

    def test_candidate_without_resume_cannot_apply(self):

        # Remove resume
        self.candidate.resume = None
        self.candidate.save()

        response = self.client.post(f"/api/jobs/{self.job.id}/apply/", format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            Application.objects.filter(candidate=self.candidate, job=self.job).count(),
            0,
        )

    def test_candidate_cannot_apply_to_closed_job(self):

        # Close the job
        self.job.status = False
        self.job.save()

        response = self.client.post(f"/api/jobs/{self.job.id}/apply/", format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            Application.objects.filter(candidate=self.candidate, job=self.job).count(),
            0,
        )

    def test_employer_cannot_access_another_employers_job(self):

        # Create Employer B
        employer_b_user = CustomUser.objects.create_user(
            username="employer_b",
            email="employer_b@example.com",
            password="Test@123",
            role=CustomUser.Role.EMPLOYER,
        )

        employer_b = Employer.objects.create(
            user=employer_b_user,
            company_name="Company B",
            is_approved=True,
        )

        # Create Employer B's job
        job_b = Job.objects.create(
            employer=employer_b,
            title="Private Job",
                description="Employer B private job",
            skills="Python",
            experience=1.0,
            salary=5000.00,
            location="Dubai",
            job_type=JobType.FULL_TIME,
            status=True,
            is_featured=False,
            deadline=date.today() + timedelta(days=30),
            is_flagged=False,
            minimum_score=60,
        )

        # Authenticate as Employer A
        self.client.force_authenticate(user=self.employer_user)

        # Try to access Employer B's job
        response = self.client.get(f"/api/jobs/{job_b.id}/")

        # Should not be accessible
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_employer_cannot_update_another_employers_job(self):

        # Create Employer B
        employer_b_user = CustomUser.objects.create_user(
            username="employer_b_update",
            email="employer_b_update@example.com",
            password="Test@123",
            role=CustomUser.Role.EMPLOYER,
        )

        employer_b = Employer.objects.create(
            user=employer_b_user,
            company_name="Company B",
            is_approved=True,
        )

        # Create Employer B's job
        job_b = Job.objects.create(
            employer=employer_b,
            title="Original Job",
            description="Original description",
            skills="Python",
            experience=1.0,
            salary=5000.00,
            location="Dubai",
            job_type=JobType.FULL_TIME,
            status=True,
            is_featured=False,
            deadline=date.today() + timedelta(days=30),
            is_flagged=False,
            minimum_score=60,
        )

        # Authenticate as Employer A
        self.client.force_authenticate(
        user=self.employer_user
        )

        # Try to update Employer B's job
        response = self.client.patch(
            f"/api/jobs/{job_b.id}/",
            {
                "title": "Hacked Job Title"
            },
            format="json"
        )

        # Job should not be accessible
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        # Verify original data is unchanged
        job_b.refresh_from_db()

        self.assertEqual(
            job_b.title,
            "Original Job"
        
        )
        
    
    
    def test_employer_cannot_delete_another_employers_job(self):

        employer_b_user = CustomUser.objects.create_user(
            username="employer_b_delete",
            email="employer_b_delete@example.com",
            password="Test@123",
            role=CustomUser.Role.EMPLOYER,
        )

        employer_b = Employer.objects.create(
            user=employer_b_user,
            company_name="Company B",
            is_approved=True,
        )

        job_b = Job.objects.create(
            employer=employer_b,
            title="Protected Job",
            description="This job belongs to Employer B.",
            skills="Python",
            experience=1.0,
            salary=5000.00,
            location="Dubai",
            job_type=JobType.FULL_TIME,
            status=True,
            is_featured=False,
            deadline=date.today() + timedelta(days=30),
            is_flagged=False,
            minimum_score=60,
        )

        # Authenticate as Employer A
        self.client.force_authenticate(
            user=self.employer_user
        )

        response = self.client.delete(
            f"/api/jobs/{job_b.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        # Make sure the job was NOT deleted
        self.assertTrue(
            Job.objects.filter(id=job_b.id).exists()
        )
        
class CandidateSecurityTest(APITestCase):

    def setUp(self):

        # Create Candidate A
        self.candidate_a_user = CustomUser.objects.create_user(
            username="candidate_a",
            email="candidate_a@example.com",
            password="Test@123",
            role=CustomUser.Role.CANDIDATE,
        )

        self.candidate_a = Candidate.objects.create(
            user=self.candidate_a_user,
            skills="Python, Django",
            education="B.Tech Computer Science",
            phone="9999999999",
            address="Dubai",
        )

        # Authenticate as Candidate A
        self.client.force_authenticate(
            user=self.candidate_a_user
        )

    def test_candidate_cannot_access_another_candidates_data(self):

        # Create Candidate B
        candidate_b_user = CustomUser.objects.create_user(
            username="candidate_b",
            email="candidate_b@example.com",
            password="Test@123",
            role=CustomUser.Role.CANDIDATE,
        )

        candidate_b = Candidate.objects.create(
            user=candidate_b_user,
            skills="JavaScript, React",
            education="B.Tech IT",
            phone="8888888888",
            address="Abu Dhabi",
        )

        # Candidate A tries to access Candidate B's profile
        response = self.client.get(
            f"/api/candidates/{candidate_b.id}/"
        )

        # Candidate B should not be accessible
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        
    def test_candidate_cannot_update_another_candidates_data(self):

        # Create Candidate B
        candidate_b_user = CustomUser.objects.create_user(
            username="candidate_b_update",
            email="candidate_b_update@example.com",
            password="Test@123",
            role=CustomUser.Role.CANDIDATE,
        )

        candidate_b = Candidate.objects.create(
            user=candidate_b_user,
            skills="JavaScript",
            education="B.Tech",
            phone="8888888888",
            address="Abu Dhabi",
        )

        # Candidate A tries to update Candidate B
        response = self.client.patch(
            f"/api/candidates/{candidate_b.id}/",
            {
                "skills": "Python, Django, React",
            },
            format="json"
        )

        # Should not be accessible
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        # Verify Candidate B's data was not changed
        candidate_b.refresh_from_db()

        self.assertEqual(
            candidate_b.skills,
            "JavaScript"
        )
