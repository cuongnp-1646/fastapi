import json

import redis
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import crud
import schemas
from cache import redis_client
from database import get_db

router = APIRouter(prefix="/tags", tags=["tags"])

CACHE_TTL_SECONDS = 300


@router.get("/", response_model=list[schemas.Tag])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cache_key = f"tags:{skip}:{limit}"
    try:
        cached = redis_client.get(cache_key)
    except redis.RedisError:
        cached = None
    if cached is not None:
        return json.loads(cached)

    tags = crud.get_tags(db, skip=skip, limit=limit)
    result = [schemas.Tag.model_validate(tag).model_dump(mode="json") for tag in tags]

    try:
        redis_client.set(cache_key, json.dumps(result), ex=CACHE_TTL_SECONDS)
    except redis.RedisError:
        pass
    return result
