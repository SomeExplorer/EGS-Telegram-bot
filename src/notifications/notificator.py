import asyncio
from datetime import timezone, timedelta

from apscheduler.schedulers.base import STATE_PAUSED

from src.bots.base_bot import BaseBot
from src.schemas.game_info_schema import GameInfoSchema
from src.notifications.epic_games_store_api import get_free_games
from src.notifications.scheduler import scheduler
from src.notifications.database import Database


class Notificator:
    def __init__(self, bot: BaseBot):
        self.bot = bot
        self.running = False

    async def run(self) -> None:
        scheduler.resume() if scheduler.state == STATE_PAUSED else scheduler.start()
        self.running = True

        self._check_store_update()
        self._add_updating_task()

        while self.running:
            await asyncio.sleep(0.5)

        scheduler.pause()

    def _check_store_update(self) -> None:
        free_games = get_free_games()
        if not free_games:
            return

        for game in free_games:
            self._add_game_task(game)

    def _add_game_task(self, game: GameInfoSchema) -> None:
        if self._already_notified(game):
            return

        if game.promotions:
            if game.promotions.promotional_offers:
                start_date = game.promotions.promotional_offers[0].promotional_offers[0].start_date
                end_date = game.promotions.promotional_offers[0].promotional_offers[0].end_date
            else:
                start_date = game.promotions.upcoming_promotional_offers[0].promotional_offers[0].start_date
                end_date = game.promotions.upcoming_promotional_offers[0].promotional_offers[0].end_date

            scheduler.add_job(
                func=self._notify_bot,
                args=(game,),
                id=game.id,
                name=game.title,
                run_date=start_date,
                misfire_grace_time=int((end_date - start_date - timedelta(hours=1)).total_seconds()),
                replace_existing=True,
            )

    @staticmethod
    def _already_notified(game: GameInfoSchema) -> bool:
        return game.id in Database.select_last_30_days_games_ids()

    async def _notify_bot(self, game: GameInfoSchema) -> None:
        await self.bot.notify_users(game)

    def _add_updating_task(self) -> None:
        job_id = "#0"
        if not scheduler.get_job(job_id):
            scheduler.add_job(
                func=self._check_store_update,
                trigger="interval",
                days=1,
                timezone=timezone.utc,
                id=job_id,
                name="updating",
                replace_existing=True,
            )
