import os
import argparse
import json
import requests
import app_constants as APP_CONSTANTS
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

parser = argparse.ArgumentParser(
    description='Backup Slack channel, conversation, Users, and direct messages.')

parser.add_argument('-t', '--token', dest='token',required=True,
                    help='Slack api Access token')

parser.add_argument('-od', '--outDir', dest='outDir',required=False,default='./output',
                    help='Output directory to store JSON backup files.')

args = parser.parse_args()

token = args.token
auth_headers = {'Authorization': 'Bearer ' + token}
outDir = args.outDir

client = WebClient(token=token)

def getOutputPath(relativePath):
    return outDir+relativePath


def parseTemplatedFileName(template, *args):
    return template.format(*args)


def readPostManCollectionJson():
    with open('slack-postman.json') as file:
        jsonObj = json.load(file)
        return jsonObj


def readRequestJsonFile():
    with open('requests.json') as file:
        jsonObj = json.load(file)
        return jsonObj


def writeJSONFile(jsonObj, filePath):
    outputPath = getOutputPath(filePath)
    dirPath = os.path.dirname(outputPath)
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    with open(outputPath, 'w+') as file:
        json.dump(jsonObj, file, indent=True)

def getUsers():
    response = client.users_list()
    return response['members']

def getChannels():
    response = client.conversations_list(types='public_channel,private_channel')
    return response['channels']

def getGroups():
    response = client.conversations_list(types='mpim')
    return response['channels']

def getOneToOneConversations():
    response = client.conversations_list(types='im')
    return response['channels']

def getConversationHistory(channelId):
    params = { 'channel': channelId, 'count': 1000}
    msgs = []
    while True:
        response = client.conversations_history(**params)
        msgs.extend(response['messages'])
        if not response['has_more']:
            break

        params['latest'] = msgs[-1]['ts']
    return msgs


def run():
    channels = getChannels()
    writeJSONFile(channels, APP_CONSTANTS.CHANNEL_LIST_FILE)

    for channel in channels:
        channelId = channel['id']
        channelName = channel['name']
        channelHistory = getConversationHistory(channelId)
        if channel['is_private']:
            template = APP_CONSTANTS.PRIVATE_CHANNEL_HISTORY_FILE
        else:
            template = APP_CONSTANTS.CHANNEL_HISTORY_FILE
        channelHistoryFilename = parseTemplatedFileName(template, channelName)
        writeJSONFile(channelHistory, channelHistoryFilename)

    groups = getGroups()
    writeJSONFile(groups, APP_CONSTANTS.GROUP_LIST_FILE)

    for group in groups:
        groupId = group['id']
        groupName = group['name']

        groupHistory = getConversationHistory(groupId)

        groupHistoryFilename = parseTemplatedFileName(
            APP_CONSTANTS.GROUP_HISTORY_FILE, groupName)
        writeJSONFile(groupHistory, groupHistoryFilename)

    users = getUsers()
    writeJSONFile(users, APP_CONSTANTS.USER_LIST_FILE)

    userIdToNameDict = {user['id']: user['name'] for user in users}

    # Get one to one conversation list
    oneToOneConversations = getOneToOneConversations()
    writeJSONFile(oneToOneConversations,
                  APP_CONSTANTS.ONE_TO_ONE_CONVERSATION_LIST_FILE)

    for conversation in oneToOneConversations:
        conversationId = conversation['id']
        userId = conversation['user']
        userName = userIdToNameDict[userId]

        conversationHistory = getConversationHistory(conversationId)
        conversationHistoryFilename = parseTemplatedFileName(
            APP_CONSTANTS.ONE_TO_ONE_CONVERSATION_HISTORY_FILE, userName, userId)
        writeJSONFile(conversationHistory, conversationHistoryFilename)

if __name__ == '__main__':
    run()
