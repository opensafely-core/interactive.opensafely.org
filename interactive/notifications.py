from environs import Env

from services import slack


env = Env()


def notify_analysis_request_submitted(title, codelist, created_by):
    job_server_url = slack.link(
        env.str("JOB_SERVER_JOBS_URL", default=""),
        "job server",
    )
    message = (
        f"{created_by} submitted an analysis request called {title} for {codelist}\n"
    )
    message += f"Please start the job in {job_server_url}"
    slack.post(text=message)


def notify_registration_request_submitted(full_name, job_title, organisation, email):
    full_name_link = slack.link(email, full_name, is_email=True)
    message = f"{full_name_link} ({job_title}) from {organisation} has registered their interest in using OpenSAFELY Interactive"
    slack.post(text=message)
