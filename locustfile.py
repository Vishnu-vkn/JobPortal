from locust import HttpUser, task, between


class PublicJobsUser(HttpUser):

    wait_time = between(1, 2)

    @task
    def get_public_jobs(self):
        self.client.get("/api/jobs/public/")