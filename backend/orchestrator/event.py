from enum import Enum


class Event(Enum):

    CV_UPLOADED = "cv_uploaded"

    PROFILE_CREATED = "profile_created"

    JOBS_FOUND = "jobs_found"

    ATS_COMPLETED = "ats_completed"

    TRANSLATION_COMPLETED = "translation_completed"

    CERTIFICATIONS_FOUND = "certifications_found"

    INTERVIEW_READY = "interview_ready"