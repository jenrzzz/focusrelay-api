import hmac

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

from .cli import FocusRelayError, build_args, run_focusrelay
from .config import settings

app = FastAPI(title="FocusRelay API", version="0.1.0")


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if not settings.api_token:
        return await call_next(request)
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
    else:
        token = ""
    if not hmac.compare_digest(token, settings.api_token):
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    return await call_next(request)


@app.exception_handler(FocusRelayError)
async def focusrelay_error_handler(request: Request, exc: FocusRelayError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )


# --- Task filter params shared between /tasks and /tasks/counts ---

TASK_FILTER_PARAMS = dict(
    completed=(bool | None, Query(default=None)),
    flagged=(bool | None, Query(default=None)),
    available_only=(bool | None, Query(default=None)),
    inbox_view=(str | None, Query(default=None)),
    project=(str | None, Query(default=None)),
    tags=(str | None, Query(default=None, description="Comma-separated tag names")),
    due_before=(str | None, Query(default=None)),
    due_after=(str | None, Query(default=None)),
    planned_before=(str | None, Query(default=None)),
    planned_after=(str | None, Query(default=None)),
    defer_before=(str | None, Query(default=None)),
    defer_after=(str | None, Query(default=None)),
    completed_before=(str | None, Query(default=None)),
    completed_after=(str | None, Query(default=None)),
    search=(str | None, Query(default=None)),
    inbox_only=(bool | None, Query(default=None)),
    project_view=(str | None, Query(default=None)),
    max_estimated_minutes=(int | None, Query(default=None)),
    min_estimated_minutes=(int | None, Query(default=None)),
    include_total_count=(bool, Query(default=False)),
)

TASK_FLAGS = {"include_total_count"}


def _task_filter_args(**kwargs) -> list[str]:
    return build_args(flags=TASK_FLAGS, **kwargs)


@app.get("/tasks/counts")
async def get_task_counts(
    completed: bool | None = None,
    flagged: bool | None = None,
    available_only: bool | None = None,
    inbox_view: str | None = None,
    project: str | None = None,
    tags: str | None = None,
    due_before: str | None = None,
    due_after: str | None = None,
    planned_before: str | None = None,
    planned_after: str | None = None,
    defer_before: str | None = None,
    defer_after: str | None = None,
    completed_before: str | None = None,
    completed_after: str | None = None,
    search: str | None = None,
    inbox_only: bool | None = None,
    project_view: str | None = None,
    max_estimated_minutes: int | None = None,
    min_estimated_minutes: int | None = None,
    include_total_count: bool = False,
):
    args = _task_filter_args(
        completed=completed, flagged=flagged, available_only=available_only,
        inbox_view=inbox_view, project=project, tags=tags,
        due_before=due_before, due_after=due_after,
        planned_before=planned_before, planned_after=planned_after,
        defer_before=defer_before, defer_after=defer_after,
        completed_before=completed_before, completed_after=completed_after,
        search=search, inbox_only=inbox_only, project_view=project_view,
        max_estimated_minutes=max_estimated_minutes,
        min_estimated_minutes=min_estimated_minutes,
        include_total_count=include_total_count,
    )
    result = await run_focusrelay("task-counts", args)
    return JSONResponse(content=result)


@app.get("/tasks/{task_id}")
async def get_task(task_id: str, fields: str | None = None):
    args = [task_id]
    if fields:
        args.extend(["--fields", fields])
    result = await run_focusrelay("get-task", args)
    return JSONResponse(content=result)


@app.get("/tasks")
async def list_tasks(
    completed: bool | None = None,
    flagged: bool | None = None,
    available_only: bool | None = None,
    inbox_view: str | None = None,
    project: str | None = None,
    tags: str | None = None,
    due_before: str | None = None,
    due_after: str | None = None,
    planned_before: str | None = None,
    planned_after: str | None = None,
    defer_before: str | None = None,
    defer_after: str | None = None,
    completed_before: str | None = None,
    completed_after: str | None = None,
    search: str | None = None,
    inbox_only: bool | None = None,
    project_view: str | None = None,
    max_estimated_minutes: int | None = None,
    min_estimated_minutes: int | None = None,
    include_total_count: bool = False,
    limit: int | None = None,
    cursor: str | None = None,
    fields: str | None = None,
):
    args = _task_filter_args(
        completed=completed, flagged=flagged, available_only=available_only,
        inbox_view=inbox_view, project=project, tags=tags,
        due_before=due_before, due_after=due_after,
        planned_before=planned_before, planned_after=planned_after,
        defer_before=defer_before, defer_after=defer_after,
        completed_before=completed_before, completed_after=completed_after,
        search=search, inbox_only=inbox_only, project_view=project_view,
        max_estimated_minutes=max_estimated_minutes,
        min_estimated_minutes=min_estimated_minutes,
        include_total_count=include_total_count,
    )
    args += build_args(limit=limit, cursor=cursor, fields=fields)
    result = await run_focusrelay("list-tasks", args)
    return JSONResponse(content=result)


@app.get("/projects/counts")
async def get_project_counts(
    completed: bool | None = None,
    flagged: bool | None = None,
    available_only: bool | None = None,
    inbox_view: str | None = None,
    project: str | None = None,
    tags: str | None = None,
    due_before: str | None = None,
    due_after: str | None = None,
    planned_before: str | None = None,
    planned_after: str | None = None,
    defer_before: str | None = None,
    defer_after: str | None = None,
    completed_before: str | None = None,
    completed_after: str | None = None,
    search: str | None = None,
    inbox_only: bool | None = None,
    project_view: str | None = None,
    max_estimated_minutes: int | None = None,
    min_estimated_minutes: int | None = None,
    include_total_count: bool = False,
):
    args = _task_filter_args(
        completed=completed, flagged=flagged, available_only=available_only,
        inbox_view=inbox_view, project=project, tags=tags,
        due_before=due_before, due_after=due_after,
        planned_before=planned_before, planned_after=planned_after,
        defer_before=defer_before, defer_after=defer_after,
        completed_before=completed_before, completed_after=completed_after,
        search=search, inbox_only=inbox_only, project_view=project_view,
        max_estimated_minutes=max_estimated_minutes,
        min_estimated_minutes=min_estimated_minutes,
        include_total_count=include_total_count,
    )
    result = await run_focusrelay("project-counts", args)
    return JSONResponse(content=result)


@app.get("/projects")
async def list_projects(
    status: str = "active",
    include_task_counts: bool = False,
    review_perspective: bool = False,
    review_due_before: str | None = None,
    review_due_after: str | None = None,
    completed: bool | None = None,
    completed_before: str | None = None,
    completed_after: str | None = None,
    fields: str | None = None,
    limit: int | None = None,
    cursor: str | None = None,
):
    args = build_args(
        flags={"include_task_counts", "review_perspective"},
        status=status,
        include_task_counts=include_task_counts,
        review_perspective=review_perspective,
        review_due_before=review_due_before,
        review_due_after=review_due_after,
        completed=completed,
        completed_before=completed_before,
        completed_after=completed_after,
        fields=fields,
        limit=limit,
        cursor=cursor,
    )
    result = await run_focusrelay("list-projects", args)
    return JSONResponse(content=result)


@app.get("/tags")
async def list_tags(
    status: str = "active",
    include_task_counts: bool = False,
    limit: int | None = None,
    cursor: str | None = None,
):
    args = build_args(
        flags={"include_task_counts"},
        status=status,
        include_task_counts=include_task_counts,
        limit=limit,
        cursor=cursor,
    )
    result = await run_focusrelay("list-tags", args)
    return JSONResponse(content=result)


@app.get("/health")
async def health():
    result = await run_focusrelay("bridge-health-check")
    return JSONResponse(content=result)
