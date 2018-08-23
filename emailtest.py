import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(smallest, largest, averageda):
    # me == my email address
    # you == recipient's email address
    me = "Austin.Lester@ftsi.com"
    you = "austin.a.lester@gmail.com"

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "KCF Summary"
    msg['From'] = me
    msg['To'] = you

    # Create the body of the message (a plain-text and an HTML version).

    html = """\
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>KCF Summary</title>
        <link rel="stylesheet" href="styles.css">
        <style type="text/css">
            .blue   {
                font-size: 12pt;
                color: blue;
                text-decoration: underline;
                font-weight: bold;
            }
    
            .boldunder   {
                font-size: 11pt;
                text-decoration: underline;
                font-weight: bold;
            }
    
            .greensig {
                font-family: Arial;
                font-size: 8pt;
                font-weight: bold;
                color: green;
            }
    
            .signature {
                font-family: Arial;
                font-size: 8pt;
            }
            
        </style>
    </head>
    
    <body>
        <p>
            <h1 class="blue">Blue</h1>
            <h2 class="boldunder">24 Hour Summary:</h2>
        </p>
    
        <p>
            <span class="bold">DA Score:</span>
            <span>""" + str(averageda) + """</span>
        </p>
    
        <p>
            <span class="boldunder">Highest Trending Pumps:</span><br />
            <span>""" + str(largest[0]) + """</span><br />
            <span>""" + str(largest[1]) + """</span><br />
            <span>""" + str(largest[2]) + """</span><br />
        </p>
    
        <p>
            <span class="boldunder">Lowest Trending Pumps:</span><br />
            <span>""" + str(smallest[0]) + """</span><br />
            <span>""" + str(smallest[1]) + """</span><br />
            <span>""" + str(smallest[2]) + """</span><br />
        </p>
    
        <b><p style="font-size: 10pt">
            Thank You,
        </p></b>
        <span class="greensig">Austin Lester</span><br />
        <span class="signature">Projects Coordinator</span><br />
        <b><span style="font-size: 8pt">FTS International</span></b><br />
        <span class="signature">986 S. Maurice St.</span>
        <span class="signature">Projects Coordinator</span><br />
        <span class="signature">Odessa, TX 79763</span><br />
        <b><span style="font-size: 8pt">Office: </span></b>
        <span class="signature">432.368.8100</span><br />
        <b><span style="font-size: 8pt">Mobile: </span></b>
        <span class="signature">432-202-0470</span><br />
        <a href="mailto:Austin.Lester@ftsi.com">
            <span style="font-size: 10pt">Austin.Lester@ftsi.com</span>
        </a>
    
    </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part2)
    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp-mail.outlook.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login('austin.lester@ftsi.com', 'Welcome6')
    mail.sendmail(me, you, msg.as_string())
