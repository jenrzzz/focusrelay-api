import pytest

from focusrelay_api.cli import FocusRelayError
from focusrelay_api.config import settings


SAMPLE_TASKS = {
    "items": [{"id": "abc123", "name": "Buy milk"}],
    "returnedCount": 1,
    "nextCursor": None,
}

SAMPLE_TASK = {"id": "abc123", "name": "Buy milk", "completed": False}

SAMPLE_PROJECTS = {
    "items": [{"id": "proj1", "name": "Home"}],
    "returnedCount": 1,
    "nextCursor": None,
}

SAMPLE_TAGS = {
    "items": [{"id": "tag1", "name": "errands", "status": "active"}],
    "returnedCount": 1,
    "nextCursor": None,
}

SAMPLE_COUNTS = {"total": 42, "available": 10, "completed": 30, "flagged": 2}

SAMPLE_HEALTH = {"ok": True, "latencyMs": 50}


class TestListTasks:
    def test_basic(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_TASKS
        resp = client.get("/tasks")
        assert resp.status_code == 200
        assert resp.json() == SAMPLE_TASKS
        mock_cli.assert_called_once_with("list-tasks", [])

    def test_with_filters(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_TASKS
        resp = client.get("/tasks?completed=true&limit=5&fields=id,name")
        assert resp.status_code == 200
        args = mock_cli.call_args[0][1]
        assert "--completed" in args
        assert "true" in args
        assert "--limit" in args
        assert "5" in args
        assert "--fields" in args
        assert "id,name" in args

    def test_include_total_count_flag(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_TASKS
        resp = client.get("/tasks?include_total_count=true")
        assert resp.status_code == 200
        args = mock_cli.call_args[0][1]
        assert "--include-total-count" in args
        # Should be presence-only, no "true" value after it
        idx = args.index("--include-total-count")
        if idx + 1 < len(args):
            assert args[idx + 1] != "true"


class TestGetTask:
    def test_basic(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_TASK
        resp = client.get("/tasks/abc123")
        assert resp.status_code == 200
        assert resp.json() == SAMPLE_TASK
        mock_cli.assert_called_once_with("get-task", ["abc123"])

    def test_with_fields(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_TASK
        resp = client.get("/tasks/abc123?fields=id,name,completed")
        assert resp.status_code == 200
        mock_cli.assert_called_once_with("get-task", ["abc123", "--fields", "id,name,completed"])


class TestTaskCounts:
    def test_basic(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_COUNTS
        resp = client.get("/tasks/counts")
        assert resp.status_code == 200
        assert resp.json() == SAMPLE_COUNTS
        mock_cli.assert_called_once_with("task-counts", [])

    def test_with_filter(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_COUNTS
        resp = client.get("/tasks/counts?completed=true&project=Home")
        assert resp.status_code == 200
        args = mock_cli.call_args[0][1]
        assert "--completed" in args
        assert "--project" in args


class TestListProjects:
    def test_basic(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_PROJECTS
        resp = client.get("/projects")
        assert resp.status_code == 200
        assert resp.json() == SAMPLE_PROJECTS
        args = mock_cli.call_args[0][1]
        assert "--status" in args
        assert "active" in args

    def test_with_task_counts_flag(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_PROJECTS
        resp = client.get("/projects?include_task_counts=true")
        assert resp.status_code == 200
        args = mock_cli.call_args[0][1]
        assert "--include-task-counts" in args


class TestProjectCounts:
    def test_basic(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_COUNTS
        resp = client.get("/projects/counts")
        assert resp.status_code == 200
        mock_cli.assert_called_once_with("project-counts", [])


class TestListTags:
    def test_basic(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_TAGS
        resp = client.get("/tags")
        assert resp.status_code == 200
        assert resp.json() == SAMPLE_TAGS

    def test_with_task_counts(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_TAGS
        resp = client.get("/tags?include_task_counts=true")
        assert resp.status_code == 200
        args = mock_cli.call_args[0][1]
        assert "--include-task-counts" in args


class TestHealth:
    def test_basic(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_HEALTH
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == SAMPLE_HEALTH
        mock_cli.assert_called_once_with("bridge-health-check")


class TestErrorHandling:
    def test_cli_failure_returns_502(self, client, mock_cli):
        mock_cli.side_effect = FocusRelayError("bridge timed out")
        resp = client.get("/tasks")
        assert resp.status_code == 502
        assert resp.json() == {"error": "bridge timed out"}

    def test_timeout_returns_504(self, client, mock_cli):
        mock_cli.side_effect = FocusRelayError("Command timed out", status_code=504)
        resp = client.get("/tasks")
        assert resp.status_code == 504

    def test_binary_not_found_returns_503(self, client, mock_cli):
        mock_cli.side_effect = FocusRelayError("focusrelay binary not found", status_code=503)
        resp = client.get("/health")
        assert resp.status_code == 503


class TestAuth:
    def test_missing_token_returns_401(self, unauthed_client, mock_cli):
        resp = unauthed_client.get("/health")
        assert resp.status_code == 401
        assert resp.json() == {"error": "Unauthorized"}
        mock_cli.assert_not_called()

    def test_wrong_token_returns_401(self, unauthed_client, mock_cli):
        resp = unauthed_client.get("/health", headers={"Authorization": "Bearer wrong"})
        assert resp.status_code == 401
        mock_cli.assert_not_called()

    def test_valid_token_passes(self, client, mock_cli):
        mock_cli.return_value = SAMPLE_HEALTH
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_auth_disabled_when_no_token_configured(self, unauthed_client, mock_cli):
        settings.api_token = ""
        mock_cli.return_value = SAMPLE_HEALTH
        resp = unauthed_client.get("/health")
        assert resp.status_code == 200
