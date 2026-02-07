
from fastapi import APIRouter, HTTPException
import os
from datetime import timedelta
from google.cloud import storage
import google.auth
from google.auth.transport.requests import Request
from google.auth import impersonated_credentials


router = APIRouter(prefix="/pdf", tags=["pdf"])

# print(os.environ["SIGNER_SERVICE_ACCOUNT"])

@router.get("/health")
def health():
	return {
		"status": "ok",
	}


@router.get("/download-pdf/{id}")
def download_pdf():
	# https://storage.googleapis.com/abdul-document-test/Full.pdf
	url = generate_signed_download_url(
			bucket_name="abdul-document-test",
			object_name="test_06/full.pdf"
	)
	return {"downloadUrl": url}


def generate_signed_download_url(bucket_name: str, object_name: str, expires_minutes: int = 15):
	try:
		signer_sa = os.environ["SIGNER_SERVICE_ACCOUNT"]  # must be set

		source_credentials, project_id = google.auth.default()
		source_credentials.refresh(Request())

		signing_credentials = impersonated_credentials.Credentials(
				source_credentials=source_credentials,
				target_principal=signer_sa,
				target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
				lifetime=expires_minutes * 60,
		)

		client = storage.Client(project=project_id, credentials=signing_credentials)
		blob = client.bucket(bucket_name).blob(object_name)

		return blob.generate_signed_url(
				version="v4",
				method="GET",
				expiration=timedelta(minutes=expires_minutes),
				response_disposition=f'attachment; filename="{object_name.split("/")[-1]}"',
				response_type="application/pdf",
				credentials=signing_credentials,
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))