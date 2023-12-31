from scheme import Scheme

#Struct for the channel
class Channel:
    def __init__(self, ChannelId):
        self.id = ChannelId
        self.scheme = Scheme(ChannelId)