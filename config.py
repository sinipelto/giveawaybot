base_url = "https://www.gamerpower.com/api/giveaways" # The base address for the Gamerpower API

ga_type = "game" # Parameter for filtering the giveaway type (game/loot/beta)
ga_sort = "value" # Parameter for sorting the giveaways (date/value/popularity)

param_type = "type=" + ga_type # Complete url parameter with key
param_sort = "sort-by=" + ga_sort # Complete url parameter with key

min_value = 9.99 # The minimum value of the giveaway to qualify
max_value = None # Maximum value for giveaway to qualify - None means no limit

db_file = "./games.db" # Path for the local databsae for memorizing the already processed giveaways
table_name = "games" # Table name for the databse

recipient_file = "./recipients.txt" # Path for the file containing all the email recipients

sender_name = "Giveaway Bot" # Name of the sender appearing in the email
sender_email = "some.account@gmail.com" # The email origin address. Usually the same as the SMTP user.

email_title = "[Giveaways] New giveaways spotted!" # Title for the email

smtp_host = "google.com" # Domain for the STMP server (e.g. GMail, Outlook, your own SMTP server, etc.)
smtp_username = "some.account@gmail.com" # Username for the mail account in the SMTP server
smtp_password = "ExamplePassword123" # Password for the mail account to be able to authenticate
