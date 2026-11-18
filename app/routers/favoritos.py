"""Lista de favoritos de cada visitante, guardada en su sesión."""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request  # noqa: F401
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from ..repository_sql import SqlProductoRepository, get_repo

router = APIRouter(prefix="/web/favoritos", include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

Repo = Annotated[SqlProductoRepository, Depends(get_repo)]


def leer_favoritos(request: Request) -> list[int]:
    return request.session.get("favoritos", [])


@router.get("", response_class=HTMLResponse)
def ver_favoritos(request: Request, repo: Repo):
    # En la sesión solo guardamos los id; los datos actuales salen de la base
    productos = [p for p in (repo.get(i) for i in leer_favoritos(request)) if p is not None]
    return templates.TemplateResponse(request, "favoritos.html", {"productos": productos})


@router.post("/{producto_id}")
def agregar_favorito(producto_id: int, request: Request, repo: Repo):
    if repo.get(producto_id) is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    favs = leer_favoritos(request)
    if producto_id not in favs:
        favs.append(producto_id)
    request.session["favoritos"] = favs
    return RedirectResponse("/web/favoritos", status_code=303)



@router.post("/{producto_id}/quitar")
def quitar_favorito(producto_id: int, request: Request):
    request.session["favoritos"] = [i for i in leer_favoritos(request) if i != producto_id]
    return RedirectResponse("/web/favoritos", status_code=303)
