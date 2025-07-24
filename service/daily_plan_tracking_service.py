from sqlalchemy.orm import Session
from entity.daily_plan_tracking import DailyPlanTracking, DailyPlanTrackingCreateUpdate
from typing import List, Optional

class DailyPlanTrackingService:
    @staticmethod
    def create(db: Session, data: DailyPlanTrackingCreateUpdate) -> DailyPlanTracking:
        tracking = DailyPlanTracking(**data)
        db.add(tracking)
        db.commit()
        db.refresh(tracking)
        return tracking

    @staticmethod
    def update(db: Session, tracking: DailyPlanTracking, data: DailyPlanTrackingCreateUpdate) -> DailyPlanTracking:
        for field, value in data.items():
            setattr(tracking, field, value)
        db.commit()
        db.refresh(tracking)
        return tracking

    @staticmethod
    def get_by_id(db: Session, tracking_id: int, user_id: Optional[int] = None) -> Optional[DailyPlanTracking]:
        query = db.query(DailyPlanTracking).filter(DailyPlanTracking.id == tracking_id)
        if user_id is not None:
            query = query.filter(DailyPlanTracking.user_id == user_id)
        return query.first()

    @staticmethod
    def get_all(db: Session, user_id: Optional[int] = None) -> List[DailyPlanTracking]:
        query = db.query(DailyPlanTracking)
        if user_id is not None:
            query = query.filter(DailyPlanTracking.user_id == user_id)
        return query.all()

    @staticmethod
    def log_food_event(db: Session, user_id: int, date, food_summary: str, calories: float = 0, protein: float = 0, carbohydrates: float = 0, fat: float = 0, fiber: float = 0):
        from datetime import date as dt_date
        if isinstance(date, str):
            date = dt_date.fromisoformat(date)
        tracking = DailyPlanTracking(
            user_id=user_id,
            date=date,
            meals_logged=True,
            meal_summary=food_summary,
            calories_intake=calories,
            protein=protein,
            carbohydrates=carbohydrates,
            fat=fat,
            fiber=fiber
        )
        db.add(tracking)
        db.commit()
        db.refresh(tracking)
        return tracking

    @staticmethod
    def log_exercise_event(db: Session, user_id: int, date, exercise_summary: str, calories_burned: float = 0, reps: int = 0):
        # Find or create today's tracking
        from datetime import date as dt_date
        if isinstance(date, str):
            date = dt_date.fromisoformat(date)
        tracking = db.query(DailyPlanTracking).filter(DailyPlanTracking.user_id == user_id, DailyPlanTracking.date == date).first()
        if not tracking:
            tracking = DailyPlanTracking(user_id=user_id, date=date, exercise_done=True, exercise_summary=exercise_summary, calories_burned=calories_burned, reps_done=reps)
            db.add(tracking)
        else:
            tracking.exercise_done = True
            tracking.exercise_summary = (tracking.exercise_summary or "") + ("\n" if tracking.exercise_summary else "") + exercise_summary
            tracking.calories_burned = (tracking.calories_burned or 0) + (calories_burned or 0)
            tracking.reps_done = (tracking.reps_done or 0) + (reps or 0)
        db.commit()
        db.refresh(tracking)
        return tracking

    @staticmethod
    def get_today_summary(db: Session, user_id: int):
        from datetime import date as dt_date
        today = dt_date.today()
        tracking_entries = db.query(DailyPlanTracking).filter(
            DailyPlanTracking.user_id == user_id,
            DailyPlanTracking.date == today
        ).all()

        if not tracking_entries:
            return None

        summaries = []
        for tracking in tracking_entries:
            summaries.append({
                "exercise_summary": tracking.exercise_summary,
                "meals_logged": tracking.meals_logged,
                "meal_summary": tracking.meal_summary,
                "calories_burned": tracking.calories_burned,
                "calories_intake": tracking.calories_intake,
                "protein": tracking.protein,
                "carbohydrates": tracking.carbohydrates,
                "fat": tracking.fat,
                "fiber": tracking.fiber,
                "reps_done": tracking.reps_done
            })
        return summaries