import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture
from apscheduler.schedulers.base import STATE_RUNNING, STATE_PAUSED

from src.schemas.game_info_schema import GameInfoSchema
from src.notifications.notifier import Notifier
from src.notifications.scheduler import scheduler
from src.notifications.models import Base, SentNotificationsModel
from src.notifications.database import sync_engine
from src.bot.base_bot import BaseBot

TIME_DELTA = 5

test_game_json = {
    "title": "test_game_title",
    "id": "test_game_id",
    "description": "test_game_description",
    "keyImages": [{"type": "OfferImageWide", "url": "http://app.example.net"}],
    "seller": {"id": "test_seller_id", "name": "test_seller_name"},
    "catalogNs": {"mappings": [{"pageSlug": "test_page_slug", "pageType": "test_page_type"}]},
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
    async def notify_users(self, game: GameInfoSchema) -> None:
        pass


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(sync_engine)
    yield
    Base.metadata.drop_all(sync_engine)


@pytest.fixture()
def clear_jobs():
    scheduler.remove_all_jobs()


class TestNotificator:
    notificator = Notifier(Bot())

    @pytest.mark.usefixtures("clear_jobs")
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
                assert added_job.name == test_game.title
                assert added_job.trigger.run_date == start_date
                assert added_job.misfire_grace_time < int((end_date - start_date).total_seconds())
                added_job.remove()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("clear_jobs")
    @pytest.mark.parametrize("test_games", [[GameInfoSchema(**test_game_json)]])
    async def test_run(self, test_games: list | None, mocker: MockerFixture):
        mocker.patch("src.notifications.notificator.get_free_games", return_value=test_games)
        mock_notify_users = mocker.patch(
            "tests.test_notifications.test_notificator.Bot.notify_users", new_callable=AsyncMock
        )

        assert mock_notify_users is not None
        run_task = asyncio.create_task(self.notificator.run())
        await asyncio.sleep(7)
        assert scheduler.state == STATE_RUNNING
        assert self.notificator.running is True
        first_run_updating_date = scheduler.get_job("#0").next_run_time
        mock_notify_users.assert_called_once()

        self.notificator.running = False
        await asyncio.sleep(1)
        assert run_task.done()
        assert scheduler.state == STATE_PAUSED

        asyncio.create_task(self.notificator.run())
        await asyncio.sleep(5)
        assert scheduler.state == STATE_RUNNING
        assert self.notificator.running is True
        assert scheduler.get_job("#0").next_run_time == first_run_updating_date
        mock_notify_users.assert_called_once()


if __name__ == "__main__":
    pytest.main()
