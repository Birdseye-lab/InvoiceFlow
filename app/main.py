from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import engine
from app.models import Client, Project, Invoice, User
from app.auth import hash_password, verify_password, create_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


app = FastAPI(
    title="InvoiceFlow API",
    description="Invoice and payment management API",
    version="1.0.0",
)


def get_db():
    with Session(engine) as session:
        yield session

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        from jose import jwt
        from app.auth import SECRET_KEY, ALGORITHM

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

        user = db.query(User).filter(User.id == int(user_id)).first()

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found",
            )

        return user

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

class ClientCreate(BaseModel):
    name: str
    email: str


class UserCreate(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@app.get("/")
def root():
    return {"message": "InvoiceFlow API is running"}

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
    }

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.email == form_data.username).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(form_data.password, db_user.hashed_password):        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token({
        "sub": str(db_user.id)
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.get("/clients")
def get_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clients = db.query(Client).filter(Client.user_id == current_user.id).all()
    return [
        {
            "id": client.id,
            "name": client.name,
            "email": client.email,
        }
        for client in clients
    ]

@app.post("/clients")
def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_client = Client(
        name=client.name,
        email=client.email,
        user_id=current_user.id,
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return {
        "id": new_client.id,
        "name": new_client.name,
        "email": new_client.email,
    }
@app.get("/clients/{client_id}")
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = (
        db.query(Client)
        .filter(
            Client.id == client_id,
            Client.user_id == current_user.id,
        )
        .first()
    )

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    return {
        "id": client.id,
        "name": client.name,
        "email": client.email,
    }

@app.put("/clients/{client_id}")
def update_client(
    client_id: int,
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = (
        db.query(Client)
        .filter(
            Client.id == client_id,
            Client.user_id == current_user.id,
        )
        .first()
    )

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client.name = client_data.name
    client.email = client_data.email

    db.commit()
    db.refresh(client)

    return {
        "id": client.id,
        "name": client.name,
        "email": client.email,
    }

@app.delete("/clients/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = (
        db.query(Client)
        .filter(
            Client.id == client_id,
            Client.user_id == current_user.id,
        )
        .first()
    )

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    db.delete(client)
    db.commit()

    return {
        "message": "Client deleted successfully"
    }

class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    client_id: int


@app.post("/projects")
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = db.get(Client, project.client_id)

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    new_project = Project(
        name=project.name,
        description=project.description,
        client_id=project.client_id,
        user_id=current_user.id,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return {
        "id": new_project.id,
        "name": new_project.name,
        "description": new_project.description,
        "client_id": new_project.client_id,
    }

@app.get("/projects")
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()

    return [
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "client_id": project.client_id,
        }
        for project in projects
    ]

@app.get("/projects/{project_id}")
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
        .first()
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "client_id": project.client_id,
    }

class ProjectUpdate(BaseModel):
    name: str
    description: str | None = None
    client_id: int

@app.put("/projects/{project_id}")
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
        .first()
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    client = (
        db.query(Client)
        .filter(
            Client.id == project_data.client_id,
            Client.user_id == current_user.id,
        )
        .first()
    )

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    project.name = project_data.name
    project.description = project_data.description
    project.client_id = project_data.client_id

    db.commit()
    db.refresh(project)

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "client_id": project.client_id,
    }

@app.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user.id,
        )
        .first()
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    return {
        "message": "Project deleted successfully"
    }

class InvoiceCreate(BaseModel):
    number: str
    amount: float
    status: str = "unpaid"
    project_id: int


@app.post("/invoices")
def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = db.get(Project, invoice.project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    new_invoice = Invoice(
        number=invoice.number,
        amount=invoice.amount,
        status=invoice.status,
        project_id=invoice.project_id,
        user_id=current_user.id,
    )

    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    return {
        "id": new_invoice.id,
        "number": new_invoice.number,
        "amount": new_invoice.amount,
        "status": new_invoice.status,
        "project_id": new_invoice.project_id,
    }

@app.get("/invoices")
def get_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoices = db.query(Invoice).filter(Invoice.user_id == current_user.id).all()

    return [
        {
            "id": invoice.id,
            "number": invoice.number,
            "amount": invoice.amount,
            "status": invoice.status,
            "project_id": invoice.project_id,
        }
        for invoice in invoices
    ]
    

@app.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clients = (
        db.query(Client)
        .filter(Client.user_id == current_user.id)
        .all()
    )

    projects = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .all()
    )

    invoices = (
        db.query(Invoice)
        .filter(Invoice.user_id == current_user.id)
        .all()
    )

    total_clients = len(clients)
    total_projects = len(projects)
    total_invoices = len(invoices)

    paid_invoices = sum(
        1 for invoice in invoices if invoice.status == "paid"
    )

    unpaid_invoices = sum(
        1 for invoice in invoices if invoice.status == "unpaid"
    )

    total_revenue = sum(
        invoice.amount
        for invoice in invoices
        if invoice.status == "paid"
    )

    return {
        "total_clients": total_clients,
        "total_projects": total_projects,
        "total_invoices": total_invoices,
        "paid_invoices": paid_invoices,
        "unpaid_invoices": unpaid_invoices,
        "total_revenue": total_revenue,
    }

@app.get("/invoices/{invoice_id}")
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id,
            Invoice.user_id == current_user.id,
        )
        .first()
    )

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return {
        "id": invoice.id,
        "number": invoice.number,
        "amount": invoice.amount,
        "status": invoice.status,
        "project_id": invoice.project_id,
    }

class InvoiceUpdate(BaseModel):
    number: str
    amount: float
    status: str
    project_id: int


@app.put("/invoices/{invoice_id}")
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id,
            Invoice.user_id == current_user.id,
        )
        .first()
    )

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    project = (
        db.query(Project)
        .filter(
            Project.id == invoice_data.project_id,
            Project.user_id == current_user.id,
        )
        .first()
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    invoice.number = invoice_data.number
    invoice.amount = invoice_data.amount
    invoice.status = invoice_data.status
    invoice.project_id = invoice_data.project_id

    db.commit()
    db.refresh(invoice)

    return {
        "id": invoice.id,
        "number": invoice.number,
        "amount": invoice.amount,
        "status": invoice.status,
        "project_id": invoice.project_id,
    }

@app.delete("/invoices/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id,
            Invoice.user_id == current_user.id,
        )
        .first()
    )

    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    db.delete(invoice)
    db.commit()

    return {
        "message": "Invoice deleted successfully"
    }