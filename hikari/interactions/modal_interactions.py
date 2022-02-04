# -*- coding: utf-8 -*-
# cython: language_level=3
# Copyright (c) 2020 Nekokatt
# Copyright (c) 2021 davfsa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Models and enums used for Discord's Modals interaction flow."""

from __future__ import annotations

__all__: typing.List[str] = [
    "ModalResponseTypesT",
    "ModalInteraction",
    "ModalInteractionTextInput",
    "ModalInteraction",
]

import typing

import attr

from hikari import messages
from hikari import snowflakes
from hikari.interactions import base_interactions
from hikari.internal import attr_extensions

if typing.TYPE_CHECKING:
    from hikari import users as _users
    from hikari.api import special_endpoints

ModalResponseTypesT = typing.Literal[
    base_interactions.ResponseType.MESSAGE_CREATE, 4, base_interactions.ResponseType.DEFERRED_MESSAGE_CREATE, 5
]
"""Type-hint of the response types which are valid for a modal interaction.

The following types are valid for this:

* `hikari.interactions.base_interactions.ResponseType.MESSAGE_CREATE`/`4`
* `hikari.interactions.base_interactions.ResponseType.DEFERRED_MESSAGE_CREATE`/`5`
"""


@attr.define(kw_only=True, weakref_slot=False)
class ModalInteractionTextInput(messages.PartialComponent):
    """A text input component in a modal interaction."""

    custom_id: str = attr.field(repr=True)
    """Developer set custom ID used for identifying interactions with this modal."""

    value: str = attr.field(repr=True)
    """Value provided for this text input."""


class ModalInteractionActionRow(typing.Protocol):
    """An action row with only partial text inputs.

    Meant purely for use with ModalInteraction.
    """

    components: typing.List[ModalInteractionTextInput]


@attr_extensions.with_copy
@attr.define(hash=True, kw_only=True, weakref_slot=False)
class ModalInteraction(base_interactions.MessageResponseMixin[ModalResponseTypesT]):
    """Represents a modal interaction on Discord."""

    channel_id: snowflakes.Snowflake = attr.field(eq=False, hash=False, repr=True)
    """ID of the channel this modal interaction event was triggered in."""

    custom_id: str = attr.field(eq=False, hash=False, repr=True)
    """The custom id of the modal."""

    guild_id: typing.Optional[snowflakes.Snowflake] = attr.field(eq=False, hash=False, repr=True)
    """ID of the guild this modal interaction event was triggered in.

    This will be `builtins.None` for modal interactions triggered in DMs.
    """

    guild_locale: typing.Optional[str] = attr.field(eq=False, hash=False, repr=True)
    """The preferred language of the guild this modal interaction was triggered in.

    This will be `builtins.None` for modal interactions triggered in DMs.

    !!! note
        This value can usually only be changed if `COMMUNITY` is in `hikari.guilds.Guild.features`
        for the guild and will otherwise default to `en-US`.
    """

    message: typing.Optional[messages.Message] = attr.field(eq=False, repr=False)
    """The message whose component triggered the modal.

    This will be None if the modal was a response to a command.
    """

    member: typing.Optional[base_interactions.InteractionMember] = attr.field(eq=False, hash=False, repr=True)
    """The member who triggered this modal interaction.

    This will be `builtins.None` for modal interactions triggered in DMs.

    !!! note
        This member object comes with the extra field `permissions` which
        contains the member's permissions in the current channel.
    """

    user: _users.User = attr.field(eq=False, hash=False, repr=True)
    """The user who triggered this modal interaction."""

    locale: str = attr.field(eq=False, hash=False, repr=True)
    """The selected language of the user who triggered this Modal interaction."""

    components: typing.Sequence[ModalInteractionActionRow] = attr.field(eq=False, hash=False, repr=True)
    """Components in the modal."""

    def build_response(self) -> special_endpoints.InteractionMessageBuilder:
        """Get a message response builder for use in the REST server flow.

        !!! note
            For interactions received over the gateway
            `ModalInteraction.create_initial_response` should be used to set
            the interaction response message.

        Examples
        --------
        ```py
        async def handle_modal_interaction(interaction: ModalInteraction) -> InteractionMessageBuilder:
            return (
                interaction
                .build_response()
                .add_embed(Embed(description="Hi there"))
                .set_content("Konnichiwa")
            )
        ```

        Returns
        -------
        hikari.api.special_endpoints.InteractionMessageBuilder
            Interaction message response builder object.
        """
        return self.app.rest.interaction_message_builder(base_interactions.ResponseType.MESSAGE_CREATE)

    def build_deferred_response(self) -> special_endpoints.InteractionDeferredBuilder:
        """Get a deferred message response builder for use in the REST server flow.

        !!! note
            For interactions received over the gateway
            `ModalInteraction.create_initial_response` should be used to set
            the interaction response message.

        !!! note
            Unlike `hikari.api.special_endpoints.InteractionMessageBuilder`,
            the result of this call can be returned as is without any modifications
            being made to it.

        Returns
        -------
        hikari.api.special_endpoints.InteractionDeferredBuilder
            Deferred interaction message response builder object.
        """
        return self.app.rest.interaction_deferred_builder(base_interactions.ResponseType.DEFERRED_MESSAGE_CREATE)
