from typing import Any

from pydantic import BaseModel

# pyright: reportAny=false, reportExplicitAny=false

def apply_updates(
    model: object, update_schema: BaseModel, exclude_fields: set[str] | None = None
) -> dict[str, Any]:
    """
    Apply updates from a Pydantic schema to a SQLAlchemy model.

    Only updates fields that were explicitly set in the update schema (not None by default).
    Returns a dictionary of the fields that were updated for further processing.

    Args:
        model: SQLAlchemy model instance to update
        update_schema: Pydantic schema with update values
        exclude_fields: Fields to skip during automatic update (for custom handling)

    Returns:
        Dictionary of field names to values that were in the update schema
    """
    exclude_fields = exclude_fields or set()

    updates = update_schema.model_dump(exclude_unset=True, exclude=exclude_fields)

    for field, value in updates.items():
        if hasattr(model, field):
            setattr(model, field, value)

    return updates


async def apply_updates_async(
    model: object,
    update_schema: BaseModel,
    exclude_fields: set[str] | None = None,
    custom_handlers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Apply updates from a Pydantic schema to a SQLAlchemy model with async custom handlers.

    Only updates fields that were explicitly set in the update schema (not None by default).
    Supports custom async handlers for complex field updates.

    Args:
        model: SQLAlchemy model instance to update
        update_schema: Pydantic schema with update values
        exclude_fields: Fields to skip during automatic update (for custom handling)
        custom_handlers: Dict mapping field names to async handler functions

    Returns:
        Dictionary of field names to values that were in the update schema
    """
    exclude_fields = exclude_fields or set()
    custom_handlers = custom_handlers or {}

    # Combine exclude_fields with custom_handlers keys
    all_excludes = exclude_fields | set(custom_handlers.keys())
    updates = update_schema.model_dump(exclude_unset=True, exclude=all_excludes)

    # Apply standard field updates
    for field, value in updates.items():
        if hasattr(model, field):
            setattr(model, field, value)

    # Handle custom handlers separately
    custom_updates = update_schema.model_dump(
        exclude_unset=True, include=set(custom_handlers.keys())
    )
    for field, value in custom_updates.items():
        await custom_handlers[field](model, value, updates)

    # Return all updates
    return {**updates, **custom_updates}
