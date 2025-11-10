"""Custom exception classes for the application.

These exceptions provide semantic meaning and allow proper HTTP status code mapping
without relying on fragile string matching.
"""


class AppException(Exception):
    """Base exception for all application-specific exceptions."""

    def __init__(self, message: str) -> None:
        self.message: str = message
        super().__init__(self.message)


# 404 Not Found Exceptions
class NotFoundException(AppException):
    """Base class for resource not found errors (maps to HTTP 404)."""


class TaskNotFoundException(NotFoundException):
    """Raised when a requested task is not found."""

    def __init__(self, task_id: str | None = None) -> None:
        message = f"Task {task_id} not found" if task_id else "Task not found"
        super().__init__(message)


class ProjectNotFoundException(NotFoundException):
    """Raised when a requested project is not found."""

    def __init__(self, project_id: str | None = None) -> None:
        message = f"Project {project_id} not found" if project_id else "Project not found"
        super().__init__(message)


class SectionNotFoundException(NotFoundException):
    """Raised when a requested section is not found."""

    def __init__(self, section_id: str | None = None) -> None:
        message = f"Section {section_id} not found" if section_id else "Section not found"
        super().__init__(message)


class LabelNotFoundException(NotFoundException):
    """Raised when a requested label is not found."""

    def __init__(self, label_id: str | None = None) -> None:
        message = f"Label {label_id} not found" if label_id else "Label not found"
        super().__init__(message)


class NoteNotFoundException(NotFoundException):
    """Raised when a requested note is not found."""

    def __init__(self, note_id: str | None = None) -> None:
        message = f"Note {note_id} not found" if note_id else "Note not found"
        super().__init__(message)


class PriorityNotFoundException(NotFoundException):
    """Raised when a requested priority is not found."""

    def __init__(self, priority_id: str | None = None) -> None:
        message = f"Priority {priority_id} not found" if priority_id else "Priority not found"
        super().__init__(message)


class RecurringTaskNotFoundException(NotFoundException):
    """Raised when a requested recurring task is not found."""

    def __init__(self, recurring_task_id: str | None = None) -> None:
        message = (
            f"Recurring task {recurring_task_id} not found"
            if recurring_task_id
            else "Recurring task not found"
        )
        super().__init__(message)


class ChecklistNotFoundException(NotFoundException):
    """Raised when a requested checklist is not found."""

    def __init__(self, checklist_id: str | None = None) -> None:
        message = (
            f"Checklist {checklist_id} not found"
            if checklist_id
            else "Checklist not found"
        )
        super().__init__(message)


class ChecklistItemNotFoundException(NotFoundException):
    """Raised when a requested checklist item is not found."""

    def __init__(self, item_id: str | None = None) -> None:
        message = (
            f"Checklist item {item_id} not found"
            if item_id
            else "Checklist item not found"
        )
        super().__init__(message)


class PushSubscriptionNotFoundException(NotFoundException):
    """Raised when a requested push subscription is not found."""

    def __init__(self) -> None:
        super().__init__("No active push subscriptions found")


class MediaNotFoundException(NotFoundException):
    """Raised when a requested media item is not found."""

    def __init__(self, media_id: str | None = None) -> None:
        message = f"Media {media_id} not found" if media_id else "Media not found"
        super().__init__(message)


# 403 Forbidden Exceptions
class ForbiddenException(AppException):
    """Base class for authorization/ownership errors (maps to HTTP 403)."""


class UnauthorizedAccessException(ForbiddenException):
    """Raised when a user tries to access a resource they don't own."""

    def __init__(self, resource_type: str = "Resource") -> None:
        super().__init__(f"{resource_type} does not belong to you")


# 400 Bad Request Exceptions
class BadRequestException(AppException):
    """Base class for client errors and validation failures (maps to HTTP 400)."""


class InvalidOperationException(BadRequestException):
    """Raised when an operation cannot be performed due to business logic constraints."""


class DuplicateResourceException(BadRequestException):
    """Raised when attempting to create a resource that already exists."""

    def __init__(self, resource_type: str, identifier: str) -> None:
        super().__init__(f"{resource_type} with {identifier} already exists")


class InvalidReferenceException(BadRequestException):
    """Raised when a foreign key reference is invalid."""

    def __init__(self, message: str = "Invalid reference: one or more related entities not found") -> None:
        super().__init__(message)


class CircularReferenceException(BadRequestException):
    """Raised when attempting to create a circular reference in hierarchical data."""

    def __init__(self, message: str = "Circular reference detected: this operation would create an infinite loop") -> None:
        super().__init__(message)


# 401 Unauthorized Exceptions
class UnauthorizedException(AppException):
    """Base class for authentication errors (maps to HTTP 401)."""

class InvalidTokenException(UnauthorizedException):
    """Raised when an authentication token is invalid or expired."""

    def __init__(self, message: str = "Invalid or expired authentication token") -> None:
        super().__init__(message)


# 409 Conflict Exceptions
class ConflictException(AppException):
    """Base class for resource conflicts (maps to HTTP 409)."""


# 503 Service Unavailable Exceptions
class ServiceUnavailableException(AppException):
    """Base class for external service failures (maps to HTTP 503)."""

    def __init__(self, message: str = "External service temporarily unavailable") -> None:
        super().__init__(message)


class ExternalServiceException(ServiceUnavailableException):
    """Raised when an external service (OAuth provider, API, etc.) fails or is unreachable."""

    def __init__(self, service_name: str, details: str | None = None) -> None:
        message = f"{service_name} is currently unavailable"
        if details:
            message += f": {details}"
        super().__init__(message)
