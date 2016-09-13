import os
import time
import json
import multipart
import pyc3
from lxml import etree
from slackclient import SlackClient
from slacker import Slacker

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = ["bar","line"]

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slack_slacker = Slacker(os.environ.get('SLACK_BOT_TOKEN'))

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    #response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
    #           "* command with numbers, delimited by spaces."

    '''Splitting chart title, names and values'''
    temp = command.split()
    chart = temp[0]
    #if 'line' in chart:
    #	values = list()
    #	values.append(str(title))
    #	for entity in temp[2:]:
    #		values.append(int(entity))
    #	create_chart(chart,values)
    if chart in EXAMPLE_COMMAND:
	values = list()
	for entity in temp[1:]:
		placeholder_list = list()
		entity = entity.split(':')
		print "entity", entity
		x_axis = entity[0]
		y_axis = entity[1]
		y_axis = y_axis.split(',')
		print "nos", y_axis
		placeholder_list.append(str(x_axis))
		for number in y_axis:
			placeholder_list.append(int(number))
		values.append(placeholder_list)
		print values
    	create_chart(chart,values)

    #if command.startswith(EXAMPLE_COMMAND):
    #    response = "Sure...write some more code then I can do that!"
    #	json_string = [{'text':response}]
    #need to encode json to send as attachment using WEB API
    #json_string = json.dumps(json_string)
    #slack_client.api_call("chat.postMessage", channel=channel,
    #                      text=response, attachments=json_string, as_user=True)
    
    a = slack_slacker.files.upload('index.html',title='Dashboard',channels=channel)

def create_chart(chart, values):
	message = """<html>
  <head>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.11/c3.min.css" rel="stylesheet" type="text/css">
  </head>
  <body>
    <h2 style="align:center;">"""+str(chart)+"""chart</h2>
    <div id="chart1" style="height:200px;"></div>
    <div class="chart2" style="height:200px;"></div>
    <div class="chart3" style="height:200px;"></div>

    <script src="https://d3js.org/d3.v3.js" charset="utf-8"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.11/c3.min.js"></script>
    <script>
      var chart1 = c3.generate({
        bindto: '#chart1',
        data: {
          columns: [
		["""+str(values).strip('[]')+"""]
		],
		type: '"""+str(chart)+"""' 
        }
      });
      var chart2 = c3.generate({
        bindto: '.chart2',
        data: {
          columns: [
            ['data1', 30, 200, 100, 400, 150, 250]
          ]
        }
      });
      var chart3 = c3.generate({
        bindto: document.getElementsByClassName('chart3')[0],
        data: {
          columns: [
            ['data1', 30, 200, 100, 400, 150, 250]
          ]
        }
      });
    </script>
  </body>
</html>"""
	f = open('index.html','w')
	f.write(message)
	f.close()

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
		# return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
