import os
import json
import requests
import web_constants as WEB_CONSTANTS
import app_constants as APP_CONSTANTS

token = 'xoxp-8910951619-266447157124-435172273238-deb696c50827fd7d5d9891e50e05e47b'
outDir = './output'

def getOutputPath(relativePath):
    return outDir+relativePath

def parseTemplatedFileName(template,args):
    return template.format(args)

def readPostManCollectionJson():
    with open('slack-postman.json') as file:
        jsonObj = json.load(file)
        return jsonObj


def readRequestJsonFile():
    with open('requests.json') as file:
        jsonObj = json.load(file)
        return jsonObj



def writeJSONFile(jsonObj,filePath):
    outputPath = getOutputPath(filePath)
    dirPath = os.path.dirname(outputPath)
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    with open(outputPath, 'w+') as file:
        json.dump(jsonObj, file)

def getChannels():
    response = requests.get(WEB_CONSTANTS.CHANNEL_LIST,params={'token':token})
    return response.json()['channels']

def getChannelHistory(channelId):
    response = requests.get(WEB_CONSTANTS.CHANNEL_HISTORY,params={'token':token,'channel':channelId})
    return response.json()

def run():
    channels = getChannels()
    writeJSONFile(channels,APP_CONSTANTS.CHANNEL_LIST_FILE)

    for channel in channels:
        channelId = channel['id']
        channelName = channel['name']
        channelHistory = getChannelHistory(channelId)
        channelHistoryFilename = parseTemplatedFileName(APP_CONSTANTS.CHANNEL_HISTORY_FILE,channelName)
        writeJSONFile(channelHistory,channelHistoryFilename)


if __name__ == '__main__':
    run()
