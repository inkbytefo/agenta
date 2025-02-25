import os
import shutil
from typing import Dict, Any, List
import json
from pathlib import Path

class FileOperations:
    """File operations tool for the CrewAI agent."""
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read contents of a file"""
        try:
            full_path = os.path.join(self.workspace_path, file_path)
            if not os.path.exists(full_path):
                return {
                    'status': 'error',
                    'error': f'File not found: {file_path}'
                }
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return {
                'status': 'success',
                'content': content
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def create_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to a file"""
        try:
            full_path = os.path.join(self.workspace_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return {
                'status': 'success',
                'message': f'File written successfully: {file_path}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def list_files(self, directory: str = '.', pattern: str = '*') -> Dict[str, Any]:
        """List files in a directory matching a pattern"""
        try:
            full_path = os.path.join(self.workspace_path, directory)
            if not os.path.exists(full_path):
                return {
                    'status': 'error',
                    'error': f'Directory not found: {directory}'
                }
            
            files = []
            dirs = []
            path = Path(full_path)
            
            for item in path.rglob(pattern):
                rel_path = os.path.relpath(item, self.workspace_path)
                if item.is_file():
                    files.append(rel_path)
                elif item.is_dir():
                    dirs.append(rel_path)
                    
            return {
                'status': 'success',
                'files': files,
                'directories': dirs
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file"""
        try:
            full_path = os.path.join(self.workspace_path, file_path)
            if not os.path.exists(full_path):
                return {
                    'status': 'error',
                    'error': f'File not found: {file_path}'
                }
            
            if os.path.isfile(full_path):
                os.remove(full_path)
            else:
                shutil.rmtree(full_path)
                
            return {
                'status': 'success',
                'message': f'Successfully deleted: {file_path}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def rename_file(self, old_path: str, new_path: str) -> Dict[str, Any]:
        """Rename or move a file"""
        try:
            old_full_path = os.path.join(self.workspace_path, old_path)
            new_full_path = os.path.join(self.workspace_path, new_path)
            
            if not os.path.exists(old_full_path):
                return {
                    'status': 'error',
                    'error': f'Source not found: {old_path}'
                }
            
            if os.path.exists(new_full_path):
                return {
                    'status': 'error',
                    'error': f'Destination already exists: {new_path}'
                }
            
            os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
            shutil.move(old_full_path, new_full_path)
            
            return {
                'status': 'success',
                'message': f'Successfully moved/renamed {old_path} to {new_path}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def copy_file(self, source_path: str, dest_path: str) -> Dict[str, Any]:
        """Copy a file or directory"""
        try:
            source_full_path = os.path.join(self.workspace_path, source_path)
            dest_full_path = os.path.join(self.workspace_path, dest_path)
            
            if not os.path.exists(source_full_path):
                return {
                    'status': 'error',
                    'error': f'Source not found: {source_path}'
                }
            
            if os.path.exists(dest_full_path):
                return {
                    'status': 'error',
                    'error': f'Destination already exists: {dest_path}'
                }
            
            os.makedirs(os.path.dirname(dest_full_path), exist_ok=True)
            
            if os.path.isfile(source_full_path):
                shutil.copy2(source_full_path, dest_full_path)
            else:
                shutil.copytree(source_full_path, dest_full_path)
            
            return {
                'status': 'success',
                'message': f'Successfully copied {source_path} to {dest_path}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a file"""
        try:
            full_path = os.path.join(self.workspace_path, file_path)
            if not os.path.exists(full_path):
                return {
                    'status': 'error',
                    'error': f'File not found: {file_path}'
                }
            
            stat = os.stat(full_path)
            
            return {
                'status': 'success',
                'info': {
                    'size': stat.st_size,
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime,
                    'is_file': os.path.isfile(full_path),
                    'is_directory': os.path.isdir(full_path),
                    'extension': os.path.splitext(full_path)[1] if os.path.isfile(full_path) else None
                }
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def create_directory(self, directory_path: str) -> Dict[str, Any]:
        """Create a new directory"""
        try:
            full_path = os.path.join(self.workspace_path, directory_path)
            
            if os.path.exists(full_path):
                return {
                    'status': 'error',
                    'error': f'Directory already exists: {directory_path}'
                }
            
            os.makedirs(full_path)
            
            return {
                'status': 'success',
                'message': f'Successfully created directory: {directory_path}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
