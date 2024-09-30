import random

class MsgCollector():
    def __init__(self):
        self.additionMsgs = []
        self.additionMsgs_colltected = []
        self.msg1 = ''
        self.msg2 = ''
        self.previousWins = 0
        self.msgCount = 0
        

    def setAdditionMsgs(self, msgs):
        self.additionMsgs.append(msgs)
    def getAdditionMsgs(self):
        return self.additionMsgs
    
    def setAdditionMsgsCollected(self, msgs):
        self.additionMsgs_colltected.append(msgs)
    def getAdditionMsgsCollected(self):
        return self.additionMsgs_colltected
    
    def setMsg1(self, msg):
        self.msg1 = msg
    def getMsg1(self):
        return self.msg1
    
    def setMsg2(self, msg):
        self.msg2 = msg
    def getMsg2(self):
        return self.msg2   

    def setPreviousWins(self, amount):
        self.previousWins = amount 
    def getPreviousWins(self):
        return self.previousWins
    
    def setMsgCount(self, count):
        self.msgCount = count
    def getMsgCount(self):
        return self.msgCount

class Config():
    def __init__(self):
        self.elizabeteLastMsg = True
        self.reaction_threshold = random.randint(10, 15)
        self.message_nr = 0
        self.echoButtons = ''
        self.echo_message_id = ''
        self.botMsg = False
        self.thread_id = ''
        self.additionMsgs = []
        self.additionMsgs_colltected = []
        self.chatChannel = 1097995867090333706 

    def setElizabeteLastMsg(self,state):
        self.elizabeteLastMsg = state
    def getElizabeteLastMsg(self):
        return self.elizabeteLastMsg     

    def setReaction_threshold(self):
        self.reaction_threshold = random.randint(10, 15)
    def getReaction_threshold(self):
        return self.reaction_threshold
    
    def setMesageNr(self, count):
        self.message_nr = count    
    def getMessageNr(self):
        return self.message_nr
    
    def setEchoButtons(self,msg):
        self.echoButtons = msg
    def getEchoButtons(self):
        return self.echoButtons

    def setEchoMessageID(self, id):
        self.echo_message_id = id
    def getEchoMessageID(self):
        return self.echo_message_id

    def setBotMsg(self, state):
        self.botMsg = state
    def getBotMsg(self):
        return self.botMsg  
    
    def setThreadID(self, id):
        self.thread_id = id
    def getThreadID(self):
        return self.thread_id
    
    def getChatChannel(self):
        return self.chatChannel