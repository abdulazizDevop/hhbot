"""Employer router"""
from aiogram import Router
from handlers.employer.callbacks import router as callbacks_router
from handlers.employer.messages import router as messages_router

router = Router()
router.include_router(callbacks_router)
router.include_router(messages_router)

