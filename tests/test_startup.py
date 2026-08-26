import importlib
import os
import sys
import unittest
from unittest.mock import patch


YAHOO_ENV_VARS = {
    "ACCESS_TOKEN",
    "CONSUMER_KEY",
    "CONSUMER_SECRET",
    "REFRESH_TOKEN",
    "TOKEN_TIME",
    "TOKEN_TYPE",
    "LEAGUE_ID",
}

OPTIONAL_PROVIDER_ENV_VARS = {
    "OPENAI_API_KEY",
    "CHAI_API",
    "WEATHER_API",
    "FORTNITE_API",
    "GIPHY_KEY",
}

PRODUCTION_COMMANDS = {
    "commands",
    "hello",
    "abc",
    "fort",
    "shop",
    "map",
    "stats",
    "joke",
    "weather",
    "goat",
    "chat",
    "fantasy",
    "play",
    "blackjack",
    "gift",
    "scores",
    "leaderboard",
    "balance",
    "bal",
}


def import_slurpy_without_optional_configuration():
    sys.modules.pop("slurpybot", None)
    sys.modules.pop("fantasy", None)

    with patch.dict(os.environ, {"FANTASY_ENABLED": "false"}, clear=False):
        for name in YAHOO_ENV_VARS | OPTIONAL_PROVIDER_ENV_VARS:
            os.environ.pop(name, None)
        return importlib.import_module("slurpybot")


class StartupIsolationTests(unittest.TestCase):
    def test_import_does_not_start_discord_or_webserver(self):
        import webserver
        from discord.ext import commands

        with (
            patch.object(webserver, "keep_alive") as keep_alive,
            patch.object(commands.Bot, "run") as client_run,
        ):
            import_slurpy_without_optional_configuration()

        keep_alive.assert_not_called()
        client_run.assert_not_called()

    def test_fantasy_is_not_imported_or_initialized_when_disabled(self):
        slurpybot = import_slurpy_without_optional_configuration()

        self.assertFalse(slurpybot.FANTASY_ENABLED)
        self.assertIsNone(slurpybot.main_menu)
        self.assertNotIn("fantasy", sys.modules)

    def test_fantasy_is_still_lazy_when_enabled(self):
        sys.modules.pop("slurpybot", None)
        sys.modules.pop("fantasy", None)

        with patch.dict(os.environ, {"FANTASY_ENABLED": "true"}, clear=False):
            slurpybot = importlib.import_module("slurpybot")

        self.assertTrue(slurpybot.FANTASY_ENABLED)
        self.assertIsNone(slurpybot.main_menu)
        self.assertNotIn("fantasy", sys.modules)

    def test_all_production_commands_remain_registered(self):
        slurpybot = import_slurpy_without_optional_configuration()
        registered_commands = {command.name for command in slurpybot.client.commands}

        self.assertTrue(PRODUCTION_COMMANDS <= registered_commands)

    def test_optional_clients_are_not_created_during_import(self):
        import_slurpy_without_optional_configuration()

        lazy_clients = {
            "chat": "client",
            "chai": "character_client",
            "fortnite": "fort_api",
        }
        for module_name, attribute in lazy_clients.items():
            module = sys.modules.get(module_name)
            if module is not None:
                self.assertIsNone(getattr(module, attribute))

    def test_normal_start_path_reaches_discord_without_yahoo(self):
        slurpybot = import_slurpy_without_optional_configuration()

        with (
            patch.dict(
                os.environ,
                {"SLURPY_TOKEN": "test-token", "LOG_LEVEL": "INFO"},
                clear=False,
            ),
            patch.object(slurpybot, "GENERAL_ID", 123),
            patch.object(slurpybot.webserver, "keep_alive") as keep_alive,
            patch.object(slurpybot.client, "run") as client_run,
        ):
            slurpybot.run_bot()

        keep_alive.assert_called_once_with()
        client_run.assert_called_once_with("test-token")
        self.assertNotIn("fantasy", sys.modules)

    def test_render_port_is_used_by_health_server(self):
        import webserver

        with (
            patch.dict(os.environ, {"PORT": "12345"}, clear=False),
            patch.object(webserver.app, "run") as app_run,
        ):
            webserver.run()

        app_run.assert_called_once_with(host="0.0.0.0", port=12345)


class FantasyCommandTests(unittest.IsolatedAsyncioTestCase):
    async def test_fantasy_command_remains_registered_while_disabled(self):
        slurpybot = import_slurpy_without_optional_configuration()
        fantasy_command = slurpybot.client.get_command("fantasy")

        class Channel:
            id = 123

        class Context:
            channel = Channel()

            def __init__(self):
                self.messages = []

            async def send(self, message):
                self.messages.append(message)

        context = Context()
        await fantasy_command.callback(context)

        self.assertEqual(
            context.messages,
            ["fantasy's benched rn while yahoo sorts itself out"],
        )


if __name__ == "__main__":
    unittest.main()
