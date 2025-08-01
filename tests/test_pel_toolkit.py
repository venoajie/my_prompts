# /tests/test_pel_toolkit.py

import pytest
import sys
import io
import yaml
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Module under test
from scripts import pel_toolkit

# --- Test Setup & Fixtures ---

@pytest.fixture(autouse=True)
def setup_pel_toolkit_config(fs):
    """Set up a default mock environment for all tests."""
    # Create a consistent root directory and config file for all tests
    fs.create_dir("/app")
    pel_toolkit.ROOT_DIR = Path("/app")
    pel_toolkit.CONFIG_FILE = pel_toolkit.ROOT_DIR / "pel.config.yml"
    pel_toolkit.PROJECTS_DIR_NAME = "projects"
    pel_toolkit.TEMPLATES_DIR_NAME = "templates"
    pel_toolkit.PERSONAS_DIR_NAME = "personas"
    pel_toolkit.META_FILENAME = ".domain_meta"

    # Global personas path, always available
    pel_toolkit.GLOBAL_PERSONAS_PATH = pel_toolkit.ROOT_DIR / "projects/prompt_engineering/personas"
    fs.create_dir(pel_toolkit.GLOBAL_PERSONAS_PATH)

    # Default config
    config_data = {
        'resolution_paths': ['project', 'template']
    }
    fs.create_file(pel_toolkit.CONFIG_FILE, contents=yaml.dump(config_data))

    # Reload the module-level config variable to use the fake file
    with open(pel_toolkit.CONFIG_FILE, 'r') as f:
        pel_toolkit.PEL_CONFIG = yaml.safe_load(f)


# --- Test Cases ---

class TestFindProjectRoot:
    def test_find_project_root_success(self, fs):
        # Arrange
        project_root = pel_toolkit.ROOT_DIR / "projects/my_proj"
        instance_path = project_root / "instances/test.md"
        fs.create_file(project_root / pel_toolkit.META_FILENAME)
        fs.create_file(instance_path)

        # Act
        found_root = pel_toolkit.find_project_root(instance_path)

        # Assert
        assert found_root == project_root

    def test_find_project_root_not_found(self, fs):
        # Arrange
        instance_path = pel_toolkit.ROOT_DIR / "projects/my_proj/instances/test.md"
        fs.create_file(instance_path) # No .domain_meta file

        # Act
        found_root = pel_toolkit.find_project_root(instance_path)

        # Assert
        assert found_root is None

    def test_find_project_root_at_top_level(self, fs):
        # Arrange
        project_root = pel_toolkit.ROOT_DIR
        instance_path = project_root / "test.md"
        fs.create_file(project_root / pel_toolkit.META_FILENAME)
        fs.create_file(instance_path)

        # Act
        found_root = pel_toolkit.find_project_root(instance_path)

        # Assert
        assert found_root == project_root


class TestGetTemplatePath:
    def test_get_template_path_success(self, fs):
        # Arrange
        project_root = pel_toolkit.ROOT_DIR / "projects/my_proj"
        meta_content = yaml.dump({'template': 'base_template'})
        fs.create_file(project_root / pel_toolkit.META_FILENAME, contents=meta_content)
        fs.create_dir(pel_toolkit.ROOT_DIR / "templates/base_template")

        # Act
        template_path = pel_toolkit.get_template_path(project_root)

        # Assert
        expected_path = pel_toolkit.ROOT_DIR / "templates/base_template"
        assert template_path == expected_path

    def test_get_template_path_no_template_key(self, fs):
        # Arrange
        project_root = pel_toolkit.ROOT_DIR / "projects/my_proj"
        fs.create_file(project_root / pel_toolkit.META_FILENAME, contents="some: data")

        # Act
        template_path = pel_toolkit.get_template_path(project_root)

        # Assert
        assert template_path is None

    def test_get_template_path_meta_file_not_found(self, fs):
        # Arrange
        project_root = pel_toolkit.ROOT_DIR / "projects/my_proj"
        fs.create_dir(project_root) # No meta file

        # Act
        template_path = pel_toolkit.get_template_path(project_root)

        # Assert
        assert template_path is None


class TestFindPersonaFile:
    @pytest.fixture
    def file_structure(self, fs):
        """Creates a standard project/template/global structure for persona resolution tests."""
        # Project
        project_root = pel_toolkit.ROOT_DIR / "projects/proj_a"
        project_personas = project_root / "personas"
        fs.create_dir(project_personas)

        # Template
        template_path = pel_toolkit.ROOT_DIR / "templates/template_a"
        template_personas = template_path / "personas"
        fs.create_dir(template_personas)

        # Global (already created in setup_pel_toolkit_config)
        global_personas = pel_toolkit.GLOBAL_PERSONAS_PATH

        return project_root, template_path, project_personas, template_personas, global_personas

    def test_find_in_project_scope(self, fs, file_structure):
        project_root, template_path, project_personas, _, _ = file_structure
        fs.create_file(project_personas / "coder.persona.md")

        found = pel_toolkit.find_persona_file("coder", project_root, template_path)
        assert found == project_personas / "coder.persona.md"

    def test_find_in_template_scope(self, fs, file_structure):
        project_root, template_path, _, template_personas, _ = file_structure
        fs.create_file(template_personas / "coder.persona.md")

        found = pel_toolkit.find_persona_file("coder", project_root, template_path)
        assert found == template_personas / "coder.persona.md"

    def test_find_in_global_scope(self, fs, file_structure):
        project_root, template_path, _, _, global_personas = file_structure
        fs.create_file(global_personas / "coder.persona.md")

        found = pel_toolkit.find_persona_file("coder", project_root, template_path)
        assert found == global_personas / "coder.persona.md"

    def test_precedence_project_over_all(self, fs, file_structure):
        project_root, template_path, project_personas, template_personas, global_personas = file_structure
        fs.create_file(project_personas / "coder.persona.md")
        fs.create_file(template_personas / "coder.persona.md")
        fs.create_file(global_personas / "coder.persona.md")

        found = pel_toolkit.find_persona_file("coder", project_root, template_path)
        assert found == project_personas / "coder.persona.md"

    def test_precedence_template_over_global(self, fs, file_structure):
        project_root, template_path, _, template_personas, global_personas = file_structure
        fs.create_file(template_personas / "coder.persona.md")
        fs.create_file(global_personas / "coder.persona.md")

        found = pel_toolkit.find_persona_file("coder", project_root, template_path)
        assert found == template_personas / "coder.persona.md"

    def test_find_mixin_file(self, fs, file_structure):
        project_root, template_path, project_personas, _, _ = file_structure
        fs.create_file(project_personas / "quality.mixin.md")

        found = pel_toolkit.find_persona_file("quality", project_root, template_path)
        assert found == project_personas / "quality.mixin.md"

    def test_persona_not_found(self, file_structure):
        project_root, template_path, _, _, _ = file_structure
        found = pel_toolkit.find_persona_file("nonexistent", project_root, template_path)
        assert found is None

    def test_ambiguity_error(self, fs, file_structure):
        project_root, template_path, project_personas, _, _ = file_structure
        fs.create_file(project_personas / "ambiguous.persona.md")
        fs.create_file(project_personas / "ambiguous.mixin.md")

        with pytest.raises(FileExistsError, match="Ambiguity Error: Found multiple personas"):
            pel_toolkit.find_persona_file("ambiguous", project_root, template_path)


class TestAssemblePersonaContent:
    @pytest.fixture
    def file_structure(self, fs):
        project_root = pel_toolkit.ROOT_DIR / "projects/proj_a"
        template_path = pel_toolkit.ROOT_DIR / "templates/template_a"
        fs.create_dir(project_root / "personas")
        fs.create_dir(template_path / "personas")
        return project_root, template_path

    def test_assemble_simple_persona(self, fs, file_structure):
        project_root, template_path = file_structure
        persona_path = project_root / "personas" / "simple.persona.md"
        fs.create_file(persona_path, contents="---\nkey: val\n---\nSimple content")

        content = pel_toolkit.assemble_persona_content(persona_path, project_root, template_path)
        assert content == "Simple content"

    def test_assemble_with_inheritance(self, fs, file_structure, mocker):
        project_root, template_path = file_structure
        # Child
        child_path = project_root / "personas" / "child.persona.md"
        child_content = "---\ninherits_from: parent\n---\nChild body."
        fs.create_file(child_path, contents=child_content)
        # Parent
        parent_path = template_path / "personas" / "parent.persona.md"
        parent_content = "---\n---\nParent body."
        fs.create_file(parent_path, contents=parent_content)

        mocker.patch(
            'scripts.pel_toolkit.find_persona_file',
            side_effect=[parent_path] # First call finds parent
        )

        content = pel_toolkit.assemble_persona_content(child_path, project_root, template_path)
        assert content == "Parent body.\nChild body."
        pel_toolkit.find_persona_file.assert_called_once_with("parent", project_root, template_path)

    def test_assemble_inheritance_not_found(self, fs, file_structure, mocker):
        project_root, template_path = file_structure
        child_path = project_root / "personas" / "child.persona.md"
        child_content = "---\ninherits_from: ghost\n---\nChild body."
        fs.create_file(child_path, contents=child_content)

        mocker.patch('scripts.pel_toolkit.find_persona_file', return_value=None)

        with pytest.raises(FileNotFoundError, match="Inherited persona 'ghost' not found"):
            pel_toolkit.assemble_persona_content(child_path, project_root, template_path)


class TestInjectFileContent:
    def test_inject_file_success(self, fs):
        # Arrange
        injected_file = pel_toolkit.ROOT_DIR / "src/code.py"
        fs.create_file(injected_file, contents="def hello(): pass")
        mandate_body = 'Here is the code:\n<Inject src="src/code.py" />'

        # Act
        result = pel_toolkit.inject_file_content(mandate_body)

        # Assert
        assert result == "Here is the code:\ndef hello(): pass"

    def test_inject_file_not_found(self, fs):
        # Arrange
        mandate_body = '<Inject src="nonexistent.txt" />'

        # Act
        result = pel_toolkit.inject_file_content(mandate_body)

        # Assert
        assert "[ERROR: Injected file not found at 'nonexistent.txt']" in result


class TestIsManifestStale:
    @pytest.fixture
    def setup_stale_check(self, fs, mocker):
        """Common setup for manifest staleness checks."""
        root_dir = pel_toolkit.ROOT_DIR
        manifest_path = root_dir / "persona_manifest.yml"
        persona_path = root_dir / "projects/prompt_engineering/personas/p1.persona.md"

        fs.create_file(persona_path)
        mocker.patch('validate_personas.find_all_personas', return_value=[persona_path])

        # Set a fixed "now" for reproducible time comparisons
        now = datetime(2023, 10, 27, 12, 0, 0, tzinfo=timezone.utc)
        return manifest_path, persona_path, now

    def test_manifest_does_not_exist(self, fs, setup_stale_check):
        manifest_path, _, _ = setup_stale_check
        is_stale, reason = pel_toolkit.is_manifest_stale(manifest_path, pel_toolkit.ROOT_DIR)
        assert is_stale
        assert reason == "Manifest file does not exist."

    def test_manifest_is_up_to_date(self, fs, setup_stale_check):
        manifest_path, persona_path, now = setup_stale_check

        # Manifest generated AFTER persona was last modified
        manifest_time = now
        persona_mod_time = (now - timedelta(minutes=10)).timestamp()
        fs.set_stat(persona_path, st_mtime=persona_mod_time)

        manifest_content = yaml.dump({"generated_at_utc": manifest_time.isoformat()})
        fs.create_file(manifest_path, contents=manifest_content)

        is_stale, reason = pel_toolkit.is_manifest_stale(manifest_path, pel_toolkit.ROOT_DIR)
        assert not is_stale
        assert reason == "Manifest is up-to-date."

    def test_manifest_is_stale(self, fs, setup_stale_check):
        manifest_path, persona_path, now = setup_stale_check

        # Manifest generated BEFORE persona was last modified
        manifest_time = now - timedelta(minutes=10)
        persona_mod_time = now.timestamp()
        fs.set_stat(persona_path, st_mtime=persona_mod_time)

        manifest_content = yaml.dump({"generated_at_utc": manifest_time.isoformat()})
        fs.create_file(manifest_path, contents=manifest_content)

        is_stale, reason = pel_toolkit.is_manifest_stale(manifest_path, pel_toolkit.ROOT_DIR)
        assert is_stale
        assert "was modified after the manifest was generated" in reason

    def test_manifest_grace_period(self, fs, setup_stale_check):
        manifest_path, persona_path, now = setup_stale_check

        # Persona modified 1 second after manifest -> OK due to grace period
        manifest_time = now
        persona_mod_time = (now + timedelta(seconds=1)).timestamp()
        fs.set_stat(persona_path, st_mtime=persona_mod_time)

        manifest_content = yaml.dump({"generated_at_utc": manifest_time.isoformat()})
        fs.create_file(manifest_path, contents=manifest_content)

        is_stale, _ = pel_toolkit.is_manifest_stale(manifest_path, pel_toolkit.ROOT_DIR)
        assert not is_stale

    def test_manifest_missing_timestamp(self, fs, setup_stale_check):
        manifest_path, _, _ = setup_stale_check
        fs.create_file(manifest_path, contents="some: data") # No timestamp

        is_stale, reason = pel_toolkit.is_manifest_stale(manifest_path, pel_toolkit.ROOT_DIR)
        assert is_stale
        assert "missing the 'generated_at_utc' timestamp" in reason


class TestMainFunction:
    @pytest.fixture
    def mock_sys(self, mocker):
        """Mock sys.exit, sys.stdout, and sys.stderr."""
        mock_exit = mocker.patch('sys.exit')
        mock_stdout = mocker.patch('sys.stdout', new_callable=io.StringIO)
        mock_stderr = mocker.patch('sys.stderr', new_callable=io.StringIO)
        return mock_exit, mock_stdout, mock_stderr

    @pytest.fixture
    def full_structure(self, fs):
        """Set up a complete, valid file structure for main() tests."""
        # Project
        project_root = pel_toolkit.ROOT_DIR / "projects/proj_a"
        fs.create_file(
            project_root / pel_toolkit.META_FILENAME,
            contents=yaml.dump({'template': 'template_a'})
        )
        fs.create_file(
            project_root / "personas/coder.persona.md",
            contents="---\n---\nProject Coder Persona"
        )
        # Instance file
        instance_path = project_root / "instances/my_task.md"
        instance_content = """---
persona_alias: coder
---
This is the mandate body.
"""
        fs.create_file(instance_path, contents=instance_content)
        return instance_path

    def test_main_success_flow(self, fs, full_structure, mock_sys):
        # Arrange
        instance_path = full_structure
        _, mock_stdout, _ = mock_sys

        # Act
        pel_toolkit.main(str(instance_path))

        # Assert
        output = mock_stdout.getvalue()
        assert "<SystemPrompt>" in output
        assert "<PersonaLibrary>" in output
        assert "Project Coder Persona" in output
        assert "<Instance>" in output
        assert "This is the mandate body." in output

    def test_main_stale_manifest_error(self, fs, full_structure, mock_sys):
        # Arrange
        instance_path = full_structure
        mock_exit, _, mock_stderr = mock_sys

        # Change alias to trigger the check
        instance_content = """---
persona_alias: SI-1
---
Mandate body.
"""
        fs.create_file(instance_path, contents=instance_content, overwrite=True)

        # Make manifest stale
        manifest_path = pel_toolkit.ROOT_DIR / "persona_manifest.yml"
        persona_path = pel_toolkit.GLOBAL_PERSONAS_PATH / "p1.persona.md"
        fs.create_file(persona_path)
        # This will always be considered stale since manifest does not exist
        pel_toolkit.is_manifest_stale(manifest_path, pel_toolkit.ROOT_DIR)

        # Act
        pel_toolkit.main(str(instance_path))

        # Assert
        mock_exit.assert_called_once_with(1)
        error_output = mock_stderr.getvalue()
        assert "FATAL ERROR: The persona_manifest.yml is stale." in error_output
        assert "Reason: Manifest file does not exist." in error_output

    def test_main_persona_not_found_error(self, fs, full_structure, mock_sys):
        # Arrange
        instance_path = full_structure
        mock_exit, _, mock_stderr = mock_sys

        # Change alias to one that does not exist
        instance_content = """---
persona_alias: nonexistent
---
Mandate body.
"""
        fs.create_file(instance_path, contents=instance_content, overwrite=True)

        # Act
        pel_toolkit.main(str(instance_path))

        # Assert
        mock_exit.assert_called_once_with(1)
        assert "Error: Persona 'nonexistent' not found" in mock_stderr.getvalue()