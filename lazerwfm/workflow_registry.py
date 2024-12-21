from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Type

import yaml

from .workflow import Workflow


@dataclass
class WorkflowMetadata:
    """Metadata for a registered workflow"""

    name: str
    class_path: str
    description: str
    parameters: dict[str, dict[str, Any]]
    is_public: bool = True


class WorkflowRegistry:
    """Registry for workflow classes"""

    def __init__(self):
        self._workflows: dict[str, tuple[Type[Workflow], WorkflowMetadata]] = {}

    def load_from_config(self, config_path: str | Path) -> None:
        """Load workflows from a YAML configuration file"""
        print(f"\nLoading workflows from: {config_path}")

        with open(config_path) as f:
            config = yaml.safe_load(f)
            print(f"Config contents: {config}")

        workflows_dir = Path(config.get("workflows_dir", "workflows"))
        if not workflows_dir.is_absolute():
            config_dir = Path(config_path).parent
            workflows_dir = config_dir / workflows_dir

        print(f"Workflows directory: {workflows_dir}")

        for wf_config in config.get("workflows", []):
            name = wf_config["name"]
            module_path = workflows_dir / wf_config["file"]
            class_name = wf_config["class"]

            print(f"\nLoading workflow: {name}")
            print(f"Module path: {module_path}")
            print(f"Class name: {class_name}")

            # Import the workflow class
            spec = importlib.util.spec_from_file_location(
                f"workflow_{name}", str(module_path)
            )
            if not spec or not spec.loader:
                raise ImportError(f"Could not load workflow from {module_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            workflow_class = getattr(module, class_name)
            if not issubclass(workflow_class, Workflow):
                raise TypeError(f"Class {class_name} must inherit from Workflow")

            metadata = WorkflowMetadata(
                name=name,
                class_path=f"{module_path}:{class_name}",
                description=wf_config.get("description", ""),
                parameters=wf_config.get("parameters", {}),
                is_public=wf_config.get("public", True),
            )

            self._workflows[name] = (workflow_class, metadata)

    def get_workflow_class(
        self, name: str
    ) -> tuple[Type[Workflow], WorkflowMetadata] | None:
        """Get a workflow class and its metadata by name"""
        return self._workflows.get(name)

    def list_workflows(self) -> list[WorkflowMetadata]:
        """List all registered workflows"""
        return [metadata for _, metadata in self._workflows.values()]

    def list_public_workflows(self) -> list[WorkflowMetadata]:
        """List only public workflows"""
        return [
            metadata for _, metadata in self._workflows.values() if metadata.is_public
        ]
