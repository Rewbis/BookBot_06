import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.core.state import ProjectRegistry

class ProjectManager:
    """Handles persistence, snapshots, and project listing for BookBot_06."""

    def __init__(self, projects_dir: str = "projects"):
        self.projects_dir = Path(projects_dir)
        self.projects_dir.mkdir(exist_ok=True)

    def list_projects(self) -> List[Dict[str, Any]]:
        """Returns a list of available projects with basic metadata."""
        projects = []
        for project_file in self.projects_dir.glob("*.json"):
            try:
                with open(project_file, 'r') as f:
                    data = json.load(f)
                    projects.append({
                        "id": data.get("project_id"),
                        "title": data.get("title", "Untitled"),
                        "last_updated": data.get("last_updated"),
                        "file_path": str(project_file),
                        "file_size_kb": round(project_file.stat().st_size / 1024, 2)
                    })
            except Exception as e:
                print(f"Error reading {project_file}: {e}")
        
        # Sort by last updated (newest first)
        return sorted(projects, key=lambda x: x.get("last_updated", ""), reverse=True)

    def load_project(self, project_id: str) -> Optional[ProjectRegistry]:
        """Loads a project registry from a JSON file."""
        file_path = self.projects_dir / f"project_{project_id}.json"
        if not file_path.exists():
            # Try searching by ID if the filename doesn't match exactly
            for p in self.projects_dir.glob("*.json"):
                if project_id in p.name:
                    file_path = p
                    break
        
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
                return ProjectRegistry.model_validate(data)
        return None

    def save_project(self, registry: ProjectRegistry) -> str:
        """Saves the current registry state to a JSON file."""
        registry.last_updated = datetime.now()
        file_name = f"project_{registry.project_id}.json"
        file_path = self.projects_dir / file_name
        
        with open(file_path, 'w') as f:
            json.dump(registry.model_dump(mode='json'), f, indent=4)
        
        return str(file_path)

    def create_new_project(self, title: str = "Untitled Project") -> ProjectRegistry:
        """Initializes a new project registry."""
        registry = ProjectRegistry(title=title)
        self.save_project(registry)
        return registry

    def delete_project(self, project_id: str) -> bool:
        """Deletes a project file."""
        file_path = self.projects_dir / f"project_{project_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False
