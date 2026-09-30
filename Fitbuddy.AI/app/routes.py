from pathlib import Path

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import SessionLocal
from app.models import User
from app.schemas import UserInput
from app.ai import (
    generate_workout_gemini,
    generate_nutrition_tip_with_flash,
    update_workout_plan
)

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):
    try:
        data = UserInput(
            username=username.strip(),
            user_id=user_id.strip(),
            age=age,
            goal=goal,
            intensity=intensity
        )
    except Exception:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "Please check your details and try again."
            },
            status_code=422
        )

    plan = generate_workout_gemini(data)
    tip = generate_nutrition_tip_with_flash(data.goal)

    db = SessionLocal()

    try:
        user = db.query(User).filter_by(
            user_id=data.user_id
        ).first()

        if user:
            user.username = data.username
            user.age = data.age
            user.goal = data.goal
            user.intensity = data.intensity
            user.original_plan = plan
            user.updated_plan = None
            user.feedback = None
            user.nutrition_tip = tip
        else:
            user = User(
                user_id=data.user_id,
                username=data.username,
                age=data.age,
                goal=data.goal,
                intensity=data.intensity,
                original_plan=plan,
                nutrition_tip=tip
            )
            db.add(user)

        db.commit()
        db.refresh(user)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "tip": tip,
                "updated": False
            }
        )
    finally:
        db.close()


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...)
):
    feedback = feedback.strip()

    if len(feedback) < 3 or len(feedback) > 1000:
        raise HTTPException(
            status_code=422,
            detail="Feedback must be 3 to 1000 characters."
        )

    db = SessionLocal()

    try:
        user = db.query(User).filter_by(
            user_id=user_id.strip()
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User ID not found. Generate a plan first."
            )

        revised_plan = update_workout_plan(
            user.updated_plan or user.original_plan,
            feedback,
            user.age
        )

        user.updated_plan = revised_plan
        user.feedback = feedback

        user.nutrition_tip = generate_nutrition_tip_with_flash(
            user.goal
        )

        db.commit()
        db.refresh(user)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": revised_plan,
                "tip": user.nutrition_tip,
                "updated": True
            }
        )
    finally:
        db.close()


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    db = SessionLocal()

    try:
        users = db.query(User).order_by(
            User.id.desc()
        ).all()

        return templates.TemplateResponse(
            request=request,
            name="all_users.html",
            context={"users": users}
        )
    finally:
        db.close()


@router.get("/health")
def health():
    return {"status": "ok"}