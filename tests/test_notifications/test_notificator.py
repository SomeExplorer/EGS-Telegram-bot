import time
from datetime import datetime, timedelta, timezone
import threading

import pytest
from pytest_mock import MockerFixture
from apscheduler.schedulers.base import STATE_RUNNING, STATE_PAUSED

from src.schemas.game_info_schema import GameInfoSchema
from src.notifications.notificator import Notificator
from src.notifications.scheduler import scheduler
from src.bots.base_bot import BaseBot

TIME_DELTA = 5

test_game_json = {
    "title": "test_game_title",
    "id": "test_game_id",
    "description": "test_game_description",
    "keyImages": [{"type": "OfferImageWide", "url": "http://app.example.net"}],
    "seller": {"id": "test_seller_id", "name": "test_seller_name"},
    "offerMappings": [{"pageSlug": "test_page_slug", "pageType": "test_page_type"}],
    "price": {"totalPrice": {"discountPrice": 100, "originalPrice": 100, "discount": 0}},
    "promotions": {
        "promotionalOffers": [],
        "upcomingPromotionalOffers": [
            {
                "promotionalOffers": [
                    {
                        "startDate": datetime.now(timezone.utc) + timedelta(seconds=TIME_DELTA),
                        "endDate": datetime.now(timezone.utc) + timedelta(seconds=TIME_DELTA + 3601),
                        "discountSetting": {"discountType": "PERCENTAGE", "discountPercentage": 0},
                    }
                ]
            }
        ],
    },
}


class Bot(BaseBot):
    def notify_users(self, game: GameInfoSchema) -> None:
        pass


class TestNotificator:
    notificator = Notificator(Bot())

    @pytest.mark.parametrize("test_games", [[GameInfoSchema(**test_game_json)], None])
    def test_check_store_update(self, test_games: list | None, mocker: MockerFixture):
        mocker.patch("src.notifications.notificator.get_free_games", return_value=test_games)

        jobs_before_update = scheduler.get_jobs()
        self.notificator._check_store_update()
        current_jobs = scheduler.get_jobs()
        if not test_games:
            assert len(current_jobs) == len(jobs_before_update)
        else:
            assert len(current_jobs) - len(jobs_before_update) == len(test_games)
            for test_game in test_games:
                start_date = test_game.promotions.upcoming_promotional_offers[0].promotional_offers[0].start_date
                end_date = test_game.promotions.upcoming_promotional_offers[0].promotional_offers[0].end_date
                added_job = scheduler.get_job(current_jobs[-1].id)
                assert added_job.args == (test_game,)
                assert added_job.name == "notification"
                assert added_job.trigger.run_date == start_date
                assert added_job.misfire_grace_time < int((end_date - start_date).total_seconds())
                added_job.remove()

    def test_run(self):
        thread1 = threading.Thread(target=self.notificator.run)
        thread1.start()
        time.sleep(0.5)
        assert scheduler.state == STATE_RUNNING
        assert self.notificator.running is True

        first_run_job_date = scheduler.get_job("#0").next_run_time
        first_run_jobs_len = len(scheduler.get_jobs())

        self.notificator.running = False
        thread1.join(timeout=1.0)
        assert not thread1.is_alive()
        assert scheduler.state == STATE_PAUSED

        thread2 = threading.Thread(target=self.notificator.run)
        thread2.start()
        time.sleep(0.5)
        assert scheduler.state == STATE_RUNNING
        assert self.notificator.running is True

        assert scheduler.get_job("#0").next_run_time == first_run_job_date
        assert len(scheduler.get_jobs()) == first_run_jobs_len
        self.notificator.running = False
        thread2.join(timeout=1.0)
        assert not thread2.is_alive()
        assert scheduler.state == STATE_PAUSED


if __name__ == "__main__":
    pytest.main()
