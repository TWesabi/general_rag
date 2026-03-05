# """
# GPU Prerequisite Tests for Docling PDF Parser
# ==============================================

# PURPOSE
# -------
# Run these tests BEFORE you start using GPU acceleration in your docling code.
# They tell you exactly what is missing and what you need to fix.

# HOW TO RUN
# ----------
# Run all GPU prerequisite tests:
#     uv run pytest tests/test_gpu_prerequisites.py -v

# Run only the hardware checks:
#     uv run pytest tests/test_gpu_prerequisites.py::TestGPUHardware -v

# Run only the PyTorch/CUDA checks:
#     uv run pytest tests/test_gpu_prerequisites.py::TestTorchCUDA -v

# Run only the Docling config checks:
#     uv run pytest tests/test_gpu_prerequisites.py::TestDoclingGPUConfig -v

# WHAT "ALL TESTS PASS" MEANS
# ----------------------------
#   TestGPUHardware       -> NVIDIA driver is installed and a GPU is visible to the OS.
#   TestTorchCUDA         -> PyTorch is installed with CUDA support AND can talk to the GPU.
#   TestDoclingGPUConfig  -> Docling's pipeline options accept CUDA config without errors.

# If ALL three groups pass you are ready to use GPU acceleration in your docling code.

# WHAT TO FIX WHEN TESTS FAIL
# ----------------------------

# 1. TestGPUHardware fails:
#    -> nvidia-smi is not found or returns no GPU.
#    Fix: Install the NVIDIA driver from https://www.nvidia.com/drivers
#         and make sure it is on your PATH.

# 2. TestTorchCUDA::test_torch_is_installed fails:
#    -> torch is not installed at all.
#    Fix: uv run pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 3. TestTorchCUDA::test_torch_has_cuda_build fails:
#    -> torch is installed but it is the CPU-only wheel (e.g. 2.x.x+cpu).
#    Fix: Uninstall the CPU build and reinstall the CUDA one:
#         uv run pip uninstall torch torchvision -y
#         uv run pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
#    Note: use cu118 instead of cu121 if your CUDA toolkit is 11.8.
#          Check your driver's max supported CUDA version with: nvidia-smi

# 4. TestTorchCUDA::test_cuda_is_available fails:
#    -> CUDA build is present but torch.cuda.is_available() returns False.
#    This usually means a driver/toolkit version mismatch.
#    Fix: Match the torch CUDA wheel to your driver.
#         nvidia-smi shows "CUDA Version: X.Y" in the top-right corner.
#         That is the MAXIMUM CUDA version your driver supports.
#         Pick a torch wheel whose cuda tag (cu121, cu118 …) is <= that version.

# 5. TestDoclingGPUConfig fails:
#    -> Docling is outdated and does not have AcceleratorDevice.CUDA yet.
#    Fix: uv add docling --upgrade

# FLASH ATTENTION 2 (OPTIONAL SPEED-UP)
# --------------------------------------
# Your RTX 2000 Ada Generation is an Ada Lovelace GPU (newer than Ampere),
# so it fully supports Flash Attention 2.

# With Flash Attention 2 docling processes transformer attention layers faster
# and uses less VRAM — especially helpful on long documents with many tables/images.

# To use it you need the flash-attn package:
#     uv run pip install flash-attn --no-build-isolation

# It requires:
#   - A CUDA-enabled PyTorch
#   - An Ampere or newer GPU (your Ada Lovelace qualifies)
#   - The package takes a few minutes to compile on first install

# HOW TO INTEGRATE GPU INTO YOUR DOCLING CODE
# --------------------------------------------
# Below is the pattern to follow wherever you want to use GPU in your own code.
# Do NOT just copy-paste it — understand each part and adapt it to your file.

# IMPORTANT: HOW DocumentConverter ACTUALLY ACCEPTS GPU OPTIONS
# ─────────────────────────────────────────────────────────────
# PipelineOptions cannot be passed directly to DocumentConverter().
# You must wrap it in PdfFormatOption and pass it via format_options:

#     from docling.document_converter import DocumentConverter, PdfFormatOption
#     from docling.datamodel.base_models import InputFormat
#     from docling.datamodel.pipeline_options import (
#         AcceleratorDevice, AcceleratorOptions, PipelineOptions,
#     )

#     pipeline_options = PipelineOptions(
#         accelerator_options=AcceleratorOptions(
#             num_threads=4,
#             device=AcceleratorDevice.CUDA,         # or CPU / AUTO
#             cuda_use_flash_attention2=False,
#         )
#     )

#     converter = DocumentConverter(
#         format_options={
#             InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
#         }
#     )
#     result = converter.convert(your_file_path)

# Pattern A — Simple toggle at the top of your script / module:
# ─────────────────────────────────────────────────────────────
#     USE_GPU = True   # flip to False to go back to CPU

#     from docling.document_converter import DocumentConverter, PdfFormatOption
#     from docling.datamodel.base_models import InputFormat
#     from docling.datamodel.pipeline_options import (
#         AcceleratorDevice, AcceleratorOptions, PipelineOptions,
#     )

#     def _is_cuda_ready() -> bool:
#         try:
#             import torch
#             return torch.version.cuda is not None and torch.cuda.is_available()
#         except ImportError:
#             return False

#     device = AcceleratorDevice.CUDA if (USE_GPU and _is_cuda_ready()) else AcceleratorDevice.CPU

#     pipeline_options = PipelineOptions(
#         accelerator_options=AcceleratorOptions(
#             num_threads=4,
#             device=device,
#             cuda_use_flash_attention2=False,   # set True only if flash-attn is installed
#         )
#     )
#     converter = DocumentConverter(
#         format_options={
#             InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
#         }
#     )
#     result = converter.convert(your_file_path)

# Pattern B — Guard block with a try/except (safer for production):
# ──────────────────────────────────────────────────────────────────
#     from docling.document_converter import DocumentConverter, PdfFormatOption
#     from docling.datamodel.base_models import InputFormat
#     from docling.datamodel.pipeline_options import (
#         AcceleratorDevice, AcceleratorOptions, PipelineOptions,
#     )

#     def build_converter(use_gpu: bool = False) -> DocumentConverter:
#         if use_gpu:
#             try:
#                 import torch
#                 if torch.version.cuda is None or not torch.cuda.is_available():
#                     raise RuntimeError("CUDA not available")
#                 device = AcceleratorDevice.CUDA
#                 print(f"Using GPU: {torch.cuda.get_device_name(0)}")
#             except (ImportError, RuntimeError) as e:
#                 print(f"GPU not available ({e}), falling back to CPU")
#                 device = AcceleratorDevice.CPU
#         else:
#             device = AcceleratorDevice.CPU

#         pipeline_options = PipelineOptions(
#             accelerator_options=AcceleratorOptions(device=device)
#         )
#         return DocumentConverter(
#             format_options={
#                 InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
#             }
#         )

#     # Usage:
#     converter = build_converter(use_gpu=True)
#     result = converter.convert(your_file_path)

# KEY DOCLING CLASSES YOU WILL USE
# ─────────────────────────────────
#   PipelineOptions       — top-level config object passed to DocumentConverter
#   AcceleratorOptions    — nested inside PipelineOptions; controls device selection
#   AcceleratorDevice     — enum: AUTO, CPU, CUDA, CUDA:N, MPS, XPU
#                           AUTO lets docling pick the best available device automatically

#   Setting device=AcceleratorDevice.AUTO is the easiest option once your environment
#   is correctly set up — docling will pick CUDA if it is available, CPU otherwise.
# """

# import subprocess

# import pytest


# # ──────────────────────────────────────────────
# # Helpers
# # ──────────────────────────────────────────────


# def _nvidia_smi_available() -> bool:
#     try:
#         result = subprocess.run(
#             ["nvidia-smi"], capture_output=True, text=True, timeout=10
#         )
#         return result.returncode == 0
#     except (FileNotFoundError, subprocess.TimeoutExpired):
#         return False


# def _torch_imported() -> bool:
#     try:
#         import torch  # noqa: F401

#         return True
#     except ImportError:
#         return False


# # ──────────────────────────────────────────────
# # Tests
# # ──────────────────────────────────────────────


# class TestGPUHardware:
#     """Step 1 — Confirm the OS can see your NVIDIA GPU."""

#     def test_nvidia_driver_present(self):
#         """nvidia-smi must be reachable — confirms the driver is installed."""
#         assert _nvidia_smi_available(), (
#             "nvidia-smi not found.\n"
#             "Fix: Install the NVIDIA driver from https://www.nvidia.com/drivers\n"
#             "     and make sure it is on your PATH."
#         )

#     def test_nvidia_smi_shows_gpu(self):
#         """nvidia-smi must report at least one GPU."""
#         result = subprocess.run(
#             ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
#             capture_output=True,
#             text=True,
#             timeout=10,
#         )
#         assert result.returncode == 0, "nvidia-smi failed"
#         gpu_names = [line.strip() for line in result.stdout.splitlines() if line.strip()]
#         assert len(gpu_names) >= 1, "No GPUs reported by nvidia-smi"
#         print(f"\n  Detected GPU(s): {gpu_names}")


# class TestTorchCUDA:
#     """Step 2 — Confirm PyTorch can use the GPU."""

#     def test_torch_is_installed(self):
#         """PyTorch must be importable."""
#         assert _torch_imported(), (
#             "torch is not installed.\n"
#             "Fix: uv run pip install torch torchvision "
#             "--index-url https://download.pytorch.org/whl/cu121"
#         )

#     def test_torch_has_cuda_build(self):
#         """PyTorch must be built with CUDA support (not a +cpu wheel)."""
#         import torch

#         assert torch.version.cuda is not None, (
#             f"PyTorch {torch.__version__} is a CPU-only build.\n"
#             "Fix: uv run pip uninstall torch torchvision -y\n"
#             "     uv run pip install torch torchvision "
#             "--index-url https://download.pytorch.org/whl/cu121"
#         )
#         print(f"\n  Torch CUDA build version: {torch.version.cuda}")

#     def test_cuda_is_available(self):
#         """torch.cuda.is_available() must return True."""
#         import torch

#         assert torch.cuda.is_available(), (
#             "CUDA build present but torch.cuda.is_available() is False.\n"
#             "Cause: driver/toolkit version mismatch.\n"
#             "Fix:   check `nvidia-smi` top-right for max supported CUDA version,\n"
#             "       then reinstall torch with a matching cu1XX tag."
#         )
#         print(f"\n  CUDA device: {torch.cuda.get_device_name(0)}")

#     def test_cuda_tensor_ops(self):
#         """A simple tensor operation on the GPU must complete without error."""
#         import torch

#         t = torch.tensor([1.0, 2.0, 3.0]).cuda()
#         result = (t * 2).sum().item()
#         assert result == 12.0, f"Unexpected GPU tensor result: {result}"
#         print(f"\n  GPU tensor op: {result} (expected 12.0)")


# class TestDoclingGPUConfig:
#     """Step 3 — Confirm Docling accepts GPU configuration."""

#     def test_docling_pipeline_options_importable(self):
#         """Docling pipeline options must import without error."""
#         from docling.datamodel.pipeline_options import (  # noqa: F401
#             AcceleratorDevice,
#             AcceleratorOptions,
#             PipelineOptions,
#         )

#     def test_docling_accelerator_cuda_device_exists(self):
#         """AcceleratorDevice.CUDA enum value must exist in this docling version."""
#         from docling.datamodel.pipeline_options import AcceleratorDevice

#         assert hasattr(AcceleratorDevice, "CUDA"), (
#             "AcceleratorDevice.CUDA not found in your docling version.\n"
#             "Fix: uv add docling --upgrade"
#         )

#     def test_docling_pipeline_options_accepts_cuda(self):
#         """PipelineOptions must accept CUDA AcceleratorOptions without error."""
#         from docling.datamodel.pipeline_options import (
#             AcceleratorDevice,
#             AcceleratorOptions,
#             PipelineOptions,
#         )

#         opts = PipelineOptions(
#             accelerator_options=AcceleratorOptions(
#                 num_threads=4,
#                 device=AcceleratorDevice.CUDA,
#                 cuda_use_flash_attention2=False,
#             )
#         )
#         assert opts.accelerator_options.device == AcceleratorDevice.CUDA

#     def test_docling_converter_builds_with_cuda_options(self):
#         """DocumentConverter must initialise with CUDA pipeline options without error.

#         PipelineOptions must be wrapped in PdfFormatOption and passed via format_options —
#         DocumentConverter does NOT accept pipeline_options as a direct argument.
#         """
#         from docling.datamodel.base_models import InputFormat
#         from docling.datamodel.pipeline_options import (
#             AcceleratorDevice,
#             AcceleratorOptions,
#             PipelineOptions,
#         )
#         from docling.document_converter import DocumentConverter, PdfFormatOption

#         pipeline_options = PipelineOptions(
#             accelerator_options=AcceleratorOptions(
#                 num_threads=4,
#                 device=AcceleratorDevice.CUDA,
#                 cuda_use_flash_attention2=False,
#             )
#         )
#         converter = DocumentConverter(
#             format_options={
#                 InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
#             }
#         )
#         assert converter is not None
#         print("\n  DocumentConverter built with CUDA options successfully.")
