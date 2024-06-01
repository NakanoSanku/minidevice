import time

from minidevice import config


class CommandBuilder(object):
    """Build command str for minitouch.

    You can use this, to custom actions as you wish::

        with safe_connection(_DEVICE_ID) as connection:
            builder = CommandBuilder()
            builder.down(0, 400, 400, 50)
            builder.commit()
            builder.move(0, 500, 500, 50)
            builder.commit()
            builder.move(0, 800, 400, 50)
            builder.commit()
            builder.up(0)
            builder.commit()
            builder.publish(connection)

    use `d.connection` to get `connection` from device
    """

    # TODO (x, y) can not beyond the screen size
    def __init__(self):
        self._content = ""
        self._delay = 0

    def append(self, new_content):
        self._content += new_content + "\n"

    def commit(self):
        """add minitouch command: 'c\n'"""
        self.append("c")

    def wait(self, ms):
        """add minitouch command: 'w <ms>\n'"""
        self.append("w {}".format(ms))
        self._delay += ms

    def up(self, contact_id):
        """add minitouch command: 'u <contact_id>\n'"""
        self.append("u {}".format(contact_id))

    def down(self, contact_id, x, y, pressure):
        """add minitouch command: 'd <contact_id> <x> <y> <pressure>\n'"""
        self.append("d {} {} {} {}".format(contact_id, x, y, pressure))

    def move(self, contact_id, x, y, pressure):
        """add minitouch command: 'm <contact_id> <x> <y> <pressure>\n'"""
        self.append("m {} {} {} {}".format(contact_id, x, y, pressure))

    def publish(self, connection):
        """apply current commands (_content), to your device"""
        self.commit()
        final_content = self._content
        # logger.info("send operation: {}".format(final_content.replace("\n", "\\n")))
        connection.send(final_content)
        time.sleep(self._delay / 1000 + config.DEFAULT_DELAY)
        self.reset()

    def reset(self):
        """clear current commands (_content)"""
        self._content = ""
        self._delay = 0
