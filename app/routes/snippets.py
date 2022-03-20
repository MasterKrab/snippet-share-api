from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.oauth2 import optional_get_current_user, get_current_user
from typing import List
from sqlalchemy.sql import func

router = APIRouter(prefix="/snippets", tags=["Snippets"])


@router.get("/", response_model=List[schemas.SnippetOutput])
def get_snippets(user=Depends(get_current_user), db: Session = Depends(get_db)):
    snippets = db.query(models.Snippet).filter(models.Snippet.user_id == user.id).all()

    return snippets


@router.get("/{id}", response_model=schemas.SnippetOutput)
def get_snippet(id: int, db: Session = Depends(get_db)):
    snippet = db.query(models.Snippet).filter(models.Snippet.id == id).first()

    if not snippet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Snippet not found",
        )

    return snippet


@router.post("/", response_model=schemas.SnippetOutput, status_code=status.HTTP_201_CREATED)
def create_snippet(snippet: schemas.SnippetCreate, user=Depends(optional_get_current_user), db: Session = Depends(get_db)):
    if user:
        new_snippet = models.Snippet(**snippet.dict(), user_id=user.id)
    else:
        new_snippet = models.Snippet(**snippet.dict())

    db.add(new_snippet)
    db.commit()
    db.refresh(new_snippet)

    return new_snippet


@router.put("/", response_model=schemas.SnippetOutput)
def update_snippet(snippet: schemas.SnippetUpdate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    snippet_query = db.query(models.Snippet).filter(models.Snippet.id == snippet.id)

    snippet_to_update = snippet_query.first()

    if not snippet_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Snippet not found",
        )

    if snippet_to_update.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this snippet",
        )

    snippet_query.update({**snippet.dict(), "updated_at": func.now()})
    db.commit()
    db.refresh(snippet_to_update)

    return snippet_to_update


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snippet(id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    snippet = db.query(models.Snippet).filter(models.Snippet.id == id).first()

    if snippet.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this snippet",
        )

    db.delete(snippet)
    db.commit()
