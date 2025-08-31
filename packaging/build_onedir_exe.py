#!/usr/bin/env python3
"""
Build executable using --onedir to avoid unpacking overhead
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build_artifacts():
    """Clean up build artifacts"""
    print("Cleaning build artifacts...")
    
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"Cleaned {dir_name}")
            except PermissionError:
                print(f"Could not clean {dir_name} (permission denied)")

def find_tiktoken_models():
    """Find tiktoken model files to include in the build"""
    print("Finding tiktoken model files...")
    
    try:
        import tiktoken
        import tiktoken.core
        
        # Get the tiktoken module path
        tiktoken_path = os.path.dirname(tiktoken.__file__)
        print(f"tiktoken path: {tiktoken_path}")
        
        # Look for model files
        model_files = []
        for root, dirs, files in os.walk(tiktoken_path):
            for file in files:
                if file.endswith('.tiktoken') or file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    model_files.append(file_path)
                    print(f"  Found model file: {file_path}")
        
        return model_files
    except Exception as e:
        print(f"Error finding tiktoken models: {e}")
        return []

def build_onedir_exe():
    """Build the executable using --onedir"""
    print("Building onedir executable...")
    
    # Find tiktoken model files
    tiktoken_models = find_tiktoken_models()
    
    # Use PyInstaller with --onedir instead of --onefile
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",  # Create directory instead of single file
        "--console",  # Keep console for debugging
        "--clean",
        "--noconfirm",
        "--add-data=src;src",  # Include entire src directory
        "--add-data=assets;assets",  # Include assets
        "--add-data=README.md;.",  # Include README
        "--add-data=LICENSE;.",  # Include LICENSE
        # "--additional-hooks-dir=.",  # No custom hooks needed
        # "--exclude-module=secrets",  # Don't exclude Python secrets module
        "--hidden-import=reader",
        "--hidden-import=src",
        "--hidden-import=src.services",
        "--hidden-import=src.services.vector_store",
        "--hidden-import=src.services.document_processor",
        "--hidden-import=src.services.llm_service",
        "--hidden-import=src.ui",
        "--hidden-import=src.ui.main_window",
        "--hidden-import=src.ui.dialogs",
        "--hidden-import=src.ui.widgets",
        "--hidden-import=src.utils",
        "--hidden-import=src.utils.text_processing",
        "--hidden-import=src.utils.file_utils",
        "--hidden-import=src.config",
        "--hidden-import=src.config.settings",
        "--hidden-import=PySide6",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtPrintSupport",
        "--hidden-import=PySide6.QtWebEngineWidgets",
        "--hidden-import=chromadb",
        "--hidden-import=chromadb.telemetry",
        "--hidden-import=chromadb.telemetry.product",
        "--hidden-import=chromadb.telemetry.product.posthog",
        "--hidden-import=chromadb.telemetry.opentelemetry",
        "--hidden-import=chromadb.telemetry.opentelemetry.grpc",
        "--hidden-import=chromadb.telemetry.opentelemetry.fastapi",
        "--hidden-import=chromadb.api",
        "--hidden-import=chromadb.api.admin",
        "--hidden-import=chromadb.api.server",
        "--hidden-import=chromadb.sqlite3",
        "--hidden-import=chromadb.errors",
        "--hidden-import=chromadb.types",
        "--hidden-import=chromadb.base_types",
        "--hidden-import=chromadb.serde",
        "--hidden-import=chromadb.auth",
        "--hidden-import=chromadb.auth.simple_rbac_authz",
        "--hidden-import=chromadb.auth.basic_authn",
        "--hidden-import=chromadb.auth.token_authn",
        "--hidden-import=chromadb.utils",
        "--hidden-import=chromadb.utils.embedding_functions",
        "--hidden-import=chromadb.config",
        "--hidden-import=chromadb.config.Settings",
        "--hidden-import=chromadb.segment",
        "--hidden-import=chromadb.segment.impl",
        "--hidden-import=chromadb.segment.impl.vector",
        "--hidden-import=chromadb.segment.impl.vector.local_hnsw",
        "--hidden-import=chromadb.segment.impl.vector.local_persistent_hnsw",
        "--hidden-import=chromadb.segment.impl.manager",
        "--hidden-import=chromadb.segment.impl.manager.local",
        "--hidden-import=chromadb.proto",
        "--hidden-import=chromadb.proto.chroma_pb2",
        "--hidden-import=chromadb.proto.query_executor_pb2",
        "--hidden-import=chromadb.proto.convert",
        "--hidden-import=chromadb.proto.utils",
        "--hidden-import=sentence_transformers",
        "--hidden-import=transformers",
        "--hidden-import=transformers.models",
        "--hidden-import=transformers.tokenization_utils",
        "--hidden-import=transformers.tokenization_utils_base",
        "--hidden-import=transformers.modeling_utils",
        "--hidden-import=transformers.configuration_utils",
        "--hidden-import=transformers.utils",
        "--hidden-import=transformers.utils.import_utils",
        "--hidden-import=torch",
        "--hidden-import=torch.nn",
        "--hidden-import=torch.nn.functional",
        "--hidden-import=torch.utils.data",
        "--hidden-import=tiktoken",
        "--hidden-import=tiktoken.core",
        "--hidden-import=tiktoken.registry",
        "--hidden-import=tiktoken.model",
        "--hidden-import=pdfplumber",
        "--hidden-import=markdown",
        "--hidden-import=mdx_math",
        "--hidden-import=python_markdown_math",
        "--hidden-import=pypandoc",
        # ChromaDB Rust support
        "--hidden-import=chromadb.api.rust",
        "--name=LLM-Textbook-Highlighter",
        "--icon=assets/llm_icon.ico",
        "run_reader.py"
    ]
    
    # Add tiktoken model files
    tiktoken_models_dir = Path("tiktoken_models")
    if tiktoken_models_dir.exists():
        for model_file in tiktoken_models_dir.glob("*.tiktoken"):
            cmd.append(f"--add-data={model_file};tiktoken")
            print(f"  Added tiktoken model: {model_file.name}")
    
    # Add tiktoken model files if found (legacy)
    if tiktoken_models:
        for model_file in tiktoken_models:
            # Get relative path from tiktoken module
            import tiktoken
            tiktoken_path = os.path.dirname(tiktoken.__file__)
            rel_path = os.path.relpath(model_file, tiktoken_path)
            cmd.append(f"--add-data={model_file};tiktoken/{rel_path}")
            print(f"  Added tiktoken model: {rel_path}")
    
    # Add explicit exclusions for sensitive files
    cmd.extend([
        "--exclude-module=keyring",  # Exclude keyring module
    ])
    
    try:
        # Use binary mode to avoid Unicode decoding issues
        result = subprocess.run(cmd, check=True, capture_output=True, text=False)
        print("Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with exit code {e.returncode}")
        if e.stderr:
            try:
                stderr_text = e.stderr.decode('utf-8', errors='replace')
                print(f"Error output: {stderr_text}")
            except:
                print(f"Error output: {e.stderr}")
        return False

def check_executable():
    """Check the built executable"""
    exe_path = Path("dist/LLM-Textbook-Highlighter/LLM-Textbook-Highlighter.exe")
    
    if not exe_path.exists():
        print("Executable not found!")
        return False
    
    # Get directory size
    dir_size = sum(f.stat().st_size for f in exe_path.parent.rglob('*') if f.is_file())
    dir_size_mb = dir_size / (1024 * 1024)
    
    print(f"Executable created: {exe_path}")
    print(f"Directory size: {dir_size_mb:.1f} MB")
    print(f"Location: {exe_path.parent}")
    
    return True

def main():
    """Main build process"""
    print("Building LLM Textbook Highlighter (Onedir)")
    print("=" * 60)
    
    # Clean previous builds
    clean_build_artifacts()
    
    # Build executable
    if build_onedir_exe():
        print("\n" + "=" * 60)
        print("Build Summary")
        print("=" * 60)
        
        if check_executable():
            print("\nFeatures:")
            print("  - All source files included")
            print("  - All necessary modules included")
            print("  - Console enabled for debugging")
            print("  - Vector store uses user AppData directory")
            print("  - ChromaDB telemetry and Rust support included")
            print("  - tiktoken support for text tokenization")
            print("  - tiktoken model files included")
            print("  - NO unpacking overhead (--onedir)")
            print()
            print("To run:")
            print("  - dist/LLM-Textbook-Highlighter/LLM-Textbook-Highlighter.exe")
            print()
            print("Important:")
            print("  - API key will be configured through the application settings")
            print("  - secrets.json will be created automatically in the project root directory")
            print("  - This creates a directory instead of a single file")
            print("  - Much faster startup due to no unpacking!")
        else:
            print("Executable check failed!")
    else:
        print("Build failed!")

if __name__ == "__main__":
    main()
