import json

from ws.websocket import WebSocket


class SocketDispatcher(object):
    """
    WebSocket 连接后的对象
    """

    # 缓存列表
    # {"队伍ID-队员ID": Socket 对象}
    cache = {}

    def __getitem__(self, user):
        """
        以字典形式获取缓存对象

        :param user:         用户
        :type user:          User
        """

        try:
            return self.cache[SocketDispatcher.format_key(user)]
        except KeyError:
            return None

    def __delitem__(self, user):
        """
        删除缓存

        :param user:         用户
        :type user:          User
        """

        try:
            del self.cache[SocketDispatcher.format_key(user)]
        except KeyError:
            pass

    def set(self, user, socket):
        """
        将 Websocket 连接缓存值内存中

        :param user:         用户
        :type user:          User
        :param socket:       WebSocket 连接对象
        :type socket:        WebSocket

        """

        if self.get(user) is not None:
            self.get(user).close()

        self.cache[SocketDispatcher.format_key(user)] = socket

    def delete(self, user):
        """
        删除缓存中的连接对象

        :param user:         用户
        :type user:          User
        """

        del self[user]

    def get(self, user):
        """
        根据用户信息获取连接对象

        :param user:         用户
        :type user:          User
        """

        return self[user]

    def send_all(self, msg):
        """
        群发信息, 发给所有连接

        :param msg:     消息体
        :type msg:      str
        """
        for key in self.cache:
            self.cache[key].send(json.dumps(msg))

    def close(self, user):
        """
        段考连接

        :param user:         用户
        :type user:          User
        """

        self.get(user).close()

    @staticmethod
    def format_key(user):
        """

        :param user:         用户
        :type user:          User
        """

        return "link-{}".format(user.id)


dispatcher = SocketDispatcher()
