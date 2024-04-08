import json
import os
from datetime import datetime
from http import HTTPStatus
from typing import Tuple

import ulid
from boto3 import client as boto3_client

from model.email.email import EmailIn
from utils.logger import logger


class EmailUsecase:
    def __init__(self) -> None:
        """
        Initialize the EmailUsecase with an instance of the SQS client and the SQS URL.
        """
        self.__sqs_client = boto3_client("sqs", region_name=os.getenv("REGION", "ap-southeast-1"))
        self.__sqs_url = os.getenv("EMAIL_QUEUE")

    def send_email(self, email_in: EmailIn) -> Tuple[HTTPStatus, str]:
        """
        Sends an email using Amazon SQS.

        :param email_in: Object containing email details.
        :type email_in: EmailIn

        :return: A tuple containing HTTP status code and a message indicating the result of the email sending operation.
        :rtype: Tuple[HTTPStatus, str]
        """
        message = None
        try:
            timestamp = datetime.utcnow().isoformat(timespec="seconds")
            event_id = email_in.eventId or email_in.to[0]
            payload = email_in.dict()
            message_id = ulid.ulid()
            response = self.__sqs_client.send_message(
                QueueUrl=self.__sqs_url,
                MessageBody=json.dumps(payload),
                MessageDeduplicationId=f"sparcs-event-{event_id}-{timestamp}-{message_id}",
                MessageGroupId=f"sparcs-event-{event_id}",
            )
            message_id = response.get("MessageId")
            message = f"Queue message success: {message_id}"
            logger.info(message)

        except Exception as e:
            message = f"Failed to send email: {str(e)}"
            logger.error(message)
            return HTTPStatus.INTERNAL_SERVER_ERROR, message

        else:
            return HTTPStatus.OK, message

    def send_admin_invitation_email(self, email: str, temp_password: str):
        """
        Sends an invitation email to an admin.

        :param email: The email address of the admin.
        :type email: str

        :param temp_password: The temporary password of the admin.
        :type temp_password: str

        :return: None
        :rtype: None
        """
        frontend_url = os.getenv("FRONTEND_URL")
        subject = "TechTix Admin Invitation"
        salutation = "Good day,"
        body = [
            "You are invited to be an Admin of TechTix. Below are your temporary credentials:",
            f"Link: {frontend_url}/admin/login",
            f"Email: {email}",
            f"Temporary Password: {temp_password}",
            "Please change your password after logging in.",
            "Thank you!",
        ]
        regards = ["Best,"]
        email_in = EmailIn(
            to=[email],
            subject=subject,
            body=body,
            salutation=salutation,
            regards=regards,
        )
        logger.info(f"Sending event invitation email to {email}")
        self.send_email(email_in=email_in)

        return
