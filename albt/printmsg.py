import click


class PrintMsg(object):
    """
    Print messages
    """
    debug = True

    @staticmethod
    def creating(msg, cmd_color='green', color='white', bold=False):
        """
        Print creating
        :param cmd_color:
        :param msg:
        :param color:
        :param bold:
        :return:
        """
        PrintMsg.cmd(msg, 'CREATING', cmd_color, color, bold)

    @staticmethod
    def updating(msg, cmd_color='green', color='white', bold=False):
        """
        Print updating
        :param cmd_color:
        :param msg:
        :param color:
        :param bold:
        :return:
        """
        PrintMsg.cmd(msg, 'UPDATING', cmd_color, color, bold)

    @staticmethod
    def invoking(msg, cmd_color='blue', color='white', bold=False):
        """
        Print invoking
        :param cmd_color:
        :param msg:
        :param color:
        :param bold:
        :return:
        """
        PrintMsg.cmd(msg, 'INVOKING', cmd_color, color, bold)

    @staticmethod
    def error(msg, cmd_color='red', color='white', bold=False):
        """
        Print error
        :param msg:
        :param cmd_color:
        :param color:
        :param bold:
        :return:
        """
        PrintMsg.cmd(msg, 'ERROR', cmd_color, color, bold)

    @staticmethod
    def done(msg, cmd_color='green', color='white', bold=False):
        """
        Print done command
        :param msg:
        :param cmd_color:
        :param color:
        :param bold:
        :return:
        """
        PrintMsg.cmd(msg, 'DONE', cmd_color, color, bold)

    @staticmethod
    def out(msg, color='white', bold=False):
        """
        Print out message
        :param msg:
        :param color:
        :param bold:
        :return:
        """
        if PrintMsg.debug:
            click.echo(PrintMsg.colored_text(msg, color, bold))

    @staticmethod
    def cmd(msg, cmd, cmd_color='green', color='white', bold=False):
        """
        Print command
        :param msg:
        :param cmd:
        :param cmd_color:
        :param color:
        :param bold:
        """
        msg = "[{}] {}".format(PrintMsg.colored_text(cmd, cmd_color), msg)
        click.echo(PrintMsg.colored_text(msg, color, bold))

    @staticmethod
    def colored_text(text, color, bold=False):
        """
        Color text
        :param text:
        :param color:
        :param bold:
        :return:
        """
        return click.style(str(text), fg=color, bold=bold)

    @staticmethod
    def attr(atr, val, attr_color='green', val_color='blue'):
        """
        Print an attribute
        :param val:
        :param attr_color:
        :param atr:
        :param val_color:
        :return:
        """
        if PrintMsg.debug:
            click.echo('{}: {}'.format(
                PrintMsg.colored_text(atr, attr_color),
                PrintMsg.colored_text(val, val_color)
            ))
