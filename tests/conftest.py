import pathlib

current_script_path = pathlib.Path(__file__).parent.resolve()

# This conftest.py must be directly under the 'tests' directory and will load all fixtures in the tests/fixtures dir.
pytest_plugins = [
    f"{fixture_file}".replace(f"{current_script_path}", "tests").replace("/", ".").replace(".py", "")
    for fixture_file in current_script_path.glob("fixtures/[!__]*.py")
]