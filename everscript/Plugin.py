"""Plugin abstract base class"""

class Plugin(object):

    conf = None

    @classmethod
    def set_config(cls, conf):
        """Set configuration object for all instances to use"""
        cls.conf = conf

    @classmethod
    def config(cls, section, variable, default=None):
        """Get configuration value, returning default if not set"""
        return cls.conf.get(section, variable, default) if cls.conf else None

    logger = None

    @classmethod
    def set_logger(cls, logger):
        """Set Logger object for all instances to use"""
        cls.logger = logger

    @classmethod
    def debug(cls, msg):
        """Debug message"""
        if cls.logger:
            cls.logger.debug(msg)

    @classmethod
    def info(cls, msg):
        """Informationational message"""
        if cls.logger:
            cls.logger.info(msg)

