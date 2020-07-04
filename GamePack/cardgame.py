import discord
import random
import asyncio
import threading
from discord.ext import commands
from Settings.MyUtility import get_prefix
from Settings.StaticData import card_deck_dict, card_deck_list

WHITE = 0xfffffe

class Cards(commands.Cog):

    def __init__(self, bot:commands.Bot):
        self.bot = bot

    # Listener Area

    @commands.Cog.listener()
    async def on_ready(self):
        print("Card Game Ready!")

    # Checker Area

    @staticmethod
    def card_to_int(game: str, on_hand: list) -> list:
        holder: list = []
        if game.lower() == "blackjack":
            A_count: int = 0
            for card in on_hand:
                if "A" in card:
                    holder.append(11)
                    A_count += 1
                elif ord(card[0]) >= 48 and ord(card[0]) < 58 and len(card) == 2:
                    holder.append(ord(card[0]) - 48)
                else:
                    holder.append(10)
            while sum(holder) > 21 and A_count > 0:
                holder.remove(11)
                holder.append(1)
                A_count -= 1
            return holder
        else:
            return on_hand

    def compare_current(self, b: list, p: list):
        bc: int = sum(self.card_to_int("blackjack", b))
        pc: int = sum(self.card_to_int("blackjack", p))
        if bc > pc:
            return False
        elif bc < pc:
            return True
        else:
            if max(bc) > max(pc):
                return False
            elif max(bc) < max(pc):
                return True
            else:
                range_symbol: list = ["♢", "♧", "♡", "♤"]
                max_p: int = 0
                max_b: int = 0
                for ib in b:
                    symbol_index: int = range_symbol.index(ib[1])
                    if max_b < symbol_index:
                        max_b = symbol_index
                for jp in p:
                    symbol_index: int = range_symbol.index(ib[1])
                    if max_b < symbol_index:
                        max_b = symbol_index
                if max_b <= max_p:
                    return True
                else:
                    return False

    # Command Area

    @commands.command(name= "blackjack", pass_context= True)
    async def _blackjack(self, ctx: commands.Context, *args):
        if len(args) == 0:
            await self.blackjack_help(ctx.channel)
        else:
            # Help
            if args[0].lower() == "-h" or args[0].lower() == "help":
                await self.blackjack_help(ctx.channel)

            # Single player
            elif args[0].lower() == "play" or args[0].lower() == "bot":
                await self.blackjack_vs_bot(ctx.channel, ctx.author)

            # Challenge player
            elif len(args) == 1:
                pass
            
    # Gameplay

    async def blackjack_vs_bot(self, channel: discord.TextChannel, player: discord.User):
        # Inner Function
        def description_maker(dh: list) -> str:
            desc_holder: str = "```"
            for x in range(len(dh)):
                if x == len(dh) - 1:
                    desc_holder += f"{dh[x]}"
                else:
                    desc_holder += f"{dh[x]} "
            return desc_holder + "```"

        # Initialize Game
        current_deck: list = card_deck_list

        bot_hand: list = []
        player_hand: list = []

        for i in range(2):
            get_card: str = random.choice(current_deck)
            current_deck.remove(get_card)
            bot_hand.append(get_card)

            get_card: str = random.choice(current_deck)
            current_deck.remove(get_card)
            player_hand.append(get_card)

        bot_current: list = self.card_to_int("blackjack", bot_hand)
        player_current: list = self.card_to_int("blackjack", player_hand)

        desc: str = f"{self.bot.user.name} | __*Sum : Unk*__\n```{bot_hand[0]} XX```\n{player.name} | __*Sum : {str(sum(player_current))}*__\n{description_maker(player_hand)}"
        board_embed: discord.Embed = discord.Embed(
            title= "🂡 Blackjack | VS Bot",
            description= desc,
            colour= discord.Colour(WHITE)
            )
        board_embed.set_footer(text= "Send 'DRAW' or 'SET'")
        handler_msg: discord.Message = await channel.send(embed= board_embed)

        # On Play
        try:
            menus: list = ["DRAW", "draw", "SET", "set"]
            while sum(player_current) <= 21:
                replied: discord.Message = await self.bot.wait_for(
                    event= "message",
                    check= lambda message: True if message.content in menus and player == message.author else False,
                    timeout= 30.0
                    )
                if replied.content.lower() == "draw":
                    get_card: str = random.choice(current_deck)
                    current_deck.remove(get_card)
                    player_hand.append(get_card)

                    # Overwrite Current Embed
                    player_current = self.card_to_int("blackjack", player_hand)
                    desc: str = f"{self.bot.user.name} | __*Sum : Unk*__\n```{bot_hand[0]} XX```\n{player.name} | __*Sum : {str(sum(player_current))}*__\n{description_maker(player_hand)}"
                    board_embed: discord.Embed = discord.Embed(
                        title= "🂡 Blackjack | VS Bot",
                        description= desc,
                        colour= discord.Colour(WHITE)
                        )
                    board_embed.set_footer(text = "Send 'DRAW' or 'SET'")
                    await replied.delete()
                    await handler_msg.edit(embed = board_embed)

                elif replied.content.lower() == "set":
                    await replied.delete()
                    break

            # Check Win-Lose Condition
            player_win: bool = compare_current(bot_hand, player_hand)
            desc: str = f"{self.bot.user.name} | __*Sum : {str(sum(bot_current))}*__\n{description_maker(bot_hand)}\n{player.name} | __*Sum : {str(sum(player_current))}*__\n{description_maker(player_hand)}"
            board_embed: discord.Embed = discord.Embed(
                title= "🂡 Blackjack | VS Bot",
                description= desc,
                colour= discord.Colour(WHITE)
                )
            if sum(player_current) > 21:
                board_embed.set_footer(text=f"💥 BUSTS! Better Luck Next Time.")
                await handler_msg.edit(embed = board_embed)
            elif player_win is True:
                board_embed.set_footer(text=f"👍 You Win! Congratulation")
                await handler_msg.edit(embed = board_embed)
            else:
                board_embed.set_footer(text=f"👎 You Lose, Better Luck Next Time.")
                await handler_msg.edit(embed = board_embed)
                
        except asyncio.TimeoutError:
            board_embed = discord.Embed(
                title="Game Forfeited, where have you been?",
                colour = discord.Colour(WHITE)
            )
            await handler_msg.edit(embed = board_embed)

    async def blackjack_vs_player(self, channel: discord.TextChannel, p1: discord.User, p2: discord.User):
        pass

    # Others

    @staticmethod
    async def blackjack_help(self, channel: discord.TextChannel):
        pref: str = get_prefix(channel.guild.id)
        emb = discord.Embed(
            title= "🂡 Blackjack | Help",
            colour= discord.Colour(WHITE)
            )
        emb.add_field(
            name= "Command :",
            value= f"> `{pref}.blackjack <option>`",
            inline= False
            )
        emb.add_field(
            name= "Options :",
            value= "`[@]` - Challange tagged person\n"
                "`bot`|`play` - Challange bot\n"
                "`-h`|`help` - This help menu",
            inline= False
            )
        emb.set_footer(text= f"Example Command : {pref}blackjack play")
        await channel.send(embed= emb)

def setup(bot:commands.Bot):
    bot.add_cog(Cards(bot))