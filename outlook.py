import win32com.client as win32
import csv
import datetime


def send_email(smallest, largest, averageda, color, tags, top_change_list=[], top_percent_list=[]):
    try:
        if top_change_list:
            top_change_html = """<p>
                <span class="boldunder">Highest 24 Hr Change:</span><br />
                <span>""" + str(top_change_list[0]) + ' - ' + str(top_percent_list[0]) + """%</span><br />
                <span>""" + str(top_change_list[1]) + ' - ' + str(top_percent_list[1]) + """%</span><br />
                <span>""" + str(top_change_list[2]) + ' - ' + str(top_percent_list[2]) + """%</span><br />
            </p>"""
        else:
            top_change_html = ''
    except IndexError:
        top_change_html = ''

    with open('emails.csv') as csvfile:
        emailreader = csv.reader(csvfile)
        labels = ['blueto', 'bluecc', 'onyxto', 'onyxcc',
                  'redto', 'redcc', 'greento', 'greencc',
                  'silverto', 'silvercc', 'goldto', 'goldcc',
                  'purpleto', 'purplecc'
                  ]
        emails = []
        for row in emailreader:
            emails.append(row)
        emaildict = dict(zip(labels, emails))

    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.To = str(emaildict[color.lower() + 'to']).strip("[]")
    mail.cc = str(emaildict[color.lower() + 'cc']).strip("[]")
    mail.subject = "KCF Observations - " + color.upper() + ' - ' + datetime.date.today().strftime('%m.%d.%y')
    mail.HtmlBody = """\
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

            .red   {
                font-size: 12pt;
                color: red;
                text-decoration: underline;
                font-weight: bold;
            }

            .green   {
                font-size: 12pt;
                color: green;
                text-decoration: underline;
                font-weight: bold;
            }

            .purple   {
                font-size: 12pt;
                color: purple;
                text-decoration: underline;
                font-weight: bold;
            }

            .gold   {
                font-size: 12pt;
                color: gold;
                text-decoration: underline;
                font-weight: bold;
            }

            .silver   {
                font-size: 12pt;
                color: silver;
                text-decoration: underline;
                font-weight: bold;
            }

            .onyx   {
                font-size: 12pt;
                color: black;
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
            <h1 class=""" + color.lower() + """>""" + color.title() + """</h1>
            <h2 class="boldunder">24 Hour Summary:</h2>
        </p>

        <p>
            <span class="bold">DA Score:</span>
            <span>""" + str(averageda) + """</span>
        </p>""" + top_change_html + """<p>
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
        <p class="boldunder">/""" + str(tags) + """ required tags</p>
        <b><p style="font-size: 10pt">
            Thank You,
        </p></b>
        <span class="greensig">Austin Lester</span><br />
        <span class="signature">Projects Coordinator</span><br />
        <b><span style="font-size: 8pt">FTS International</span></b><br />
        <span class="signature">986 S. Maurice St.</span>
        <span class="signature">Odessa, TX 79763</span><br />
        <b><span style="font-size: 8pt">Office: </span></b>
        <span class="signature">432.368.8100</span><br />
        <b><span style="font-size: 8pt">Mobile: </span></b>
        <span class="signature">432-202-0470</span><br />
        <a href="mailto:Austin.Lester@ftsi.com">
            <span style="font-size: 10pt">Austin.Lester@ftsi.com</span>
        </a>

    </body>
    </html>"""
    mail.display(False)
