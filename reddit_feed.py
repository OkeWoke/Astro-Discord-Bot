#!/usr/bin/env python3

"""
Created on Sun Mar 23 10:49:07 2023

@author: BooleanCube
"""

import json.decoder
from discord_webhook import DiscordWebhook, DiscordEmbed
import requests
import database
import time
from html import unescape


print("Starting Reddit Listener...")

cache = set()
conn = database.get_connection()
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS posts (name)")
rows = c.execute('SELECT * FROM posts')
for row in rows:
    cache.add(row[0])
conn.commit()
conn.close()

subreddits = ["astrophotography"]
webhook_url = "YOUR_WEBHOOK_URL_HERE"

while 1:
    try:
        req = requests.get(f'https://www.reddit.com/r/{"+".join(subreddits)}/new/.json', headers={
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "User-Agent": "discord-feed-bot"
        })
    except requests.exceptions.RequestException as e:
        time.sleep(300)
        continue

    try:
        posts = req.json()['data']['children'][::-1]  # Returns 25 newest posts
    except json.decoder.JSONDecodeError as e:
        print(req.json())
        time.sleep(300)
        continue

    for post in posts:
        if post['data']['hidden'] or post['data']['removed_by'] is not None:
            continue

        if post['data']['name'] not in cache:
            webhook = DiscordWebhook(url=webhook_url)
            permalink = f"https://www.reddit.com{post['data']['permalink']}"
            color = post['data']['link_flair_background_color']
            color = "1C1B19" if color == "" or color is None else color[1:]
            subreddit = post['data']['subreddit_name_prefixed']
            subreddit_url = "https://www.reddit.com/" + subreddit

            if post['data']['thumbnail'] == 'self':
                embed = DiscordEmbed(title=unescape(post['data']['title']), url=permalink,
                                     description=unescape(post['data']['selftext']))
                embed.set_author(subreddit, url=subreddit_url)
                embed.set_footer(text=f"Posted by u/{post['data']['author']}")
                embed.set_timestamp(timestamp=post['data']['created'])
                embed.set_color(color)
            elif post['data']['is_video']:
                embed = DiscordEmbed(title=unescape(post['data']['title']), url=permalink)
                embed.set_author(subreddit, url=subreddit_url)
                embed.set_image(url=post['data']['thumbnail'])
                embed.set_footer(text=f"Video posted by u/{post['data']['author']}")
                embed.set_timestamp(timestamp=post['data']['created'])
                embed.set_color(color)
            else:
                embed = DiscordEmbed(title=unescape(post['data']['title']), url=permalink)
                embed.set_author(subreddit, url=subreddit_url)
                url = post['data']['url'].lower()
                if url[url.rfind("."):] in [".jpg",".png",".gif",".webp",".jpeg"]:
                    embed.set_image(url=url)
                else:
                    embed.set_image(url=post['data']['thumbnail'])
                embed.set_footer(text=f"Image posted by u/{post['data']['author']}")
                embed.set_timestamp(timestamp=post['data']['created'])
                embed.set_color(color)


            webhook.add_embed(embed)
            webhook.execute()
            time.sleep(5)  # to prevent Discord webhook rate limiting

            cache.add(post['data']['name'])

    # update posts table in the database
    for post in list(cache)[-25:]:
        conn = database.get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO posts VALUES (?)', (post,))
        conn.commit()
        conn.close()

    time.sleep(300) # Wait 5 minutes until requesting again