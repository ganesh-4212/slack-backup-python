import os
import click
import json
import requests
import web_constants as WEB_CONSTANTS
import app_constants as APP_CONSTANTS


@click.command()
@click.option('--out', default='./output')
@click.argument('token', type=click.types.STRING)
def cli(out, token):
    run(token, out)


def getOutputPath(relativePath, outDir):
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


def writeJSONFile(jsonObj, filePath, outDir):
    outputPath = getOutputPath(filePath, outDir)
    dirPath = os.path.dirname(outputPath)
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

    with open(outputPath, 'w+') as file:
        json.dump(jsonObj, file, indent=True)


def getChannels(token):
    response = requests.get(WEB_CONSTANTS.CHANNEL_LIST,
                            params={'token': token})
    return response.json()['channels']


def getChannelHistory(channelId, token):
    response = requests.get(WEB_CONSTANTS.CHANNEL_HISTORY, params={
                            'token': token, 'channel': channelId})
    return response.json()


def getGroups(token):
    response = requests.get(WEB_CONSTANTS.GROUP_LIST, params={'token': token})
    return response.json()['groups']


def getGroupHistory(groupId, token):
    response = requests.get(WEB_CONSTANTS.GROUP_HISTORY, params={
                            'token': token, 'channel': groupId})
    return response.json()


def getOneToOneConversations(token):
    # im for one to one conv.
    response = requests.get(WEB_CONSTANTS.CONVERSATION_LIST, params={
                            'token': token, 'types': 'im'})
    return response.json()['channels']


def getUsers(token):
    # im for one to one conv.
    response = requests.get(WEB_CONSTANTS.USERS_LIST, params={'token': token})
    return response.json()['members']


def getConversationHistory(conversationId, token):
    response = requests.get(WEB_CONSTANTS.CONVERSATION_HISTORY, params={
                            'token': token, 'channel': conversationId})
    return response.json()


def run(token, outDir):
    channels = getChannels(token)
    writeJSONFile(channels, APP_CONSTANTS.CHANNEL_LIST_FILE, outDir)

    for channel in channels:
        channelId = channel['id']
        channelName = channel['name']
        channelHistory = getChannelHistory(channelId, token)
        channelHistoryFilename = parseTemplatedFileName(
            APP_CONSTANTS.CHANNEL_HISTORY_FILE, channelName)
        writeJSONFile(channelHistory, channelHistoryFilename, outDir)

    groups = getGroups(token)
    writeJSONFile(groups, APP_CONSTANTS.GROUP_LIST_FILE, outDir)

    for group in groups:
        groupId = group['id']
        groupName = group['name']

        groupHistory = getGroupHistory(groupId, token)

        groupHistoryFilename = parseTemplatedFileName(
            APP_CONSTANTS.GROUP_HISTORY_FILE, groupName)
        writeJSONFile(groupHistory, groupHistoryFilename, outDir)

    users = getUsers(token)
    writeJSONFile(users, APP_CONSTANTS.USER_LIST_FILE, outDir)

    userIdToNameDict = {user['id']: user['name'] for user in users}

    # Getting one to one conversation list
    oneToOneConversations = getOneToOneConversations(token)
    writeJSONFile(oneToOneConversations,
                  APP_CONSTANTS.ONE_TO_ONE_CONVERSATION_LIST_FILE, outDir)

    for conversation in oneToOneConversations:
        conversationId = conversation['id']
        userId = conversation['user']
        userName = userIdToNameDict[userId]

        conversationHistory = getConversationHistory(conversationId, token)
        conversationHistoryFilename = parseTemplatedFileName(
            APP_CONSTANTS.ONE_TO_ONE_CONVERSATION_HISTORY_FILE, userName, userId)
        writeJSONFile(conversationHistory, conversationHistoryFilename, outDir)
