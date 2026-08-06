"""
StudyOS Educational Asset Engine (EAE) — Asset Compiler Package
"""

from app.services.asset_compiler.packager import BundlePackager, CompiledBundle
from app.services.asset_compiler.pipeline import (
    AssetCompilerPipeline,
    CompilationPipelineResult,
)
from app.services.asset_compiler.sanitizer import SVGSanitizer
from app.services.asset_compiler.spatial import SpatialIndexBuilder

__all__ = [
    "AssetCompilerPipeline",
    "BundlePackager",
    "CompilationPipelineResult",
    "SVGSanitizer",
    "SpatialIndexBuilder",
    "CompiledBundle",
]
