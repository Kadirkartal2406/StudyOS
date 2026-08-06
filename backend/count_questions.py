import asyncio
import sys

sys.path.insert(0, r"C:\projects\StudyOS\backend")
from app.db.session import AsyncSessionLocal
from sqlalchemy import select, func
from app.models.question_pool import QuestionPoolCard

async def count_questions():
    async with AsyncSessionLocal() as db:
        stmt = select(func.count(QuestionPoolCard.id))
        result = await db.execute(stmt)
        total = result.scalar()
        print(f"Total questions in QuestionPoolCard: {total}")

if __name__ == "__main__":
    asyncio.run(count_questions())
