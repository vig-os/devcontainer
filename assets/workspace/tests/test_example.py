"""Example tests for {{SHORT_NAME}}."""


def test_example():
    """Example test that always passes."""
    assert True


def test_import():
    """Test that the package can be imported."""
    import template_project  # noqa: F401 - renamed to project name by init-workspace.sh

    assert template_project.__version__ == "0.1.0"
