import os
import argparse
import json
import requests
import web_constants as WEB_CONSTANTS
import app_constants as APP_CONSTANTS

parser = argparse.ArgumentParser(
    description='Backup Slack channel, conversation, Users, and direct messages.')

parser.add_argument('-t', '--token', dest='token',required=True,
                    help='Slack api Access token')

parser.add_argument('-od', '--outDir', dest='outDir',required=False,default='./output',
                    help='Output directory to store JSON backup files.')

args = parser.parse_args()

token = args.token
outDir = args.outDir


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


def getChannels():
    response = requests.get(WEB_CONSTANTS.CHANNEL_LIST,
                            params={'token': token})
    return response.json()['channels']


def getChannelHistory(channelId):
    response = requests.get(WEB_CONSTANTS.CHANNEL_HISTORY, params={
                            'token': token, 'channel': channelId})
    return response.json()


def getGroups():
    response = requests.get(WEB_CONSTANTS.GROUP_LIST, params={'token': token})
    return response.json()['groups']


def getGroupHistory(groupId):
    response = requests.get(WEB_CONSTANTS.GROUP_HISTORY, params={
                            'token': token, 'channel': groupId})
    return response.json()


def getOneToOneConversations():
    # im for one to one conv.
    response = requests.get(WEB_CONSTANTS.CONVERSATION_LIST, params={
                            'token': token, 'types': 'im'})
    return response.json()['channels']


def getUsers():
    # im for one to one conv.
    response = requests.get(WEB_CONSTANTS.USERS_LIST, params={'token': token})
    return response.json()['members']


def getConversationHistory(conversationId):
    response = requests.get(WEB_CONSTANTS.CONVERSATION_HISTORY, params={
                            'token': token, 'channel': conversationId})
    return response.json()


def run():
    channels = getChannels()
    writeJSONFile(channels, APP_CONSTANTS.CHANNEL_LIST_FILE)

    for channel in channels:
        channelId = channel['id']
        channelName = channel['name']
        channelHistory = getChannelHistory(channelId)
        channelHistoryFilename = parseTemplatedFileName(
            APP_CONSTANTS.CHANNEL_HISTORY_FILE, channelName)
        writeJSONFile(channelHistory, channelHistoryFilename)

    groups = getGroups()
    writeJSONFile(groups, APP_CONSTANTS.GROUP_LIST_FILE)

    for group in groups:
        groupId = group['id']
        groupName = group['name']

        groupHistory = getGroupHistory(groupId)

        groupHistoryFilename = parseTemplatedFileName(
            APP_CONSTANTS.GROUP_HISTORY_FILE, groupName)
        writeJSONFile(groupHistory, groupHistoryFilename)

    users = getUsers()
    writeJSONFile(users, APP_CONSTANTS.USER_LIST_FILE)

    userIdToNameDict = {user['id']: user['name'] for user in users}

    # Getting one to one conversation list
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
