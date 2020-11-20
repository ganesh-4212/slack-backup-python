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

parser.add_argument('-c', '--cookie', dest='cookie',required=False,
                    help='Slack user cookie')

parser.add_argument('-od', '--outDir', dest='outDir',required=False,default='./output',
                    help='Output directory to store JSON backup files.')

args = parser.parse_args()

token = args.token
auth_headers = {'Authorization': 'Bearer ' + token}
if args.cookie:
    auth_cookies = {'d': args.cookie}
else:
    auth_cookies = {}
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
                            headers=auth_headers, cookies=auth_cookies)
    print(response.json());
    return response.json()['channels']


def getChannelHistory(channelId):
    params = { 'channel': channelId, 'count': 1000}
    msgs = []
    while True:
        response = requests.get(WEB_CONSTANTS.CHANNEL_HISTORY, params=params,
                                headers=auth_headers, cookies=auth_cookies)
        rsp = response.json()
        msgs.extend(rsp['messages'])
        if not rsp['has_more']:
            break

        params['latest'] = msgs[-1]['ts']
    return msgs


def getGroups():
    response = requests.get(WEB_CONSTANTS.GROUP_LIST, headers=auth_headers, cookies=auth_cookies)
    return response.json()['groups']


def getGroupHistory(groupId):
    params = { 'channel': groupId, 'count': 1000}
    msgs = []
    while True:
        response = requests.get(WEB_CONSTANTS.GROUP_HISTORY, params=params,
                                headers=auth_headers, cookies=auth_cookies)
        rsp = response.json()
        msgs.extend(rsp['messages'])
        if not rsp['has_more']:
            break

        params['latest'] = msgs[-1]['ts']
    return msgs

def getOneToOneConversations():
    # im for one to one conv.
    response = requests.get(WEB_CONSTANTS.CONVERSATION_LIST, params={
                            'types': 'im'}, headers=auth_headers, cookies=auth_cookies)
    return response.json()['channels']


def getUsers():
    # im for one to one conv.
    response = requests.get(WEB_CONSTANTS.USERS_LIST, headers=auth_headers, cookies=auth_cookies)
    return response.json()['members']


def getConversationHistory(conversationId):
    params = { 'channel': conversationId, 'limit': 1000}
    msgs = []
    while True:
        response = requests.get(WEB_CONSTANTS.CONVERSATION_HISTORY, params=params,
                                headers=auth_headers, cookies=auth_cookies)
        rsp = response.json()
        msgs.extend(rsp['messages'])
        if not rsp['has_more']:
            break

        params['cursor'] = rsp['response_metadata']['next_cursor']
    return msgs


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
