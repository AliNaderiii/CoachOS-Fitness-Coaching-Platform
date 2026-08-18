"""Copilot API exceptions.

Each carries a stable ``message_key`` consumed by the Phase 04 RFC 7807
exception handler, so clients always receive a safe localized envelope with no
echoed payloads.
"""

from rest_framework.exceptions import APIException, PermissionDenied, Throttled


class CopilotBadRequest(APIException):
    status_code = 400
    default_detail = "The Copilot request could not be processed."
    default_code = "copilot_bad_request"
    message_key = "error.ai_bad_request"

    def __init__(self, detail=None, message_key=None):
        super().__init__(detail=detail)
        if message_key:
            self.message_key = message_key


class CopilotFeatureDisabled(PermissionDenied):
    default_detail = "The AI Copilot is disabled."
    message_key = "error.ai_feature_disabled"


class CopilotNotAuthorized(PermissionDenied):
    default_detail = "You are not authorized for this Copilot operation."
    message_key = "error.ai_not_authorized"


class CopilotProhibitedUse(CopilotBadRequest):
    default_detail = "The request is outside the Copilot's permitted scope."
    message_key = "error.ai_prohibited_use"


class CopilotThrottled(Throttled):
    default_detail = "Copilot rate limit or quota exceeded. Try again later."
    message_key = "error.ai_quota_exceeded"

    def __init__(self, detail=None, message_key=None):
        super().__init__(detail=detail)
        if message_key:
            self.message_key = message_key


class CopilotConflict(APIException):
    status_code = 409
    default_detail = "The Copilot run state does not allow this action."
    default_code = "copilot_conflict"
    message_key = "error.ai_state_conflict"


class CopilotGone(APIException):
    status_code = 410
    default_detail = "This Copilot record has expired under the retention policy."
    default_code = "copilot_gone"
    message_key = "error.ai_expired"
