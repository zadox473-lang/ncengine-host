from aiogram.fsm.state import State, StatesGroup


class UserSettings(StatesGroup):

    waiting_for_name = State()

    waiting_for_owner = State()


class HostingStates(StatesGroup):

    waiting_for_tokens = State()


class SupportStates(StatesGroup):

    waiting_for_message = State()


class BroadcastStates(StatesGroup):

    waiting_for_broadcast = State()


class OwnerStates(StatesGroup):

    waiting_for_user = State()

    waiting_for_reply = State()
