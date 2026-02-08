from bulk_rename.cli import (
    generate_new_name,
    find_files,
    sort_files,
    generate_rename_plan,
    show_preview,
    confirm_action,
    save_backup,
    validate_rename_plan,
    execute_rename,
)
from pathlib import Path
import pytest


def test_generate_new_name_basic():
    """Test basic filename generation with zero-padded numbering."""
    result = generate_new_name("track_{:03d}", 1, "opus")
    assert result == "track_001.opus"


def test_generate_new_name_double_digit():
    """Test filename generation with two-digit zero padding."""
    result = generate_new_name("video_{:02d}", 25, "mkv")
    assert result == "video_25.mkv"


def test_generate_new_name_starting_from_zero():
    """Test filename generation starting from index 0."""
    result = generate_new_name("file_{:03d}", 0, "txt")
    assert result == "file_000.txt"


def test_generate_new_name_large_number():
    """Test filename generation with number exceeding padding width."""
    result = generate_new_name("track_{:02d}", 999, "mp3")
    assert result == "track_999.mp3"


def test_find_files(tmp_path):
    """Test finding files with a specific extension in directory."""
    (tmp_path / "video1.mp4").touch()
    (tmp_path / "video2.mp4").touch()
    (tmp_path / "image.jpg").touch()

    result = find_files(tmp_path, "mp4")

    assert set(result) == {tmp_path / "video1.mp4", tmp_path / "video2.mp4"}


def test_sort_files_starting_letters():
    """Test sorting files with different starting letters."""
    files = [
        Path("/tmp/z_track.opus"),
        Path("/tmp/a_track.opus"),
        Path("/tmp/m_track.opus"),
        Path("/tmp/b_track.opus"),
    ]

    result = sort_files(files)

    assert result == [
        Path("/tmp/a_track.opus"),
        Path("/tmp/b_track.opus"),
        Path("/tmp/m_track.opus"),
        Path("/tmp/z_track.opus"),
    ]


def test_sort_files_same_name():
    """Test sorting files with the same name but different directories."""
    files = [
        Path("/tmp/track.opus"),
        Path("/home/user/music/track.opus"),
        Path("/home/tmp/track.opus"),
    ]

    result = sort_files(files)

    assert result == [
        Path("/tmp/track.opus"),
        Path("/home/user/music/track.opus"),
        Path("/home/tmp/track.opus"),
    ]


def test_sort_files_case_insensitive():
    """Test sorting files with uppercase and lowercase starting letters."""
    files = [
        Path("/tmp/Z_track.opus"),
        Path("/tmp/m_track.opus"),
        Path("/tmp/A_track.opus"),
        Path("/tmp/b_track.opus"),
    ]

    result = sort_files(files)

    assert result == [
        Path("/tmp/A_track.opus"),
        Path("/tmp/Z_track.opus"),
        Path("/tmp/b_track.opus"),
        Path("/tmp/m_track.opus"),
    ]


def test_sort_files_starting_numbers():
    """Test sorting files with different starting numbers."""
    files = [
        Path("/tmp/4_track.opus"),
        Path("/tmp/3_track.opus"),
        Path("/tmp/1_track.opus"),
        Path("/tmp/2_track.opus"),
    ]

    result = sort_files(files)

    assert result == [
        Path("/tmp/1_track.opus"),
        Path("/tmp/2_track.opus"),
        Path("/tmp/3_track.opus"),
        Path("/tmp/4_track.opus"),
    ]


def test_sort_files_starting_special_characters():
    """Test sorting files with starting special characters."""
    files = [
        Path("/tmp/_track.opus"),
        Path("/tmp/-track.opus"),
        Path("/tmp/@track.opus"),
    ]

    result = sort_files(files)

    assert result == [
        Path("/tmp/-track.opus"),
        Path("/tmp/@track.opus"),
        Path("/tmp/_track.opus"),
    ]


def test_generate_rename_plan_basic():
    """Test generating a rename plan starting from index 1."""
    files = [
        Path("tmp/a.mp4"),
        Path("tmp/b.mp4"),
        Path("tmp/c.mp4"),
    ]

    result = generate_rename_plan(files, "video_{:03d}", 1)

    assert result == [
        (Path("tmp/a.mp4"), Path("tmp/video_001.mp4")),
        (Path("tmp/b.mp4"), Path("tmp/video_002.mp4")),
        (Path("tmp/c.mp4"), Path("tmp/video_003.mp4")),
    ]


def test_generate_rename_plan_starting_from_zero():
    """Test generating a rename plan starting from index 0."""
    files = [
        Path("tmp/a.mp4"),
        Path("tmp/b.mp4"),
        Path("tmp/c.mp4"),
    ]

    result = generate_rename_plan(files, "video_{:03d}", 0)

    assert result == [
        (Path("tmp/a.mp4"), Path("tmp/video_000.mp4")),
        (Path("tmp/b.mp4"), Path("tmp/video_001.mp4")),
        (Path("tmp/c.mp4"), Path("tmp/video_002.mp4")),
    ]


def test_generate_rename_plan_preserves_directory():
    """Test that the rename plan preserves the original directory."""
    files = [
        Path("/home/user/videos/a.mp4"),
        Path("/tmp/other/b.mp4"),
        Path("relative/path/c.mp4"),
    ]

    result = generate_rename_plan(files, "video_{:02d}", 1)

    assert result == [
        (Path("/home/user/videos/a.mp4"), Path("/home/user/videos/video_01.mp4")),
        (Path("/tmp/other/b.mp4"), Path("/tmp/other/video_02.mp4")),
        (Path("relative/path/c.mp4"), Path("relative/path/video_03.mp4")),
    ]


def test_generate_rename_plan_same_directory():
    """Test generating a rename plan for files in the same directory."""
    files = [
        Path("a.mp4"),
        Path("b.mp4"),
    ]

    result = generate_rename_plan(files, "video_{:02d}", 1)

    assert result == [
        (Path("a.mp4"), Path("video_01.mp4")),
        (Path("b.mp4"), Path("video_02.mp4")),
    ]


def test_validate_rename_plan_no_conflicts(tmp_path):
    """All files exist, no target conflicts."""
    (tmp_path / "a.mp4").touch()
    plan = [(tmp_path / "a.mp4", tmp_path / "video_001.mp4")]

    conflicts = validate_rename_plan(plan)

    assert conflicts == []


def test_validate_rename_plan_target_exists(tmp_path):
    """Target file already exists."""
    (tmp_path / "a.mp4").touch()
    (tmp_path / "video_001.mp4").touch()

    plan = [(tmp_path / "a.mp4", tmp_path / "video_001.mp4")]

    conflicts = validate_rename_plan(plan)

    assert len(conflicts) == 1
    assert conflicts[0][0] == tmp_path / "a.mp4"
    assert conflicts[0][1] == tmp_path / "video_001.mp4"
    assert "already exists" in conflicts[0][2].lower()


def test_validate_rename_plan_source_missing(tmp_path):
    """Source file doesn't exist."""
    plan = [(tmp_path / "a.mp4", tmp_path / "video_001.mp4")]

    conflicts = validate_rename_plan(plan)

    assert len(conflicts) == 1
    assert "not found" in conflicts[0][2].lower()


def test_validate_rename_plan_one_error_per_operation(tmp_path):
    """One operation should produce at most one error."""
    (tmp_path / "video_001.mp4").touch()

    plan = [(tmp_path / "b.mp4", tmp_path / "video_001.mp4")]

    conflicts = validate_rename_plan(plan)

    assert len(conflicts) == 1


def test_show_preview_success(capsys, tmp_path):
    """Test showing preview without conflicts."""
    (tmp_path / "a.mp4").touch()
    (tmp_path / "b.mp4").touch()

    plan = [
        (tmp_path / "a.mp4", tmp_path / "video_001.mp4"),
        (tmp_path / "b.mp4", tmp_path / "video_002.mp4"),
    ]

    show_preview(plan)
    captured = capsys.readouterr()

    assert captured.out == (
        f"✅ {tmp_path}/a.mp4 -> {tmp_path}/video_001.mp4\n"
        f"✅ {tmp_path}/b.mp4 -> {tmp_path}/video_002.mp4\n"
    )


def test_show_preview_conflicts(capsys, tmp_path):
    """Test showing preview for conflicts."""
    (tmp_path / "b.mp4").touch()
    (tmp_path / "video_002.mp4").touch()

    plan = [
        (tmp_path / "a.mp4", tmp_path / "video_001.mp4"),
        (tmp_path / "b.mp4", tmp_path / "video_002.mp4"),
    ]

    show_preview(plan)
    captured = capsys.readouterr()

    assert captured.out == (
        f"❌ {tmp_path}/a.mp4 -> {tmp_path}/video_001.mp4 [Source file is not found]\n"
        f"❌ {tmp_path}/b.mp4 -> {tmp_path}/video_002.mp4 [Target file already exists]\n"
    )


def test_show_preview_empty(capsys):
    """Test showing preview for zero operations."""
    plan = []

    show_preview(plan)
    captured = capsys.readouterr()

    assert captured.out == ""


@pytest.mark.parametrize(
    "user_input, expected",
    [
        pytest.param("y", True, id="y"),
        pytest.param("Y", True, id="Y"),
        pytest.param("yes", True, id="yes"),
        pytest.param("YES", True, id="YES"),
        pytest.param("yEs", True, id="yes_mixed"),
        pytest.param(" Yes ", True, id="yes_spaces"),
        pytest.param("n", False, id="n"),
        pytest.param("N", False, id="N"),
        pytest.param("no", False, id="no"),
        pytest.param("NO", False, id="NO"),
        pytest.param("nO", False, id="no_mixed"),
        pytest.param(" No ", False, id="no_spaces"),
        pytest.param("blabla", False, id="invalid"),
        pytest.param("", False, id="empty"),
    ],
)
def test_confirm_action(monkeypatch, user_input, expected):
    """Test confirming action with various inputs."""
    monkeypatch.setattr("builtins.input", lambda _: user_input)
    assert confirm_action() is expected


def test_save_backup_nonempty(tmp_path):
    """Test saving two operations to a backup file."""
    plan = [
        (Path("tmp/a.mp4"), Path("tmp/video_001.mp4")),
        (Path("tmp/b.mp4"), Path("tmp/video_002.mp4")),
    ]

    backup_file = save_backup(plan, tmp_path)

    assert backup_file.exists()
    assert backup_file.read_text() == (
        "tmp/a.mp4 -> tmp/video_001.mp4\ntmp/b.mp4 -> tmp/video_002.mp4\n"
    )


def test_save_backup_empty(tmp_path):
    """Test saving zero operations to a backup file."""
    plan = []

    backup_file = save_backup(plan, tmp_path)

    assert backup_file.exists()
    assert backup_file.read_text() == ""


def test_execute_rename_nonempty(tmp_path, capsys):
    """Test executing rename for a plan without conflicts."""
    (tmp_path / "a.mp4").touch()
    (tmp_path / "b.mp4").touch()

    plan = [
        (tmp_path / "a.mp4", tmp_path / "video_001.mp4"),
        (tmp_path / "b.mp4", tmp_path / "video_002.mp4"),
    ]

    execute_rename(plan)
    expected = capsys.readouterr()

    assert (tmp_path / "video_001.mp4").exists()
    assert (tmp_path / "video_002.mp4").exists()
    assert expected.out == ""


def test_execute_rename_conflics(tmp_path, capsys):
    """Test executing rename for a plan with conflicts."""
    (tmp_path / "b.mp4").touch()
    (tmp_path / "video_002.mp4").touch()

    plan = [
        (tmp_path / "a.mp4", tmp_path / "video_001.mp4"),
        (tmp_path / "b.mp4", tmp_path / "video_002.mp4"),
    ]

    execute_rename(plan)
    captured = capsys.readouterr()

    assert (tmp_path / "b.mp4").exists()
    assert (tmp_path / "video_002.mp4").exists()
    assert captured.out == (
        f"⚠️ [SKIPPED] {tmp_path}/a.mp4 -> {tmp_path}/video_001.mp4 [Source file is not found]\n"
        f"⚠️ [SKIPPED] {tmp_path}/b.mp4 -> {tmp_path}/video_002.mp4 [Target file already exists]\n"
    )


def test_execute_rename_empty(capsys):
    """Test executing rename for an empty plan."""
    plan = []

    execute_rename(plan)
    captured = capsys.readouterr()

    assert captured.out == ""
