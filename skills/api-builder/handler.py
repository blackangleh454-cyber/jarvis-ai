#!/usr/bin/env python3
import sys
import os

PROJECTS_DIR = os.path.expanduser("~/Projects")

REST_API_TEMPLATE = '''from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import jwt
from passlib.context import CryptContext
from functools import wraps
import time

app = FastAPI(
    title="API_NAME",
    description="Professional REST API with authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
def rate_limit(max_calls: int = 100, period: int = 60):
    calls = {}
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client_ip = "default"
            now = time.time()
            if client_ip not in calls:
                calls[client_ip] = []
            calls[client_ip] = [t for t in calls[client_ip] if now - t < period]
            if len(calls[client_ip]) >= max_calls:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            calls[client_ip].append(now)
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Models
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: str
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    price: float = Field(..., gt=0)

class ItemResponse(ItemBase):
    id: str
    price: float
    owner_id: str
    created_at: datetime

# Database (in-memory)
users_db: List[UserResponse] = []
items_db: List[ItemResponse] = []

# Auth functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    for user in users_db:
        if user.username == username:
            return user
    raise credentials_exception

# Auth routes
@app.post("/token", response_model=Token)
@rate_limit(max_calls=10, period=60)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    for user in users_db:
        if user.username == form_data.username:
            if not verify_password(form_data.password, get_password_hash(form_data.username)):
                raise HTTPException(status_code=400, detail="Incorrect password")
            access_token_expires = timedelta(minutes=30)
            access_token = create_access_token(
                data={"sub": user.username}, expires_delta=access_token_expires
            )
            return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="User not found")

@app.post("/register", response_model=UserResponse)
@rate_limit(max_calls=5, period=60)
async def register(user: UserCreate):
    for existing in users_db:
        if existing.email == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if existing.username == user.username:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    new_user = UserResponse(
        id=str(uuid.uuid4()),
        email=user.email,
        username=user.username,
        is_active=True,
        created_at=datetime.utcnow()
    )
    users_db.append(new_user)
    return new_user

# Items CRUD
@app.get("/items", response_model=List[ItemResponse])
async def get_items(skip: int = 0, limit: int = 100):
    return items_db[skip:skip + limit]

@app.get("/items/{{item_id}}", response_model=ItemResponse)
async def get_item(item_id: str):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/items", response_model=ItemResponse)
async def create_item(item: ItemCreate, current_user: UserResponse = Depends(get_current_user)):
    new_item = ItemResponse(
        id=str(uuid.uuid4()),
        name=item.name,
        description=item.description,
        price=item.price,
        owner_id=current_user.id,
        created_at=datetime.utcnow()
    )
    items_db.append(new_item)
    return new_item

@app.put("/items/{{item_id}}", response_model=ItemResponse)
async def update_item(item_id: str, item: ItemCreate, current_user: UserResponse = Depends(get_current_user)):
    for i, existing in enumerate(items_db):
        if existing.id == item_id:
            if existing.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
            item_data = item.model_dump()
            item_data.update({
                "id": item_id,
                "price": item.price,
                "owner_id": current_user.id,
                "created_at": existing.created_at
            })
            items_db[i] = ItemResponse(**item_data)
            return items_db[i]
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/items/{{item_id}}")
async def delete_item(item_id: str, current_user: UserResponse = Depends(get_current_user)):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            if item.owner_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
            items_db.pop(i)
            return {{"message": "Item deleted"}}
    raise HTTPException(status_code=404, detail="Item not found")

# Health check
@app.get("/health")
async def health_check():
    return {{"status": "healthy", "timestamp": datetime.utcnow()}}

# OpenAPI info
@app.get("/")
async def root():
    return {{"message": "Welcome to API_NAME", "docs": "/docs"}}
'''

GRAPHQL_API_TEMPLATE = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry import Schema
from strawberry.fastapi import GraphQLRouter
import strawberry
from datetime import datetime
import uuid

app = FastAPI(
    title="API_NAME",
    description="GraphQL API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Types
@strawberry.type
class User:
    id: str
    username: str
    email: str
    created_at: datetime

@strawberry.type
class Item:
    id: str
    name: str
    description: str
    price: float
    owner_id: str
    created_at: datetime

@strawberry.type
class CreateUserInput:
    username: str
    email: str
    password: str

@strawberry.type
class CreateItemInput:
    name: str
    description: str
    price: float

# Database
users_db = []
items_db = []

# Queries
@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> list[User]:
        return [User(**{{"id": u["id"], "username": u["username"], "email": u["email"], "created_at": u["created_at"]}}) for u in users_db]
    
    @strawberry.field
    def user(self, id: str) -> User:
        for u in users_db:
            if u["id"] == id:
                return User(**u)
        return None
    
    @strawberry.field
    def items(self) -> list[Item]:
        return [Item(**i) for i in items_db]
    
    @strawberry.field
    def item(self, id: str) -> Item:
        for i in items_db:
            if i["id"] == id:
                return Item(**i)
        return None

# Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, input: CreateUserInput) -> User:
        user = {{
            "id": str(uuid.uuid4()),
            "username": input.username,
            "email": input.email,
            "password": input.password,
            "created_at": datetime.utcnow()
        }}
        users_db.append(user)
        return User(**{{k: v for k, v in user.items() if k != "password"}})
    
    @strawberry.mutation
    def create_item(self, input: CreateItemInput) -> Item:
        item = {{
            "id": str(uuid.uuid4()),
            "name": input.name,
            "description": input.description,
            "price": input.price,
            "owner_id": "anonymous",
            "created_at": datetime.utcnow()
        }}
        items_db.append(item)
        return Item(**item)
    
    @strawberry.mutation
    def delete_item(self, id: str) -> bool:
        global items_db
        items_db = [i for i in items_db if i["id"] != id]
        return True

schema = Schema(query=Query, mutation=Mutation)
graphql_router = GraphQLRouter(schema)

app.include_router(graphql_router, prefix="/graphql")

@app.get("/health")
async def health():
    return {{"status": "healthy"}}

@app.get("/")
async def root():
    return {{"message": "GraphQL API", "endpoint": "/graphql"}}
'''

def generate_rest_api(name):
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    project_path = os.path.join(PROJECTS_DIR, name)
    os.makedirs(project_path, exist_ok=True)
    
    template = REST_API_TEMPLATE.replace("API_NAME", name.replace("-", " ").title())
    
    files = {
        os.path.join(project_path, "main.py"): template.replace("{{", "").replace("}}", ""),
        os.path.join(project_path, "requirements.txt"): "fastapi==0.109.0\nuvicorn[standard]==0.27.0\npydantic[email]==2.5.3\npython-jose[cryptography]==3.3.0\npasslib[bcrypt]==1.7.4\npyjwt==2.8.0\npython-multipart==0.0.6\n",
    }
    
    for path, content in files.items():
        with open(path, 'w') as f:
            f.write(content)
    
    return f"REST API created at: {project_path}\n\nTo run:\n  cd {project_path}\n  pip install -r requirements.txt\n  uvicorn main:app --reload"

def generate_graphql_api(name):
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    project_path = os.path.join(PROJECTS_DIR, name)
    os.makedirs(project_path, exist_ok=True)
    
    template = GRAPHQL_API_TEMPLATE.replace("API_NAME", name.replace("-", " ").title())
    
    files = {
        os.path.join(project_path, "main.py"): template.replace("{{", "").replace("}}", ""),
        os.path.join(project_path, "requirements.txt"): "fastapi==0.109.0\nstrawberry-graphql[fastapi]==0.223.0\nuvicorn[standard]==0.27.0\n",
    }
    
    for path, content in files.items():
        with open(path, 'w') as f:
            f.write(content)
    
    return f"GraphQL API created at: {project_path}\n\nTo run:\n  cd {project_path}\n  pip install -r requirements.txt\n  uvicorn main:app --reload"

def main():
    if len(sys.argv) < 2:
        return """Usage: api-builder <command> [args]

Commands:
  generate rest <name>      - Generate REST API with auth
  generate graphql <name>   - Generate GraphQL API

Examples:
  python handler.py generate rest myapi
  python handler.py generate graphql myapi"""
    
    command = sys.argv[1]
    
    if command == "generate":
        if len(sys.argv) < 4:
            return "Usage: generate <rest|graphql> <name>"
        api_type = sys.argv[2]
        name = sys.argv[3]
        
        if api_type == "rest":
            return generate_rest_api(name)
        elif api_type == "graphql":
            return generate_graphql_api(name)
        else:
            return f"Unknown type: {api_type}"
    
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
