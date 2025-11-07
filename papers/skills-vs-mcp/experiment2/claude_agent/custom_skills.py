from pathlib import Path
from typing import List, Dict, Any
from anthropic import Anthropic
from anthropic.lib import files_from_dir


def create_skill(
    client: Anthropic, 
    skill_path: str, 
    display_title: str
) -> Dict[str, Any]:
    """
    Create a new custom skill from a directory.

    The directory must contain:
    - SKILL.md file with YAML frontmatter (name, description)
    - Optional: scripts, resources, etc.

    Args:
        client: Anthropic client instance with Skills beta
        skill_path: Path to skill directory containing SKILL.md
        display_title: Human-readable name for the skill

    Returns:
        Dictionary with skill creation results:
        {
            'success': bool,
            'skill_id': str (if successful),
            'display_title': str,
            'latest_version': str,
            'created_at': str,
            'source': str ('custom'),
            'error': str (if failed)
        }
    """
    try:
        # Validate skill directory
        skill_dir = Path(skill_path)
        if not skill_dir.exists():
            return {"success": False, "error": f"Skill directory does not exist: {skill_path}"}

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return {"success": False, "error": f"SKILL.md not found in {skill_path}"}

        # Create skill using files_from_dir
        skill = client.beta.skills.create(
            display_title=display_title, files=files_from_dir(skill_path)
        )

        return {
            "success": True,
            "skill_id": skill.id,
            "display_title": skill.display_title,
            "latest_version": skill.latest_version,
            "created_at": skill.created_at,
            "source": skill.source,
        }

    except Exception as e:
        print(f"Error creating skill: {e}")
        return {"success": False, "error": str(e)}


def list_skills(
    client: Anthropic
) -> List[Dict[str, Any]]:
    """
    List all custom skills in the workspace.

    Args:
        client: Anthropic client instance with Skills beta

    Returns:
        List of skill dictionaries with metadata
    """
    try:
        skills_response = client.beta.skills.list(source="custom")

        skills = []
        for skill in skills_response.data:
            skills.append(
                {
                    "skill_id": skill.id,
                    "display_title": skill.display_title,
                    "latest_version": skill.latest_version,
                    "created_at": skill.created_at,
                    "updated_at": skill.updated_at,
                }
            )

        return skills

    except Exception as e:
        print(f"Error listing skills: {e}")
        return []


def delete_skill(
    client: Anthropic, 
    skill_id: str, 
    delete_versions: bool = True
) -> bool:
    """
    Delete a custom skill and optionally all its versions.

    Note: All versions must be deleted before the skill can be deleted.

    Args:
        client: Anthropic client instance
        skill_id: ID of skill to delete
        delete_versions: Whether to delete all versions first

    Returns:
        True if successful, False otherwise
    """
    try:
        if delete_versions:
            # First delete all versions
            versions = client.beta.skills.versions.list(skill_id=skill_id)

            for version in versions.data:
                client.beta.skills.versions.delete(skill_id=skill_id, version=version.version)
                print(f"    Deleted version: {version.version}")

        # Then delete the skill itself
        client.beta.skills.delete(skill_id)
        print(f"    Deleted skill ID: {skill_id}")
        return True

    except Exception as e:
        print(f"Error deleting skill: {e}")
        return False


def set_custom_skills(
    client: Anthropic,
    custom_skill_folders: List,
    force_update: bool =True
) -> List[Dict[str, Any]]: 

    try:
        custom_skills = []
        remaining_skills = set(custom_skill_folders)
        
        existing_custom_skills = list_skills(client)

        for item in existing_custom_skills:
            skill_name = item["display_title"]
            
            if skill_name in remaining_skills:
                if force_update:
                    print(f"Delete existing version of '{skill_name.split('/')[-1]}' skill for update...")
                    delete_skill(client, item["skill_id"])
                else:
                    custom_skills.append({
                        "type": "custom",
                        "skill_id": item["skill_id"],
                        "version": "latest"
                    })
                    remaining_skills.discard(skill_name)
                    print(f"Use existing version of '{skill_name}' skill")

        for skill_name in remaining_skills:
            
            print(f"Upload '{skill_name.split('/')[-1]}' skill...")     
            skill_path = Path(f"{skill_name}")
            result = create_skill(client, str(skill_path), skill_name)
            
            if result["success"]:
                custom_skills.append({
                    "type": "custom",
                    "skill_id": result["skill_id"],
                    "version": "latest"
                })
                print(f"   Uploaded version: {result['latest_version']}")
                print(f"   Uploaded skill ID: {result['skill_id']}")

            else:
                print(f"Upload failed: {result['error']}")

        return custom_skills

    except Exception as e:
        print(f"Error setting custom skills: {e}")
        return []
