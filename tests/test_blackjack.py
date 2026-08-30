import asyncio
import unittest
from unittest.mock import patch

import psycopg2

import blackjack


class FakeCursor:
    def __init__(self, balances):
        self.balances = balances
        self.fetchone_result = None
        self.fetchall_result = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, query, parameters=None):
        normalized_query = " ".join(query.split()).upper()

        if normalized_query.startswith("INSERT INTO USER_BALANCES"):
            user_id, starting_balance = parameters
            self.balances.setdefault(user_id, starting_balance)
        elif normalized_query.startswith("SELECT BALANCE FROM USER_BALANCES"):
            user_id = parameters[0]
            self.fetchone_result = (self.balances[user_id],)
        elif normalized_query.startswith("UPDATE USER_BALANCES"):
            amount, user_id = parameters
            self.balances[user_id] += amount
            self.fetchone_result = (self.balances[user_id],)
        elif normalized_query.startswith("SELECT USER_ID, BALANCE"):
            self.fetchall_result = list(self.balances.items())
        else:
            raise AssertionError(f"Unexpected query in test: {normalized_query}")

    def fetchone(self):
        return self.fetchone_result

    def fetchall(self):
        return self.fetchall_result


class FakeConnection:
    def __init__(self, balances):
        self.balances = balances

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def cursor(self):
        return FakeCursor(self.balances)


class FakeMessage:
    def __init__(self, content, author, channel):
        self.content = content
        self.author = author
        self.channel = channel


class FakeAuthor:
    def __init__(self, user_id):
        self.id = user_id


class FakeChannel:
    id = 123


class FakeBot:
    def __init__(self, context, responses=None):
        self.context = context
        self.responses = list(responses or [])

    async def wait_for(self, event, *, check, timeout):
        self.context.wait_for_calls += 1
        if not self.responses:
            raise AssertionError("The test did not provide another user response.")

        response = self.responses.pop(0)
        if isinstance(response, BaseException):
            raise response

        message = FakeMessage(
            content=response,
            author=self.context.author,
            channel=self.context.channel,
        )
        if not check(message):
            raise AssertionError("The blackjack message check rejected a valid response.")
        return message


class FakeContext:
    def __init__(self, user_id=1, responses=None, fail_on_send=None):
        self.author = FakeAuthor(user_id)
        self.channel = FakeChannel()
        self.messages = []
        self.send_calls = 0
        self.wait_for_calls = 0
        self.fail_on_send = fail_on_send
        self.bot = FakeBot(self, responses)

    async def send(self, message):
        self.send_calls += 1
        if self.send_calls == self.fail_on_send:
            raise RuntimeError("simulated Discord send failure")
        self.messages.append(message)


def fake_connect(balances):
    return lambda database_url: FakeConnection(balances)


class BalanceDatabaseTests(unittest.TestCase):
    def test_new_user_is_persisted_at_100(self):
        balances = {}
        with patch.object(
            blackjack.psycopg2,
            "connect",
            side_effect=fake_connect(balances),
        ):
            balance = blackjack.get_user_balance(10)

        self.assertEqual(balance, 100)
        self.assertEqual(balances, {10: 100})

    def test_existing_user_balance_is_preserved(self):
        balances = {10: 437}
        with patch.object(
            blackjack.psycopg2,
            "connect",
            side_effect=fake_connect(balances),
        ):
            balance = blackjack.get_user_balance(10)

        self.assertEqual(balance, 437)
        self.assertEqual(balances, {10: 437})

    def test_first_win_starts_from_persisted_100(self):
        balances = {}
        with patch.object(
            blackjack.psycopg2,
            "connect",
            side_effect=fake_connect(balances),
        ):
            balance = blackjack.update_user_balance(10, 50)

        self.assertEqual(balance, 150)
        self.assertEqual(balances, {10: 150})

    def test_first_loss_starts_from_persisted_100(self):
        balances = {}
        with patch.object(
            blackjack.psycopg2,
            "connect",
            side_effect=fake_connect(balances),
        ):
            balance = blackjack.update_user_balance(10, -50)

        self.assertEqual(balance, 50)
        self.assertEqual(balances, {10: 50})

    def test_normal_update_preserves_existing_balance(self):
        balances = {10: 250}
        with patch.object(
            blackjack.psycopg2,
            "connect",
            side_effect=fake_connect(balances),
        ):
            balance = blackjack.update_user_balance(10, 25)

        self.assertEqual(balance, 275)
        self.assertEqual(balances, {10: 275})


class HandCalculationTests(unittest.TestCase):
    def test_multi_ace_totals(self):
        cases = [
            ([11, 11], 12),
            ([11, 11, 9], 21),
            ([11, 11, 10, 9], 21),
            ([11, 11, 11, 9], 12),
        ]

        for hand, expected_total in cases:
            with self.subTest(hand=hand):
                self.assertEqual(blackjack.calculate_hand(hand), expected_total)

    def test_calculate_hand_does_not_mutate_hand(self):
        hand = [11, 11, 9]
        original_hand = hand.copy()

        blackjack.calculate_hand(hand)

        self.assertEqual(hand, original_hand)

    def test_dealer_hits_and_stands_using_soft_hand_total(self):
        self.assertTrue(blackjack.dealer_should_hit([11, 5]))
        self.assertTrue(blackjack.dealer_should_hit([11, 5, 10]))
        self.assertFalse(blackjack.dealer_should_hit([11, 6]))
        self.assertFalse(blackjack.dealer_should_hit([11, 7]))


class GameResultTests(unittest.TestCase):
    def test_player_win(self):
        self.assertEqual(
            blackjack.determine_game_result([10, 9], [10, 8], 50),
            ("win", 50),
        )

    def test_player_loss(self):
        self.assertEqual(
            blackjack.determine_game_result([10, 7], [10, 8], 50),
            ("loss", -50),
        )

    def test_push(self):
        self.assertEqual(
            blackjack.determine_game_result([10, 8], [9, 9], 50),
            ("push", 0),
        )

    def test_player_bust(self):
        self.assertEqual(
            blackjack.determine_game_result([10, 8, 7], [10, 8], 50),
            ("player_bust", -50),
        )

    def test_dealer_bust(self):
        self.assertEqual(
            blackjack.determine_game_result([10, 8], [10, 7, 8], 50),
            ("dealer_bust", 50),
        )

    def test_natural_blackjack_pays_1_point_5_profit(self):
        self.assertEqual(
            blackjack.determine_game_result([11, 10], [10, 9], 25),
            ("natural", 38),
        )

    def test_both_natural_blackjacks_push(self):
        self.assertEqual(
            blackjack.determine_game_result([11, 10], [10, 11], 50),
            ("push", 0),
        )


class BlackjackCommandTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        blackjack.ongoing_games.clear()
        blackjack.last_gift_times.clear()
        blackjack.game_lock = asyncio.Lock()
        blackjack.gift_lock = asyncio.Lock()

    async def test_first_gift_results_in_200(self):
        balances = {}
        context = FakeContext(user_id=10)
        with patch.object(
            blackjack.psycopg2,
            "connect",
            side_effect=fake_connect(balances),
        ):
            await blackjack.daily_gift(context)

        self.assertEqual(balances, {10: 200})
        self.assertIn("**New Balance: 200  💎**", context.messages[-1])

    async def test_natural_blackjack_settles_exactly_once(self):
        context = FakeContext(user_id=10, responses=["50"])
        cards = [10, 9, 11, 10]

        with (
            patch.object(blackjack, "get_user_balance", return_value=100),
            patch.object(blackjack, "update_user_balance", return_value=175) as update,
            patch.object(blackjack, "deal_card", side_effect=cards),
        ):
            await blackjack.play_blackjack(context)

        update.assert_called_once_with(10, 75)
        self.assertTrue(
            any("You got a natural blackjack" in message for message in context.messages)
        )
        self.assertNotIn(10, blackjack.ongoing_games)

    async def test_invalid_bet_and_action_inputs_still_reprompt(self):
        context = FakeContext(
            user_id=10,
            responses=["not-a-number", "500", "50", "dance", "stay"],
        )
        cards = [10, 8, 10, 9]

        with (
            patch.object(blackjack, "get_user_balance", return_value=100),
            patch.object(blackjack, "update_user_balance", return_value=150) as update,
            patch.object(blackjack, "deal_card", side_effect=cards),
        ):
            await blackjack.play_blackjack(context)

        update.assert_called_once_with(10, 50)
        self.assertEqual(context.wait_for_calls, 5)
        self.assertTrue(
            any("Please enter a valid number" in message for message in context.messages)
        )
        self.assertTrue(
            any("Invalid amount" in message for message in context.messages)
        )
        self.assertTrue(
            any("Invalid input" in message for message in context.messages)
        )

    async def test_cleanup_after_input_timeout(self):
        context = FakeContext(
            user_id=10,
            responses=[asyncio.TimeoutError()],
        )

        with patch.object(blackjack, "get_user_balance", return_value=100):
            await blackjack.play_blackjack(context)

        self.assertNotIn(10, blackjack.ongoing_games)
        self.assertIn("game has been canceled", context.messages[-1])

    async def test_cleanup_and_friendly_message_after_database_failure(self):
        context = FakeContext(user_id=10)

        with patch.object(
            blackjack,
            "get_user_balance",
            side_effect=psycopg2.OperationalError("database details"),
        ):
            await blackjack.play_blackjack(context)

        self.assertNotIn(10, blackjack.ongoing_games)
        self.assertEqual(context.messages, [blackjack.AURA_BANK_UNAVAILABLE])
        self.assertNotIn("database details", context.messages[0])

    async def test_cleanup_after_unexpected_exception(self):
        context = FakeContext(user_id=10, responses=[RuntimeError("unexpected")])

        with (
            patch.object(blackjack, "get_user_balance", return_value=100),
            self.assertRaises(RuntimeError),
        ):
            await blackjack.play_blackjack(context)

        self.assertNotIn(10, blackjack.ongoing_games)

    async def test_cleanup_after_discord_send_failure(self):
        context = FakeContext(user_id=10, fail_on_send=1)

        with (
            patch.object(blackjack, "get_user_balance", return_value=100),
            self.assertRaises(RuntimeError),
        ):
            await blackjack.play_blackjack(context)

        self.assertNotIn(10, blackjack.ongoing_games)

    async def test_cleanup_after_cancellation(self):
        context = FakeContext(user_id=10, responses=[asyncio.CancelledError()])

        with (
            patch.object(blackjack, "get_user_balance", return_value=100),
            self.assertRaises(asyncio.CancelledError),
        ):
            await blackjack.play_blackjack(context)

        self.assertNotIn(10, blackjack.ongoing_games)

    async def test_existing_global_one_game_restriction_is_preserved(self):
        blackjack.ongoing_games[99] = True
        context = FakeContext(user_id=10)

        with patch.object(blackjack, "get_user_balance") as get_balance:
            await blackjack.play_blackjack(context)

        get_balance.assert_not_called()
        self.assertEqual(
            context.messages,
            ["Someone is in a game right now, **wait!**"],
        )
        self.assertEqual(blackjack.ongoing_games, {99: True})


if __name__ == "__main__":
    unittest.main()
