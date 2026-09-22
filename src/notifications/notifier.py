import asyncio
from datetime import timezone, timedelta

from apscheduler.schedulers.base import STATE_PAUSED

from src.bot.base_bot import BaseBot
from src.logger import logger
from src.config import settings
from src.schemas.game_info_schema import GameInfoSchema, PromotionalOfferSchema
from src.notifications.constants import UPDATING_TASK_ID
from src.notifications.database import Database
from src.notifications.epic_games_store_api import get_free_games
from src.notifications.scheduler import scheduler


class Notifier:
    def __init__(self, bot: BaseBot):
        self.bot = bot
        self.running = False

    async def run(self) -> None:
        scheduler.resume() if scheduler.state == STATE_PAUSED else scheduler.start()
        logger.info("scheduler запущен")
        self.running = True

        self._check_store_update()
        self._add_updating_task()

        while self.running:
            await asyncio.sleep(0.5)

        scheduler.pause()
        logger.info("scheduler приостановлен")

    def _check_store_update(self) -> None:
        free_games = get_free_games(
            locale=settings.locale,
            country=settings.country,
            allow_countries=settings.allow_countries,
        )
        if not free_games:
            return

        for game in free_games:
            self._add_game_task(game)

    def _add_game_task(self, game: GameInfoSchema) -> None:
        if self._already_notified(game):
            return

        def find_free_offer(offers: list) -> PromotionalOfferSchema | None:
            return next(filter(lambda offer: offer.discount_setting.discount_percentage == 0, offers), None)

        if game.promotions:
            if game.promotions.promotional_offers and (
                free_offer := find_free_offer(game.promotions.promotional_offers[0].promotional_offers)
            ):
                start_date = free_offer.start_date
                end_date = free_offer.end_date
            elif game.promotions.upcoming_promotional_offers and (
                free_offer := find_free_offer(game.promotions.upcoming_promotional_offers[0].promotional_offers)
            ):
                start_date = free_offer.start_date
                end_date = free_offer.end_date
            else:
                start_date = end_date = None

            if start_date:
                scheduler.add_job(
                    func=self._notify_bot,
                    args=(game,),
                    id=game.id,
                    name=game.title,
                    run_date=start_date,
                    misfire_grace_time=int((end_date - start_date - timedelta(hours=1)).total_seconds()),
                    replace_existing=True,
                )
                logger.info(f"{scheduler.get_job(game.id)} добавлена в scheduler")

    @staticmethod
    def _already_notified(game: GameInfoSchema) -> bool:
        return game.id in Database.select_last_30_days_games_ids()

    async def _notify_bot(self, game: GameInfoSchema) -> None:
        logger.info(f"{self.__class__.__name__} вызывает оповещение об игре {game.title} (id={game.id})")
        await self.bot.notify_users(game)

    def _add_updating_task(self) -> None:
        if not scheduler.get_job(UPDATING_TASK_ID):
            scheduler.add_job(
                func=self._check_store_update,
                trigger="interval",
                hours=1,
                timezone=timezone.utc,
                id=UPDATING_TASK_ID,
                name="updating",
                replace_existing=True,
            )
