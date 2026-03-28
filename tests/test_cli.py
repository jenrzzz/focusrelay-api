from focusrelay_api.cli import build_args


class TestBuildArgs:
    def test_skips_none_values(self):
        args = build_args(completed=None, search=None)
        assert args == []

    def test_option_bool_passes_explicit_value(self):
        args = build_args(completed=True, flagged=False)
        assert "--completed" in args
        assert args[args.index("--completed") + 1] == "true"
        assert "--flagged" in args
        assert args[args.index("--flagged") + 1] == "false"

    def test_flag_bool_presence_only_when_true(self):
        args = build_args(flags={"include_total_count"}, include_total_count=True)
        assert args == ["--include-total-count"]

    def test_flag_bool_omitted_when_false(self):
        args = build_args(flags={"include_total_count"}, include_total_count=False)
        assert args == []

    def test_underscore_to_hyphen(self):
        args = build_args(due_before="2026-01-01T00:00:00Z")
        assert args == ["--due-before", "2026-01-01T00:00:00Z"]

    def test_int_values(self):
        args = build_args(limit=10)
        assert args == ["--limit", "10"]

    def test_string_values(self):
        args = build_args(search="groceries", project="Home")
        assert "--search" in args
        assert "groceries" in args
        assert "--project" in args
        assert "Home" in args

    def test_mixed_flags_and_options(self):
        args = build_args(
            flags={"include_total_count"},
            completed=True,
            include_total_count=True,
            limit=5,
        )
        assert "--completed" in args
        assert args[args.index("--completed") + 1] == "true"
        assert "--include-total-count" in args
        assert "--limit" in args
        assert args[args.index("--limit") + 1] == "5"
        # Flag should NOT have a value after it
        idx = args.index("--include-total-count")
        if idx + 1 < len(args):
            assert args[idx + 1].startswith("--") or args[idx + 1].isdigit() or args[idx + 1] == "true"
