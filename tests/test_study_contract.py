"""Contrato de material estudiable: tipos públicos, etapas y fuentes limpias."""

import inspect
import re
from pathlib import Path

import nbformat
from IPython.core.inputtransformer2 import TransformerManager

from neurofisiologia import analysis, examples, model, parameters, plotting, stimulus


def test_public_functions_have_types_and_explanations():
    for module in (analysis, examples, model, parameters, plotting, stimulus):
        for name, function in inspect.getmembers(module, inspect.isfunction):
            if name.startswith('_') or function.__module__ != module.__name__:
                continue
            signature = inspect.signature(function)
            assert signature.return_annotation != inspect.Signature.empty, name
            assert all(p.annotation != inspect.Parameter.empty for p in signature.parameters.values()), name
            assert function.__doc__, name


def test_notebooks_have_all_stages_clean_cells_and_valid_python():
    root = Path(__file__).resolve().parents[1]
    transformer = TransformerManager()
    for name in ('01_baston_tres_compartimentos', '02_estudio_guiado_baston'):
        notebook = nbformat.read(root/f'notebooks/{name}.ipynb', as_version=4)
        nbformat.validate(notebook)
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                assert cell.outputs == []
                assert cell.execution_count is None
                compile(transformer.transform_cell(cell.source), name, 'exec')
        if name.startswith('02'):
            narrative = '\n'.join(c.source for c in notebook.cells if c.cell_type == 'markdown')
            stages = re.findall(r'^## (\d\d) ·', narrative, flags=re.MULTILINE)
            assert stages == [f'{n:02d}' for n in range(16)]
            assert '<details>' in narrative and '</details>' in narrative


def test_study_markdown_local_links_resolve():
    root = Path(__file__).resolve().parents[1]
    files = [root/'README.md', *root.glob('docs/*.md')]
    for file in files:
        for link in re.findall(r'\]\(([^)]+)\)', file.read_text()):
            if '://' not in link and not link.startswith('#'):
                assert (file.parent/link.split('#')[0]).exists(), (file, link)
