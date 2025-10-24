from datetime import timezone
import time

from apscheduler.schedulers.base import STATE_PAUSED


from src.bots.base_bot import BaseBot
from src.schemas.game_info_schema import GameInfoSchema
from .epic_games_store_api import get_free_games
from .scheduler import scheduler


class Notificator:
    def __init__(self, bot: BaseBot):
        self.__bot = bot
        self.running = False

    def __notify_bot(self, game: GameInfoSchema) -> None:
        self.__bot.notify_users(game)

    def _check_store_update(self) -> None:
        free_games = get_free_games()
        if not free_games:
            return

        for game in free_games:
            if game.promotions and game.promotions.upcoming_promotional_offers:
                start_date = game.promotions.upcoming_promotional_offers[0].promotional_offers[0].start_date
                end_date = game.promotions.upcoming_promotional_offers[0].promotional_offers[0].end_date
                scheduler.add_job(
                    func=self.__notify_bot,
                    args=(game,),
                    id=game.id,
                    name="notification",
                    run_date=start_date,
                    misfire_grace_time=int((end_date - start_date).total_seconds())
                    - 3600,  # no less than 1h before the end of the offering
                    replace_existing=True,
                )

    def run(self) -> None:
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
        scheduler.resume() if scheduler.state == STATE_PAUSED else scheduler.start()

        self.running = True
        while self.running:
            time.sleep(0.5)

        scheduler.pause()
