class Settings:
    # The prefix used for executing all commands
    PREFIX = "./"
    DELETE_CMD = True               # Deletes the original message executing the command

    # Message Spamming:
    SPAM_CNT = 10                   # Number of messages to spam
    SPAM_DELAY = 0.5                # Delay in between messages
    SPAM_MSG = "SPAM"               # default spam message

    # Invite Spamming ()
    INVITE_DUPLICATES = False       # Change this to true if you want to be incredibly annoying
    INVITE_DB = "invites.p"         # location to store a pickled set of user IDs
    INVITE_CONNS = 1               # number of concurrent private messages
    INVITE_DELAY = 60 * 5           # Discord allows 10 per 5 minutes.
    INVITE_LINK = "https://discord.gg/F9uj2Dd"                # default invite link
    #INVITE_MSG  = "hey {username} saw u on {servername} just wondering if you wanna join my server: {link}"
    INVITE_MSG = "{link}"

    # Purging Messages
    PURGE_CNT = 10                  # default number of messages to purge (if not user-provided)
